"""
Tests for CLIP SDK caching functionality.
"""

import json
import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

import pytest

from clip_sdk.cache import CacheEntry, CLIPCache, get_default_cache_dir


class TestCacheEntry:
    """Test CacheEntry class."""

    def test_cache_entry_creation(self):
        """Test basic cache entry creation."""
        data = {"test": "data"}
        entry = CacheEntry(data)

        assert entry.data == data
        assert entry.expires_at is None
        assert entry.access_count == 1
        assert isinstance(entry.created_at, datetime)
        assert isinstance(entry.accessed_at, datetime)

    def test_cache_entry_with_expiration(self):
        """Test cache entry with expiration."""
        data = {"test": "data"}
        expires_at = datetime.now() + timedelta(hours=1)
        entry = CacheEntry(data, expires_at)

        assert entry.expires_at == expires_at
        assert not entry.is_expired()

    def test_cache_entry_expiration(self):
        """Test cache entry expiration."""
        data = {"test": "data"}
        expires_at = datetime.now() - timedelta(seconds=1)
        entry = CacheEntry(data, expires_at)

        assert entry.is_expired()

    def test_cache_entry_touch(self):
        """Test updating access time."""
        entry = CacheEntry({"test": "data"})
        original_accessed = entry.accessed_at
        original_count = entry.access_count

        time.sleep(0.01)  # Small delay
        entry.touch()

        assert entry.accessed_at > original_accessed
        assert entry.access_count == original_count + 1

    def test_cache_entry_age(self):
        """Test age calculation."""
        entry = CacheEntry({"test": "data"})
        time.sleep(0.01)

        age = entry.age_seconds()
        assert age > 0
        assert age < 1  # Should be very small

    def test_time_to_expiry(self):
        """Test time to expiry calculation."""
        # No expiration
        entry = CacheEntry({"test": "data"})
        assert entry.time_to_expiry_seconds() is None

        # With expiration
        expires_at = datetime.now() + timedelta(seconds=10)
        entry = CacheEntry({"test": "data"}, expires_at)

        ttl = entry.time_to_expiry_seconds()
        assert ttl is not None
        assert 9 < ttl <= 10


