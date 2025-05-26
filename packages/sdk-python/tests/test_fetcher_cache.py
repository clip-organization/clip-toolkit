"""
Tests for CLIPFetcher caching functionality.
"""

import json
import tempfile
import time
from unittest.mock import MagicMock, Mock, patch

import pytest
import requests

from clip_sdk import CLIPCache, CLIPFetcher, CLIPFetchError


class TestCLIPFetcherCaching:
    """Test CLIPFetcher with caching enabled."""

    def setup_method(self):
        """Set up test fixtures."""
        self.sample_clip = {
            "@context": "https://clipprotocol.org/context/v1",
            "type": "Venue",
            "id": "clip:test:venue:sample",
            "name": "Test Venue",
            "description": "A test venue",
        }

    def test_fetcher_with_default_cache(self):
        """Test fetcher with default cache configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create custom cache in temp directory
            cache = CLIPCache(cache_dir=temp_dir, max_age=3600)
            fetcher = CLIPFetcher(cache=cache)

            assert fetcher.cache_enabled is True
            assert fetcher.cache is not None
            assert isinstance(fetcher.cache, CLIPCache)

    def test_fetcher_cache_disabled(self):
        """Test fetcher with caching disabled."""
        fetcher = CLIPFetcher(cache_enabled=False)

        assert fetcher.cache_enabled is False
        assert fetcher.cache is None

    @patch("requests.get")
    def test_fetch_from_url_with_caching(self, mock_get):
        """Test URL fetching with caching."""
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = self.sample_clip
        mock_response.headers = {"Cache-Control": "max-age=3600"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        with tempfile.TemporaryDirectory() as temp_dir:
            cache = CLIPCache(cache_dir=temp_dir)
            fetcher = CLIPFetcher(cache=cache)

            url = "https://example.com/clip.json"

            # First fetch - should hit the network
            result1 = fetcher.fetch_from_url(url)
            assert result1 == self.sample_clip
            assert mock_get.call_count == 1

            # Second fetch - should hit cache
            result2 = fetcher.fetch_from_url(url)
            assert result2 == self.sample_clip
            assert mock_get.call_count == 1  # Should not increase

    @patch("requests.get")
    def test_fetch_cache_miss_then_hit(self, mock_get):
        """Test cache miss followed by cache hit."""
        mock_response = Mock()
        mock_response.json.return_value = self.sample_clip
        mock_response.headers = {}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        cache = CLIPCache(cache_dir=None)  # Memory only
        fetcher = CLIPFetcher(cache=cache)

        url = "https://example.com/clip.json"

        # Verify cache is empty
        stats = fetcher.get_cache_stats()
        assert stats["hits"] == 0
        assert stats["misses"] == 0

        # First fetch
        result = fetcher.fetch_from_url(url)
        assert result == self.sample_clip

        # Should have 1 miss (no cache hit)
        stats = fetcher.get_cache_stats()
        assert stats["misses"] == 1

        # Second fetch should hit cache
        result = fetcher.fetch_from_url(url)
        assert result == self.sample_clip

        # Should have 1 hit
        stats = fetcher.get_cache_stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 1

    @patch("requests.get")
    def test_fetch_with_cache_disabled_parameter(self, mock_get):
        """Test fetch with cache disabled via parameter."""
        mock_response = Mock()
        mock_response.json.return_value = self.sample_clip
        mock_response.headers = {}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        cache = CLIPCache(cache_dir=None)
        fetcher = CLIPFetcher(cache=cache)

        url = "https://example.com/clip.json"

        # First fetch with caching disabled
        result1 = fetcher.fetch_from_url(url, use_cache=False)
        assert result1 == self.sample_clip

        # Second fetch with caching disabled
        result2 = fetcher.fetch_from_url(url, use_cache=False)
        assert result2 == self.sample_clip

        # Should have hit network twice
        assert mock_get.call_count == 2

        # Cache should show no activity
        stats = fetcher.get_cache_stats()
        assert stats["hits"] == 0
        assert stats["misses"] == 0

    @patch("requests.get")
    def test_fetch_with_validation_disabled(self, mock_get):
        """Test fetch with validation disabled."""
        # Invalid CLIP object (missing required fields)
        invalid_clip = {"name": "Invalid CLIP"}

        mock_response = Mock()
        mock_response.json.return_value = invalid_clip
        mock_response.headers = {}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        cache = CLIPCache(cache_dir=None)
        fetcher = CLIPFetcher(cache=cache)

        url = "https://example.com/invalid-clip.json"

        # Should fail with validation enabled (default)
        with pytest.raises(CLIPFetchError):
            fetcher.fetch_from_url(url)

        # Should succeed with validation disabled
        result = fetcher.fetch_from_url(url, validate=False)
        assert result == invalid_clip

    @patch("requests.get")
    def test_cache_http_headers_max_age(self, mock_get):
        """Test caching with HTTP max-age header."""
        mock_response = Mock()
        mock_response.json.return_value = self.sample_clip
        mock_response.headers = {"Cache-Control": "max-age=1"}  # 1 second
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        cache = CLIPCache(cache_dir=None)
        fetcher = CLIPFetcher(cache=cache)

        url = "https://example.com/clip.json"

        # First fetch
        result1 = fetcher.fetch_from_url(url)
        assert result1 == self.sample_clip

        # Immediate second fetch should hit cache
        result2 = fetcher.fetch_from_url(url)
        assert result2 == self.sample_clip
        assert mock_get.call_count == 1

        # Wait for expiration
        time.sleep(1.1)

        # Third fetch should miss cache and hit network
        result3 = fetcher.fetch_from_url(url)
        assert result3 == self.sample_clip
        assert mock_get.call_count == 2

    @patch("requests.get")
    def test_cache_no_cache_header(self, mock_get):
        """Test caching with no-cache header."""
        mock_response = Mock()
        mock_response.json.return_value = self.sample_clip
        mock_response.headers = {"Cache-Control": "no-cache"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        cache = CLIPCache(cache_dir=None)
        fetcher = CLIPFetcher(cache=cache)

        url = "https://example.com/clip.json"

        # Multiple fetches should all hit network
        fetcher.fetch_from_url(url)
        fetcher.fetch_from_url(url)

        assert mock_get.call_count == 2

    def test_cache_management_methods(self):
        """Test cache management methods."""
        cache = CLIPCache(cache_dir=None)
        fetcher = CLIPFetcher(cache=cache)

        # Add some test data to cache
        cache.set("test_key", {"data": "test"})
        cache.set("another_key", {"data": "another"})

        # Test get_cache_stats
        stats = fetcher.get_cache_stats()
        assert isinstance(stats, dict)
        assert "hits" in stats
        assert "misses" in stats

        # Test clear_cache
        cleared = fetcher.clear_cache()
        assert cleared >= 2

        # Cache should be empty
        assert cache.get("test_key") is None
        assert cache.get("another_key") is None

    def test_cache_management_with_disabled_cache(self):
        """Test cache management when cache is disabled."""
        fetcher = CLIPFetcher(cache_enabled=False)

        # Should return None for stats
        stats = fetcher.get_cache_stats()
        assert stats is None

        # Should return 0 for clear
        cleared = fetcher.clear_cache()
        assert cleared == 0

    def test_set_cache_max_age(self):
        """Test setting cache max age."""
        cache = CLIPCache(cache_dir=None, max_age=3600)
        fetcher = CLIPFetcher(cache=cache)

        # Change max age
        fetcher.set_cache_max_age(1800)
        assert cache.max_age == 1800

        # Set to None (no expiration)
        fetcher.set_cache_max_age(None)
        assert cache.max_age is None

    @patch("requests.get")
    def test_prefetch_urls(self, mock_get):
        """Test URL prefetching functionality."""
        mock_response = Mock()
        mock_response.json.return_value = self.sample_clip
        mock_response.headers = {}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        cache = CLIPCache(cache_dir=None)
        fetcher = CLIPFetcher(cache=cache)

        urls = [
            "https://example.com/clip1.json",
            "https://example.com/clip2.json",
            "https://example.com/clip3.json",
        ]

        # Prefetch URLs
        results = fetcher.prefetch_urls(urls)

        # Should have fetched all URLs
        assert len(results["successful"]) == 3
        assert len(results["failed"]) == 0
        assert len(results["cached"]) == 0
        assert results["total_time"] >= 0  # Can be 0 for mocked responses

        # All should be cached now
        for url in urls:
            assert cache.get(url) is not None

        # Prefetch again - should all be cached
        results2 = fetcher.prefetch_urls(urls)
        assert len(results2["cached"]) == 3
        assert len(results2["successful"]) == 0

    @patch("requests.get")
    def test_prefetch_with_failures(self, mock_get):
        """Test prefetching with some failures."""

        def side_effect(url, **kwargs):
            if "fail" in url:
                raise requests.RequestException("Network error")

            mock_response = Mock()
            mock_response.json.return_value = self.sample_clip
            mock_response.headers = {}
            mock_response.raise_for_status.return_value = None
            return mock_response

        mock_get.side_effect = side_effect

        cache = CLIPCache(cache_dir=None)
        fetcher = CLIPFetcher(cache=cache)

        urls = [
            "https://example.com/clip1.json",
            "https://example.com/fail-clip.json",
            "https://example.com/clip3.json",
        ]

        results = fetcher.prefetch_urls(urls)

        assert len(results["successful"]) == 2
        assert len(results["failed"]) == 1
        assert "fail-clip" in results["failed"][0]["url"]

    def test_fetch_file_caching_not_applicable(self):
        """Test that file fetching doesn't use caching."""
        cache = CLIPCache(cache_dir=None)
        fetcher = CLIPFetcher(cache=cache)

        # Create a temporary CLIP file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(self.sample_clip, f)
            temp_file = f.name

        try:
            # Fetch file multiple times
            result1 = fetcher.fetch_from_file(temp_file)
            result2 = fetcher.fetch_from_file(temp_file)

            assert result1 == self.sample_clip
            assert result2 == self.sample_clip

            # Cache stats should show no activity (files aren't cached)
            stats = fetcher.get_cache_stats()
            assert stats["hits"] == 0
            assert stats["misses"] == 0

        finally:
            # Clean up
            import os

            os.unlink(temp_file)

    @patch("requests.get")
    def test_fetch_multiple_with_caching(self, mock_get):
        """Test fetch_multiple with caching."""
        mock_response = Mock()
        mock_response.json.return_value = self.sample_clip
        mock_response.headers = {}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        cache = CLIPCache(cache_dir=None)
        fetcher = CLIPFetcher(cache=cache)

        urls = ["https://example.com/clip1.json", "https://example.com/clip2.json"]

        # First fetch_multiple call
        results1 = fetcher.fetch_multiple(urls)
        assert len(results1) == 2
        assert mock_get.call_count == 2

        # Second fetch_multiple call - should hit cache
        results2 = fetcher.fetch_multiple(urls)
        assert len(results2) == 2
        assert mock_get.call_count == 2  # Should not increase

        # Verify cache stats
        stats = fetcher.get_cache_stats()
        assert stats["hits"] == 2  # Second call should hit cache twice
        assert stats["misses"] == 2  # First call should miss twice


