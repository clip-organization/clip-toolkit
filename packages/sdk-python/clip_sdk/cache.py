"""
CLIP SDK Caching Module

Provides caching functionality for CLIP objects with both memory and disk storage,
HTTP cache header support, and configurable expiration policies.
"""

import hashlib
import json
import logging
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional, Union

logger = logging.getLogger(__name__)


class CacheEntry:
    """
    Represents a single cache entry with data and expiration information.
    """

    def __init__(self, data: Dict[str, Any], expires_at: Optional[datetime] = None):
        """
        Initialize cache entry.

        Args:
            data: The cached data (CLIP object)
            expires_at: When this entry expires (None for no expiration)
        """
        self.data = data
        self.expires_at = expires_at
        self.created_at = datetime.now()
        self.accessed_at = datetime.now()
        self.access_count = 1

    def is_expired(self) -> bool:
        """
        Check if this cache entry has expired.

        Returns:
            True if expired, False otherwise
        """
        if not self.expires_at:
            return False
        return datetime.now() > self.expires_at

    def touch(self) -> None:
        """Update access time and increment access count."""
        self.accessed_at = datetime.now()
        self.access_count += 1

    def age_seconds(self) -> float:
        """Get age of entry in seconds."""
        return (datetime.now() - self.created_at).total_seconds()

    def time_to_expiry_seconds(self) -> Optional[float]:
        """Get seconds until expiry (None if no expiration)."""
        if not self.expires_at:
            return None
        return (self.expires_at - datetime.now()).total_seconds()


