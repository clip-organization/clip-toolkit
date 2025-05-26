"""
Asynchronous CLIP object fetching with aiohttp.
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlparse

import aiohttp

from .cache import CLIPCache, get_default_cache_dir
from .utils import load_json_from_path

logger = logging.getLogger(__name__)


class AsyncCLIPFetchError(Exception):
    """Custom exception for async CLIP fetching errors."""

    pass


class AsyncCLIPFetcher:
    """
    Async fetcher for CLIP objects from various sources with advanced caching.

    Features:
    - Async fetch from URLs (HTTP/HTTPS) and local files
    - Advanced caching (memory + disk) with HTTP header support
    - Timeout and retry handling
    - Cache statistics and management
    - Support for batch operations
    - Configurable cache policies
    """

    def __init__(
        self,
        timeout: float = 30.0,
        max_retries: int = 3,
        cache: Optional[CLIPCache] = None,
        cache_enabled: bool = True,
        cache_max_age: int = 3600,
        user_agent: str = "CLIP-SDK-Python-Async/0.1.0",
    ):
        """
        Initialize the async CLIP fetcher with advanced caching.

        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            cache: Custom CLIPCache instance (None for default)
            cache_enabled: Whether to enable caching
            cache_max_age: Default cache max age in seconds
            user_agent: User agent string for HTTP requests
        """
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.max_retries = max_retries
        self.cache_enabled = cache_enabled
        self.user_agent = user_agent

        # Initialize cache
        if cache_enabled:
            if cache is None:
                # Create default cache
                self.cache = CLIPCache(
                    cache_dir=get_default_cache_dir(),
                    max_age=cache_max_age,
                    max_memory_entries=1000,
                    max_disk_size_mb=100,
                )
            else:
                self.cache = cache
        else:
            self.cache = None

        # Failed sources tracking
        self._failed_sources: List[Dict[str, str]] = []

    async def fetch(
        self, source: str, use_cache: bool = True, validate: bool = True
    ) -> Dict[str, Any]:
        """
        Asynchronously fetch a CLIP object from a source (URL or file path).

        Args:
            source: URL or file path to fetch from
            use_cache: Whether to use caching for this request
            validate: Whether to validate basic CLIP structure

        Returns:
            The fetched CLIP object

        Raises:
            AsyncCLIPFetchError: If fetching fails
        """
        if self._is_url(source):
            return await self.fetch_from_url(
                source, use_cache=use_cache, validate=validate
            )
        else:
            return await self.fetch_from_file(source, validate=validate)

    async def fetch_from_url(
        self, url: str, use_cache: bool = True, validate: bool = True
    ) -> Dict[str, Any]:
        """
        Asynchronously fetch a CLIP object from a URL with advanced caching.

        Args:
            url: URL to fetch from
            use_cache: Whether to use caching for this request
            validate: Whether to validate basic CLIP structure

        Returns:
            The fetched CLIP object

        Raises:
            AsyncCLIPFetchError: If fetching fails
        """
        # Check cache first if enabled
        if self.cache_enabled and use_cache and self.cache:
            cached_object = self.cache.get(url)
            if cached_object is not None:
                if not validate or self._is_valid_clip_structure(cached_object):
                    logger.debug(f"Cache hit for URL: {url}")
                    return cached_object
                else:
                    logger.warning(
                        f"Cached object for {url} failed validation, refetching"
                    )

        # Fetch from URL with retries
        last_exception = None
        for attempt in range(self.max_retries):
            try:
                headers = {"Accept": "application/json", "User-Agent": self.user_agent}

                async with aiohttp.ClientSession(timeout=self.timeout) as session:
                    async with session.get(url, headers=headers) as response:
                        response.raise_for_status()

                        # Parse JSON
                        clip_object = await response.json()

                        # Validate basic CLIP structure if requested
                        if validate:
                            self._validate_basic_structure(clip_object, url)

                        # Cache if enabled
                        if self.cache_enabled and use_cache and self.cache:
                            # Extract cache headers
                            http_headers = dict(response.headers)
                            self.cache.set(
                                url, clip_object, from_http_headers=http_headers
                            )

                        logger.info(f"Successfully fetched CLIP object from: {url}")
                        return clip_object

            except (aiohttp.ClientError, json.JSONDecodeError, ValueError) as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    try:
                        error_msg = str(e)
                    except Exception:
                        error_msg = repr(e)
                    logger.warning(
                        f"Attempt {attempt + 1} failed for {url}: "
                        f"{error_msg}. Retrying..."
                    )
                    await asyncio.sleep(1)  # Brief delay before retry
                else:
                    logger.error(f"All {self.max_retries} attempts failed for {url}")

        try:
            error_msg = str(last_exception)
        except Exception:
            error_msg = repr(last_exception)
        raise AsyncCLIPFetchError(
            f"Failed to fetch CLIP object from {url}: {error_msg}"
        )

    async def fetch_from_file(
        self, file_path: str, validate: bool = True
    ) -> Dict[str, Any]:
        """
        Asynchronously fetch a CLIP object from a local file.

        Args:
            file_path: Path to the file
            validate: Whether to validate basic CLIP structure

        Returns:
            The fetched CLIP object

        Raises:
            AsyncCLIPFetchError: If fetching fails
        """
        try:
            # Run file I/O in executor to avoid blocking
            loop = asyncio.get_event_loop()
            clip_object = await loop.run_in_executor(
                None, load_json_from_path, file_path
            )

            if validate:
                self._validate_basic_structure(clip_object, file_path)

            logger.info(f"Successfully loaded CLIP object from: {file_path}")
            return clip_object

        except Exception as e:
            raise AsyncCLIPFetchError(
                f"Failed to load CLIP object from {file_path}: {str(e)}"
            )

    async def fetch_batch(
        self,
        sources: List[str],
        use_cache: bool = True,
        validate: bool = True,
        max_concurrent: int = 10,
    ) -> List[Union[Dict[str, Any], Exception]]:
        """
        Asynchronously fetch multiple CLIP objects from a list of sources.

        Args:
            sources: List of URLs or file paths
            use_cache: Whether to use caching for requests
            validate: Whether to validate basic CLIP structure
            max_concurrent: Maximum number of concurrent requests

        Returns:
            List of fetched CLIP objects or exceptions for failed fetches

        Note:
            This method returns results for all sources, with exceptions
            for failed fetches. Use return_exceptions=True behavior.
        """
        # Create semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(max_concurrent)

        async def fetch_with_semaphore(source: str) -> Union[Dict[str, Any], Exception]:
            async with semaphore:
                try:
                    return await self.fetch(
                        source, use_cache=use_cache, validate=validate
                    )
                except Exception as e:
                    logger.error(f"Failed to fetch from {source}: {str(e)}")
                    return e

        # Execute all fetches concurrently
        tasks = [fetch_with_semaphore(source) for source in sources]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Track failed sources
        self._failed_sources = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self._failed_sources.append(
                    {"source": sources[i], "error": str(result)}
                )

        successful_count = sum(1 for r in results if not isinstance(r, Exception))
        logger.info(
            f"Batch fetch completed: {successful_count}/{len(sources)} successful"
        )

        return results

    async def fetch_multiple(
        self,
        sources: List[str],
        use_cache: bool = True,
        validate: bool = True,
        max_concurrent: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Asynchronously fetch multiple CLIP objects, returning only successful results.

        Args:
            sources: List of URLs or file paths
            use_cache: Whether to use caching for requests
            validate: Whether to validate basic CLIP structure
            max_concurrent: Maximum number of concurrent requests

        Returns:
            List of successfully fetched CLIP objects

        Note:
            Failed fetches are logged but don't stop the process.
            Use get_failed_sources() to check for failures.
        """
        results = await self.fetch_batch(sources, use_cache, validate, max_concurrent)

        # Filter out exceptions and return only successful results
        successful_results = [
            result for result in results if not isinstance(result, Exception)
        ]

        return successful_results

    def get_failed_sources(self) -> List[Dict[str, str]]:
        """
        Get list of sources that failed during the last batch operation.

        Returns:
            List of failed sources with error messages
        """
        return getattr(self, "_failed_sources", [])

    async def discover_from_directory(
        self, directory: str, recursive: bool = True
    ) -> List[str]:
        """
        Asynchronously discover CLIP JSON files in a directory.

        Args:
            directory: Directory to search
            recursive: Whether to search recursively

        Returns:
            List of discovered file paths
        """
        directory_path = Path(directory)
        if not directory_path.exists():
            raise AsyncCLIPFetchError(f"Directory does not exist: {directory}")

        # Run directory traversal in executor
        loop = asyncio.get_event_loop()

        def _discover_files():
            pattern = "**/*.json" if recursive else "*.json"
            json_files = list(directory_path.glob(pattern))

            # Filter to only include likely CLIP files
            clip_files = []
            for file_path in json_files:
                try:
                    # Quick check for CLIP structure
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if self._is_likely_clip_object(data):
                            clip_files.append(str(file_path))
                except (json.JSONDecodeError, IOError):
                    # Skip files that can't be read as JSON
                    continue

            return clip_files

        clip_files = await loop.run_in_executor(None, _discover_files)

        logger.info(f"Discovered {len(clip_files)} potential CLIP files in {directory}")
        return clip_files

    def clear_cache(self, pattern: Optional[str] = None) -> int:
        """
        Clear cached CLIP objects.

        Args:
            pattern: Optional pattern to match cache keys (None clears all)

        Returns:
            Number of entries cleared
        """
        if not self.cache_enabled or not self.cache:
            logger.warning("Cache is not enabled")
            return 0

        cleared = self.cache.clear(pattern)
        logger.info(
            f"Cleared {cleared} cache entries"
            + (f" matching '{pattern}'" if pattern else "")
        )
        return cleared

    def get_cache_stats(self) -> Optional[Dict[str, Any]]:
        """
        Get cache statistics.

        Returns:
            Cache statistics dictionary or None if caching disabled
        """
        if not self.cache_enabled or not self.cache:
            return None

        return self.cache.get_stats()

    def set_cache_max_age(self, max_age: Optional[int]) -> None:
        """
        Set the default cache max age.

        Args:
            max_age: Maximum age in seconds (None for no expiration)
        """
        if self.cache_enabled and self.cache:
            self.cache.max_age = max_age
            logger.info(f"Set cache max age to: {max_age}")
        else:
            logger.warning("Cache is not enabled")

    async def prefetch_urls(
        self, urls: List[str], use_cache: bool = True, max_concurrent: int = 10
    ) -> Dict[str, Any]:
        """
        Asynchronously prefetch multiple URLs and store in cache.

        Args:
            urls: List of URLs to prefetch
            use_cache: Whether to use/store in cache
            max_concurrent: Maximum number of concurrent requests

        Returns:
            Dictionary with prefetch results
        """
        import time

        start_time = time.time()

        results = {"successful": [], "failed": [], "cached": [], "total_time": 0}

        # Check cache first
        urls_to_fetch = []
        if self.cache_enabled and use_cache and self.cache:
            for url in urls:
                if self.cache.get(url) is not None:
                    results["cached"].append(url)
                else:
                    urls_to_fetch.append(url)
        else:
            urls_to_fetch = urls

        # Fetch remaining URLs
        if urls_to_fetch:
            fetch_results = await self.fetch_batch(
                urls_to_fetch, use_cache=use_cache, max_concurrent=max_concurrent
            )

            for i, result in enumerate(fetch_results):
                if isinstance(result, Exception):
                    results["failed"].append(
                        {"url": urls_to_fetch[i], "error": str(result)}
                    )
                else:
                    results["successful"].append(urls_to_fetch[i])

        results["total_time"] = time.time() - start_time

        logger.info(
            f"Async prefetch completed: {len(results['successful'])} successful, "
            f"{len(results['failed'])} failed, {len(results['cached'])} cached"
        )

        return results

    def _is_url(self, source: str) -> bool:
        """Check if a source is a URL."""
        try:
            result = urlparse(source)
            return bool(result.scheme and result.netloc)
        except Exception:
            return False

    def _validate_basic_structure(
        self, clip_object: Dict[str, Any], source: str
    ) -> None:
        """Validate basic CLIP object structure."""
        if not self._is_valid_clip_structure(clip_object):
            raise ValueError(f"Invalid CLIP object structure from {source}")

    def _is_valid_clip_structure(self, clip_object: Dict[str, Any]) -> bool:
        """Check if object has valid CLIP structure."""
        if not isinstance(clip_object, dict):
            return False

        # Check for required fields
        required_fields = ["@context", "type", "id"]
        if not all(field in clip_object for field in required_fields):
            return False

        # Check for valid CLIP context
        context = clip_object.get("@context")
        if not isinstance(context, str) or "clipprotocol.org" not in context:
            return False

        return True

    def _is_likely_clip_object(self, data: Dict[str, Any]) -> bool:
        """Quick check to see if a JSON object is likely a CLIP object."""
        if not isinstance(data, dict):
            return False

        # Check for CLIP indicators
        context = data.get("@context", "")
        has_clip_context = isinstance(context, str) and "clipprotocol.org" in context
        has_clip_type = data.get("type") in ["Venue", "Device", "SoftwareApp"]
        has_clip_id = isinstance(data.get("id"), str) and data.get("id", "").startswith(
            "clip:"
        )

        return has_clip_context or has_clip_type or has_clip_id