class TestCLIPCache:
    """Test CLIPCache class."""

    def test_memory_only_cache(self):
        """Test memory-only cache."""
        cache = CLIPCache(cache_dir=None, max_age=None)

        # Test set and get
        data = {"test": "data"}
        cache.set("key1", data)

        retrieved = cache.get("key1")
        assert retrieved == data

        # Test miss
        assert cache.get("nonexistent") is None

    def test_cache_with_disk(self):
        """Test cache with disk storage."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = CLIPCache(cache_dir=temp_dir, max_age=None)

            # Test set and get
            data = {"test": "data", "complex": {"nested": True}}
            cache.set("key1", data)

            # Should hit memory first
            retrieved = cache.get("key1")
            assert retrieved == data

            # Clear memory cache and test disk retrieval
            cache.memory_cache.clear()
            retrieved = cache.get("key1")
            assert retrieved == data

    def test_cache_expiration(self):
        """Test cache expiration."""
        cache = CLIPCache(cache_dir=None, max_age=1)  # 1 second

        data = {"test": "data"}
        cache.set("key1", data)

        # Should be available immediately
        assert cache.get("key1") == data

        # Wait for expiration
        time.sleep(1.1)
        assert cache.get("key1") is None

    def test_http_cache_headers(self):
        """Test HTTP cache header processing."""
        cache = CLIPCache(cache_dir=None)

        # Test max-age header
        headers = {"Cache-Control": "max-age=60"}
        data = {"test": "data"}
        cache.set("key1", data, from_http_headers=headers)

        # Should be cached
        assert cache.get("key1") == data

        # Test no-cache header
        headers = {"Cache-Control": "no-cache"}
        cache.set("key2", data, from_http_headers=headers)

        # Should not be cached (expires immediately)
        time.sleep(0.01)
        assert cache.get("key2") is None

    def test_lru_eviction(self):
        """Test LRU eviction."""
        cache = CLIPCache(cache_dir=None, max_memory_entries=2)

        # Add entries up to limit
        cache.set("key1", {"data": 1})
        time.sleep(0.01)  # Ensure different timestamps
        cache.set("key2", {"data": 2})

        time.sleep(0.01)  # Ensure different timestamps
        # Access key1 to make it more recently used
        cache.get("key1")

        time.sleep(0.01)  # Ensure different timestamps
        # Add another entry, should evict key2
        cache.set("key3", {"data": 3})

        assert cache.get("key1") is not None  # Should still be there
        assert cache.get("key2") is None  # Should be evicted
        assert cache.get("key3") is not None  # Should be there

    def test_cache_clear(self):
        """Test cache clearing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = CLIPCache(cache_dir=temp_dir)

            # Add some entries
            cache.set("key1", {"data": 1})
            cache.set("key2", {"data": 2})
            cache.set("test_key", {"data": 3})

            # Clear specific pattern
            cleared = cache.clear("test_")
            assert cleared >= 1

            # test_key should be gone
            assert cache.get("test_key") is None
            # Others should remain
            assert cache.get("key1") is not None

            # Clear all
            cleared = cache.clear()
            assert cleared >= 2
            assert cache.get("key1") is None
            assert cache.get("key2") is None

    def test_cache_stats(self):
        """Test cache statistics."""
        cache = CLIPCache(cache_dir=None)

        # Initially no stats
        stats = cache.get_stats()
        assert stats["total_requests"] == 0
        assert stats["hits"] == 0
        assert stats["misses"] == 0
        assert stats["hit_rate"] == 0

        # Add some activity
        cache.set("key1", {"data": 1})
        cache.get("key1")  # Hit
        cache.get("key2")  # Miss

        stats = cache.get_stats()
        assert stats["total_requests"] == 2
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["hit_rate"] == 0.5

    def test_disk_size_limit(self):
        """Test disk size limits."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Very small disk limit
            cache = CLIPCache(cache_dir=temp_dir, max_disk_size_mb=0.001)

            # Add several entries to exceed limit
            for i in range(10):
                large_data = {"data": "x" * 1000, "index": i}
                cache.set(f"key{i}", large_data)

            # Should have removed some files
            cache_files = list(Path(temp_dir).glob("*.json"))
            assert len(cache_files) < 10

    def test_periodic_cleanup(self):
        """Test periodic cleanup of expired entries."""
        cache = CLIPCache(cache_dir=None, cleanup_interval_seconds=0.1)

        # Add expired entry
        cache.set("key1", {"data": 1}, max_age=0.05)  # Very short expiration

        # Wait and trigger cleanup
        time.sleep(0.2)
        cache.get("key2")  # This should trigger cleanup

        # Expired entry should be gone
        assert cache.get("key1") is None

    def test_expires_header_parsing(self):
        """Test Expires header parsing."""
        cache = CLIPCache(cache_dir=None)

        # Mock current time for predictable testing
        future_time = datetime.now() + timedelta(seconds=60)
        expires_str = future_time.strftime("%a, %d %b %Y %H:%M:%S GMT")

        headers = {"Expires": expires_str}

        with patch("clip_sdk.cache.datetime") as mock_datetime:
            mock_datetime.now.return_value = datetime.now()
            mock_datetime.fromisoformat = datetime.fromisoformat

            cache.set("key1", {"data": 1}, from_http_headers=headers)

            # Should be cached
            assert cache.get("key1") is not None


def test_get_default_cache_dir():
    """Test default cache directory function."""
    cache_dir = get_default_cache_dir()

    assert isinstance(cache_dir, str)
    assert ".clip-sdk" in cache_dir
    assert "cache" in cache_dir

    # Should be absolute path
    assert Path(cache_dir).is_absolute()


class TestCacheIntegration:
    """Integration tests for caching."""

    def test_cache_persistence_across_instances(self):
        """Test that cache persists across different cache instances."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # First cache instance
            cache1 = CLIPCache(cache_dir=temp_dir)
            cache1.set("persistent_key", {"data": "persistent"})

            # Second cache instance (same directory)
            cache2 = CLIPCache(cache_dir=temp_dir)

            # Should be able to retrieve from disk
            retrieved = cache2.get("persistent_key")
            assert retrieved == {"data": "persistent"}

    def test_cache_with_invalid_json_files(self):
        """Test cache handling of invalid JSON files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = CLIPCache(cache_dir=temp_dir)

            # Create invalid cache file
            invalid_file = Path(temp_dir) / "invalid.json"
            invalid_file.write_text("invalid json content")

            # Should handle gracefully
            assert cache.get("any_key") is None

            # Invalid file should be cleaned up
            cache._cleanup()
            assert not invalid_file.exists()

    def test_cache_concurrent_access(self):
        """Test cache behavior with concurrent access patterns."""
        cache = CLIPCache(cache_dir=None, max_memory_entries=5)

        # Simulate concurrent access
        keys = [f"key{i}" for i in range(10)]

        # Add all keys
        for key in keys:
            cache.set(key, {"data": key})

        # Some should be evicted due to size limit
        assert len(cache.memory_cache) <= 5

        # Access patterns should affect LRU
        for key in keys[:3]:
            cache.get(key)

        # Add more entries
        for i in range(3):
            cache.set(f"new_key{i}", {"data": f"new{i}"})

        # Should still respect memory limits
        assert len(cache.memory_cache) <= 5


if __name__ == "__main__":
    pytest.main([__file__])