class CLIPCache:
    """
    Comprehensive caching system for CLIP objects with memory and disk storage.

    Features:
    - Memory and disk caching
    - HTTP cache header support
    - Configurable expiration
    - Cache statistics
    - Automatic cleanup
    """

    def __init__(
        self,
        cache_dir: Optional[str] = None,
        max_age: Optional[int] = None,
        max_memory_entries: int = 1000,
        max_disk_size_mb: int = 100,
        cleanup_interval_seconds: int = 3600,
    ):
        """
        Initialize the cache.

        Args:
            cache_dir: Directory for disk cache (None for memory-only)
            max_age: Default maximum age in seconds (None for no expiration)
            max_memory_entries: Maximum entries to keep in memory
            max_disk_size_mb: Maximum disk cache size in MB
            cleanup_interval_seconds: How often to run cleanup
        """
        self.memory_cache: Dict[str, CacheEntry] = {}
        self.cache_dir = cache_dir
        self.max_age = max_age
        self.max_memory_entries = max_memory_entries
        self.max_disk_size_mb = max_disk_size_mb
        self.cleanup_interval_seconds = cleanup_interval_seconds

        # Statistics
        self.stats = {
            "hits": 0,
            "misses": 0,
            "memory_hits": 0,
            "disk_hits": 0,
            "evictions": 0,
            "errors": 0,
        }

        self.last_cleanup = datetime.now()

        # Create cache directory if specified
        if cache_dir:
            try:
                os.makedirs(cache_dir, exist_ok=True)
                logger.info(f"Cache directory created/verified: {cache_dir}")
            except OSError as e:
                logger.warning(f"Failed to create cache directory {cache_dir}: {e}")
                self.cache_dir = None

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get item from cache (memory first, then disk).

        Args:
            key: Cache key (typically URL)

        Returns:
            Cached data if found and not expired, None otherwise
        """
        # Periodic cleanup
        if self._should_cleanup():
            self._cleanup()

        # Check memory cache first
        if key in self.memory_cache:
            entry = self.memory_cache[key]
            if not entry.is_expired():
                entry.touch()
                self.stats["hits"] += 1
                self.stats["memory_hits"] += 1
                logger.debug(f"Cache hit (memory): {key}")
                return entry.data
            else:
                # Remove expired entry
                del self.memory_cache[key]
                logger.debug(f"Expired entry removed from memory: {key}")

        # Check disk cache if enabled
        if self.cache_dir:
            cache_file = self._get_cache_file_path(key)
            if cache_file.exists():
                try:
                    with open(cache_file, "r", encoding="utf-8") as f:
                        cache_data = json.load(f)

                    # Check expiration
                    expires_at = cache_data.get("expires_at")
                    if expires_at:
                        expires_at = datetime.fromisoformat(expires_at)
                        if datetime.now() > expires_at:
                            # Remove expired file
                            cache_file.unlink()
                            logger.debug(f"Expired entry removed from disk: {key}")
                            self.stats["misses"] += 1
                            return None

                    # Add to memory cache for faster access
                    entry = CacheEntry(cache_data["data"], expires_at)
                    entry.access_count = cache_data.get("access_count", 1)

                    # Only add to memory if we have space
                    if len(self.memory_cache) < self.max_memory_entries:
                        self.memory_cache[key] = entry

                    self.stats["hits"] += 1
                    self.stats["disk_hits"] += 1
                    logger.debug(f"Cache hit (disk): {key}")
                    return entry.data

                except (json.JSONDecodeError, KeyError, OSError, ValueError) as e:
                    logger.warning(f"Failed to read cache file {cache_file}: {e}")
                    # Remove invalid cache file
                    try:
                        cache_file.unlink()
                    except OSError:
                        pass
                    self.stats["errors"] += 1

        self.stats["misses"] += 1
        logger.debug(f"Cache miss: {key}")
        return None

    def set(
        self,
        key: str,
        data: Dict[str, Any],
        max_age: Optional[int] = None,
        from_http_headers: Optional[Dict[str, str]] = None,
    ) -> None:
        """
        Store item in cache.

        Args:
            key: Cache key (typically URL)
            data: Data to cache
            max_age: Maximum age in seconds (overrides default)
            from_http_headers: HTTP response headers for cache control
        """
        # Determine expiration time
        expires_at = None
        cache_max_age = self._determine_max_age(max_age, from_http_headers)

        # Don't cache if max_age is 0 (no-cache directive)
        if cache_max_age == 0:
            logger.debug(f"Skipping cache for {key} due to no-cache directive")
            return

        if cache_max_age is not None:
            expires_at = datetime.now() + timedelta(seconds=cache_max_age)

        # Create cache entry
        entry = CacheEntry(data, expires_at)

        # Store in memory (with LRU eviction if needed)
        # Only evict if we're adding a new key and at capacity
        if (
            key not in self.memory_cache
            and len(self.memory_cache) >= self.max_memory_entries
        ):
            self._evict_lru_memory()

        self.memory_cache[key] = entry

        # Store on disk if enabled
        if self.cache_dir:
            self._store_to_disk(key, entry)

        logger.debug(f"Cached: {key} (expires: {expires_at})")

    def clear(self, pattern: Optional[str] = None) -> int:
        """
        Clear cache entries.

        Args:
            pattern: Optional pattern to match keys (None clears all)

        Returns:
            Number of entries cleared
        """
        cleared = 0

        # Clear memory cache
        if pattern:
            to_remove = [k for k in self.memory_cache.keys() if pattern in k]
            for key in to_remove:
                del self.memory_cache[key]
                cleared += 1
        else:
            cleared += len(self.memory_cache)
            self.memory_cache.clear()

        # Clear disk cache
        if self.cache_dir and Path(self.cache_dir).exists():
            for cache_file in Path(self.cache_dir).glob("*.json"):
                if pattern:
                    # Read file to check if key matches pattern
                    try:
                        with open(cache_file, "r") as f:
                            cache_data = json.load(f)
                        original_key = cache_data.get("original_key", "")
                        if pattern not in original_key:
                            continue
                    except:
                        pass

                try:
                    cache_file.unlink()
                    cleared += 1
                except OSError:
                    pass

        logger.info(
            f"Cleared {cleared} cache entries"
            + (f" matching '{pattern}'" if pattern else "")
        )
        return cleared

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        total_requests = self.stats["hits"] + self.stats["misses"]
        hit_rate = self.stats["hits"] / total_requests if total_requests > 0 else 0

        disk_size_mb = 0
        if self.cache_dir and Path(self.cache_dir).exists():
            disk_size_mb = sum(
                f.stat().st_size for f in Path(self.cache_dir).glob("*.json")
            ) / (1024 * 1024)

        return {
            "total_requests": total_requests,
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "hit_rate": hit_rate,
            "memory_hits": self.stats["memory_hits"],
            "disk_hits": self.stats["disk_hits"],
            "memory_entries": len(self.memory_cache),
            "disk_size_mb": round(disk_size_mb, 2),
            "evictions": self.stats["evictions"],
            "errors": self.stats["errors"],
        }

    def _determine_max_age(
        self, max_age: Optional[int], http_headers: Optional[Dict[str, str]]
    ) -> Optional[int]:
        """Determine max age from various sources."""
        # Explicit max_age takes precedence
        if max_age is not None:
            return max_age

        # Parse HTTP cache headers
        if http_headers:
            cache_control = http_headers.get("Cache-Control", "").lower()

            # Check for no-cache or no-store
            if "no-cache" in cache_control or "no-store" in cache_control:
                return 0  # Don't cache

            # Extract max-age
            if "max-age=" in cache_control:
                try:
                    max_age_match = (
                        cache_control.split("max-age=")[1].split(",")[0].strip()
                    )
                    return int(max_age_match)
                except (ValueError, IndexError):
                    pass

            # Check Expires header
            expires_header = http_headers.get("Expires")
            if expires_header:
                try:
                    from email.utils import parsedate_to_datetime

                    expires_time = parsedate_to_datetime(expires_header)
                    age_seconds = (expires_time - datetime.now()).total_seconds()
                    return max(0, int(age_seconds))
                except:
                    pass

        # Use default max_age
        return self.max_age

    def _get_cache_file_path(self, key: str) -> Path:
        """Get cache file path for a key."""
        filename = self._key_to_filename(key)
        return Path(self.cache_dir) / filename

    def _key_to_filename(self, key: str) -> str:
        """Convert cache key to safe filename."""
        return hashlib.md5(key.encode()).hexdigest() + ".json"

    def _store_to_disk(self, key: str, entry: CacheEntry) -> None:
        """Store cache entry to disk."""
        if not self.cache_dir:
            return

        cache_file = self._get_cache_file_path(key)

        try:
            cache_data = {
                "data": entry.data,
                "expires_at": entry.expires_at.isoformat()
                if entry.expires_at
                else None,
                "created_at": entry.created_at.isoformat(),
                "access_count": entry.access_count,
                "original_key": key,  # Store original key for pattern matching
            }

            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(cache_data, f, separators=(",", ":"))

            # Check disk size limits
            self._enforce_disk_size_limit()

        except OSError as e:
            logger.warning(f"Failed to write cache file {cache_file}: {e}")
            self.stats["errors"] += 1

    def _evict_lru_memory(self) -> None:
        """Evict least recently used entry from memory."""
        if not self.memory_cache:
            return

        # Find LRU entry
        lru_key = min(
            self.memory_cache.keys(), key=lambda k: self.memory_cache[k].accessed_at
        )

        del self.memory_cache[lru_key]
        self.stats["evictions"] += 1
        logger.debug(f"Evicted LRU entry: {lru_key}")

    def _enforce_disk_size_limit(self) -> None:
        """Remove old files if disk cache exceeds size limit."""
        if not self.cache_dir:
            return

        cache_dir = Path(self.cache_dir)
        if not cache_dir.exists():
            return

        # Get all cache files with sizes and modification times
        cache_files = []
        total_size = 0

        for cache_file in cache_dir.glob("*.json"):
            try:
                stat = cache_file.stat()
                cache_files.append((cache_file, stat.st_size, stat.st_mtime))
                total_size += stat.st_size
            except OSError:
                pass

        max_size_bytes = self.max_disk_size_mb * 1024 * 1024

        if total_size > max_size_bytes:
            # Sort by modification time (oldest first)
            cache_files.sort(key=lambda x: x[2])

            # Remove oldest files until under limit
            for cache_file, size, _ in cache_files:
                if total_size <= max_size_bytes:
                    break

                try:
                    cache_file.unlink()
                    total_size -= size
                    logger.debug(f"Removed old cache file: {cache_file}")
                except OSError:
                    pass

    def _should_cleanup(self) -> bool:
        """Check if it's time for periodic cleanup."""
        return (
            datetime.now() - self.last_cleanup
        ).total_seconds() > self.cleanup_interval_seconds

    def _cleanup(self) -> None:
        """Perform periodic cleanup of expired entries."""
        self.last_cleanup = datetime.now()

        # Clean memory cache
        expired_keys = [
            key for key, entry in self.memory_cache.items() if entry.is_expired()
        ]

        for key in expired_keys:
            del self.memory_cache[key]

        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired memory entries")

        # Clean disk cache
        if self.cache_dir:
            cleaned_disk = 0
            cache_dir = Path(self.cache_dir)

            for cache_file in cache_dir.glob("*.json"):
                try:
                    with open(cache_file, "r") as f:
                        cache_data = json.load(f)

                    expires_at = cache_data.get("expires_at")
                    if expires_at:
                        expires_at = datetime.fromisoformat(expires_at)
                        if datetime.now() > expires_at:
                            cache_file.unlink()
                            cleaned_disk += 1

                except (json.JSONDecodeError, KeyError, OSError, ValueError):
                    # Remove invalid files
                    try:
                        cache_file.unlink()
                        cleaned_disk += 1
                    except OSError:
                        pass

            if cleaned_disk:
                logger.debug(f"Cleaned up {cleaned_disk} expired/invalid disk entries")


def get_default_cache_dir() -> str:
    """Get the default cache directory for the CLIP SDK."""
    home_dir = Path.home()
    return str(home_dir / ".clip-sdk" / "cache")


# Export for convenience
__all__ = ["CLIPCache", "CacheEntry", "get_default_cache_dir"]