class TestCachePerformance:
    """Test caching performance benefits."""

    @patch("requests.get")
    def test_cache_performance_improvement(self, mock_get):
        """Test that caching improves performance."""

        # Mock slow response
        def slow_response(*args, **kwargs):
            time.sleep(0.1)  # Simulate network delay
            mock_response = Mock()
            mock_response.json.return_value = {
                "@context": "https://clipprotocol.org/context/v1",
                "type": "Venue",
                "id": "clip:test:venue:perf",
                "name": "Performance Test Venue",
            }
            mock_response.headers = {}
            mock_response.raise_for_status.return_value = None
            return mock_response

        mock_get.side_effect = slow_response

        cache = CLIPCache(cache_dir=None)
        fetcher = CLIPFetcher(cache=cache)

        url = "https://example.com/slow-clip.json"

        # First fetch - should be slow
        start_time = time.time()
        result1 = fetcher.fetch_from_url(url)
        first_time = time.time() - start_time

        # Second fetch - should be fast (cached)
        start_time = time.time()
        result2 = fetcher.fetch_from_url(url)
        second_time = time.time() - start_time

        # Results should be identical
        assert result1 == result2

        # Second fetch should be significantly faster
        assert second_time < first_time / 2

        # Should have hit network only once
        assert mock_get.call_count == 1


if __name__ == "__main__":
    pytest.main([__file__])
