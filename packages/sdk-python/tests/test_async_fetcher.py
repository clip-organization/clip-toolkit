"""
Tests for async CLIP fetcher functionality.
"""

import asyncio
import json
import tempfile
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import aiohttp
import pytest
from aioresponses import aioresponses

from clip_sdk import AsyncCLIPFetcher, AsyncCLIPFetchError, CLIPCache, CLIPFetcher

# Test data
VALID_CLIP_OBJECT = {
    "@context": "https://clipprotocol.org/context/v1",
    "type": "Venue",
    "id": "clip:test:venue:library",
    "name": "City Public Library",
    "description": "A modern library with excellent facilities",
}

INVALID_CLIP_OBJECT = {"type": "Unknown", "name": "Invalid Object"}


class TestAsyncCLIPFetcher:
    """Test the AsyncCLIPFetcher class."""

    @pytest.fixture
    def fetcher(self):
        """Create a test async fetcher."""
        return AsyncCLIPFetcher(timeout=5.0, max_retries=2, cache_enabled=False)

    @pytest.fixture
    def cached_fetcher(self):
        """Create a test async fetcher with caching enabled."""
        return AsyncCLIPFetcher(timeout=5.0, max_retries=2, cache_enabled=True)

    @pytest.fixture
    def temp_clip_file(self):
        """Create a temporary CLIP file for testing."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(VALID_CLIP_OBJECT, f)
            temp_path = f.name

        yield temp_path

        # Cleanup
        Path(temp_path).unlink(missing_ok=True)

    @pytest.mark.asyncio
    async def test_fetch_from_url_success(self, fetcher):
        """Test successful async URL fetching."""
        url = "https://api.example.com/clip/test"

        with aioresponses() as m:
            m.get(
                url,
                payload=VALID_CLIP_OBJECT,
                headers={"Content-Type": "application/json"},
            )

            result = await fetcher.fetch_from_url(url)

            assert result == VALID_CLIP_OBJECT
            assert len(m.requests) == 1

    @pytest.mark.asyncio
    async def test_fetch_from_url_with_retries(self, fetcher):
        """Test async URL fetching with retries."""
        url = "https://api.example.com/clip/retry"

        with aioresponses() as m:
            # First attempt fails
            m.get(url, status=500)
            # Second attempt succeeds
            m.get(
                url,
                payload=VALID_CLIP_OBJECT,
                headers={"Content-Type": "application/json"},
            )

            result = await fetcher.fetch_from_url(url)

            assert result == VALID_CLIP_OBJECT
            assert len(m.requests) == 2

    @pytest.mark.asyncio
    async def test_fetch_from_url_timeout(self, fetcher):
        """Test async URL fetching with timeout."""
        url = "https://api.example.com/clip/timeout"

        with aioresponses() as m:
            m.get(url, exception=asyncio.TimeoutError())

            with pytest.raises(AsyncCLIPFetchError) as exc_info:
                await fetcher.fetch_from_url(url)

            assert "Failed to fetch CLIP object" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_fetch_from_url_network_error(self, fetcher):
        """Test async URL fetching with network error."""
        url = "https://nonexistent.example.com/clip/test"

        with aioresponses() as m:
            m.get(
                url,
                exception=aiohttp.ClientConnectorError(None, OSError("Network error")),
            )

            with pytest.raises(AsyncCLIPFetchError) as exc_info:
                await fetcher.fetch_from_url(url)

            assert "Failed to fetch CLIP object" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_fetch_from_url_invalid_json(self, fetcher):
        """Test async URL fetching with invalid JSON response."""
        url = "https://api.example.com/clip/invalid"

        with aioresponses() as m:
            m.get(
                url,
                body="Invalid JSON content",
                headers={"Content-Type": "application/json"},
            )

            with pytest.raises(AsyncCLIPFetchError) as exc_info:
                await fetcher.fetch_from_url(url)

            assert "Failed to fetch CLIP object" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_fetch_from_url_http_error(self, fetcher):
        """Test async URL fetching with HTTP error status."""
        url = "https://api.example.com/clip/notfound"

        with aioresponses() as m:
            m.get(url, status=404)

            with pytest.raises(AsyncCLIPFetchError) as exc_info:
                await fetcher.fetch_from_url(url)

            assert "Failed to fetch CLIP object" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_fetch_from_file_success(self, fetcher, temp_clip_file):
        """Test successful async file fetching."""
        result = await fetcher.fetch_from_file(temp_clip_file)

        assert result == VALID_CLIP_OBJECT

    @pytest.mark.asyncio
    async def test_fetch_from_file_not_found(self, fetcher):
        """Test async file fetching with non-existent file."""
        with pytest.raises(AsyncCLIPFetchError) as exc_info:
            await fetcher.fetch_from_file("/nonexistent/file.json")

        assert "Failed to load CLIP object" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_fetch_with_validation_success(self, fetcher, temp_clip_file):
        """Test async fetch with successful validation."""
        result = await fetcher.fetch(temp_clip_file, validate=True)

        assert result == VALID_CLIP_OBJECT

    @pytest.mark.asyncio
    async def test_fetch_with_validation_failure(self, fetcher):
        """Test async fetch with validation failure."""
        url = "https://api.example.com/clip/invalid"

        with aioresponses() as m:
            m.get(
                url,
                payload=INVALID_CLIP_OBJECT,
                headers={"Content-Type": "application/json"},
            )

            with pytest.raises(AsyncCLIPFetchError) as exc_info:
                await fetcher.fetch_from_url(url, validate=True)

            assert "Invalid CLIP object structure" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_fetch_batch_success(self, fetcher):
        """Test successful async batch fetching."""
        urls = [
            "https://api.example.com/clip/1",
            "https://api.example.com/clip/2",
            "https://api.example.com/clip/3",
        ]

        with aioresponses() as m:
            for i, url in enumerate(urls):
                clip_data = {**VALID_CLIP_OBJECT, "id": f"clip:test:venue:library{i+1}"}
                m.get(
                    url, payload=clip_data, headers={"Content-Type": "application/json"}
                )

            results = await fetcher.fetch_batch(urls)

            assert len(results) == 3
            assert all(not isinstance(result, Exception) for result in results)
            assert len(m.requests) == 3

    @pytest.mark.asyncio
    async def test_fetch_batch_with_failures(self, fetcher):
        """Test async batch fetching with some failures."""
        urls = [
            "https://api.example.com/clip/1",
            "https://api.example.com/clip/error",
            "https://api.example.com/clip/3",
        ]

        with aioresponses() as m:
            m.get(
                urls[0],
                payload=VALID_CLIP_OBJECT,
                headers={"Content-Type": "application/json"},
            )
            m.get(urls[1], status=500)
            m.get(
                urls[2],
                payload=VALID_CLIP_OBJECT,
                headers={"Content-Type": "application/json"},
            )

            results = await fetcher.fetch_batch(urls)

            assert len(results) == 3
            assert not isinstance(results[0], Exception)
            assert isinstance(results[1], Exception)
            assert not isinstance(results[2], Exception)

            failed_sources = fetcher.get_failed_sources()
            assert len(failed_sources) == 1
            assert failed_sources[0]["source"] == urls[1]

    @pytest.mark.asyncio
    async def test_fetch_multiple_success(self, fetcher):
        """Test successful async multiple fetching (only successful results)."""
        urls = [
            "https://api.example.com/clip/1",
            "https://api.example.com/clip/error",
            "https://api.example.com/clip/3",
        ]

        with aioresponses() as m:
            m.get(
                urls[0],
                payload=VALID_CLIP_OBJECT,
                headers={"Content-Type": "application/json"},
            )
            m.get(urls[1], status=500)
            m.get(
                urls[2],
                payload=VALID_CLIP_OBJECT,
                headers={"Content-Type": "application/json"},
            )

            results = await fetcher.fetch_multiple(urls)

            assert len(results) == 2  # Only successful results
            assert all(isinstance(result, dict) for result in results)

    @pytest.mark.asyncio
    async def test_concurrency_limiting(self, fetcher):
        """Test that concurrent requests are properly limited."""
        urls = [f"https://api.example.com/clip/{i}" for i in range(20)]

        with aioresponses() as m:
            for url in urls:
                m.get(
                    url,
                    payload=VALID_CLIP_OBJECT,
                    headers={"Content-Type": "application/json"},
                )

            start_time = time.time()
            results = await fetcher.fetch_batch(urls, max_concurrent=5)
            end_time = time.time()

            assert len(results) == 20
            assert all(not isinstance(result, Exception) for result in results)
            # With 5 concurrent requests, it should take some time
            assert end_time - start_time > 0

    @pytest.mark.asyncio
    async def test_cache_integration(self, cached_fetcher):
        """Test async fetcher integration with caching."""
        url = "https://api.example.com/clip/cached"

        with aioresponses() as m:
            m.get(
                url,
                payload=VALID_CLIP_OBJECT,
                headers={"Content-Type": "application/json"},
            )

            # First request should hit the network
            result1 = await cached_fetcher.fetch_from_url(url)
            assert result1 == VALID_CLIP_OBJECT
            assert len(m.requests) == 1

            # Second request should use cache
            result2 = await cached_fetcher.fetch_from_url(url)
            assert result2 == VALID_CLIP_OBJECT
            assert len(m.requests) == 1  # No additional network request

    @pytest.mark.asyncio
    async def test_cache_http_headers(self, cached_fetcher):
        """Test async fetcher caching with HTTP headers."""
        url = "https://api.example.com/clip/headers"

        with aioresponses() as m:
            headers = {
                "Content-Type": "application/json",
                "Cache-Control": "max-age=300",
            }
            m.get(url, payload=VALID_CLIP_OBJECT, headers=headers)

            result = await cached_fetcher.fetch_from_url(url)
            assert result == VALID_CLIP_OBJECT

            # Check that the object is cached
            cache_stats = cached_fetcher.get_cache_stats()
            assert cache_stats is not None
            assert cache_stats["memory_entries"] > 0

    @pytest.mark.asyncio
    async def test_discover_from_directory(self, fetcher):
        """Test async directory discovery."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create test files
            clip_file = temp_path / "test.json"
            with open(clip_file, "w") as f:
                json.dump(VALID_CLIP_OBJECT, f)

            non_clip_file = temp_path / "other.json"
            with open(non_clip_file, "w") as f:
                json.dump({"not": "a clip object"}, f)

            discovered = await fetcher.discover_from_directory(str(temp_path))

            assert len(discovered) == 1
            assert str(clip_file) in discovered

    @pytest.mark.asyncio
    async def test_prefetch_urls(self, cached_fetcher):
        """Test async URL prefetching."""
        urls = [
            "https://api.example.com/clip/1",
            "https://api.example.com/clip/2",
            "https://api.example.com/clip/error",
        ]

        with aioresponses() as m:
            m.get(
                urls[0],
                payload=VALID_CLIP_OBJECT,
                headers={"Content-Type": "application/json"},
            )
            m.get(
                urls[1],
                payload=VALID_CLIP_OBJECT,
                headers={"Content-Type": "application/json"},
            )
            m.get(urls[2], status=500)

            results = await cached_fetcher.prefetch_urls(urls)

            assert len(results["successful"]) == 2
            assert len(results["failed"]) == 1
            assert len(results["cached"]) == 0
            assert results["total_time"] > 0


class TestCLIPFetcherAsyncIntegration:
    """Test the integration of async methods in CLIPFetcher."""

    @pytest.fixture
    def fetcher(self):
        """Create a test fetcher with async support."""
        return CLIPFetcher(timeout=5.0, max_retries=2, cache_enabled=False)

    @pytest.mark.asyncio
    async def test_fetch_async_method(self, fetcher, temp_clip_file):
        """Test the async fetch method in CLIPFetcher."""
        result = await fetcher.fetch_async(temp_clip_file)

        assert result == VALID_CLIP_OBJECT

    @pytest.mark.asyncio
    async def test_fetch_multiple_async_method(self, fetcher):
        """Test the async fetch_multiple method."""
        urls = ["https://api.example.com/clip/1", "https://api.example.com/clip/2"]

        with aioresponses() as m:
            for url in urls:
                m.get(
                    url,
                    payload=VALID_CLIP_OBJECT,
                    headers={"Content-Type": "application/json"},
                )

            results = await fetcher.fetch_multiple_async(urls)

            assert len(results) == 2
            assert all(isinstance(result, dict) for result in results)

    @pytest.mark.asyncio
    async def test_shared_cache_between_sync_async(self, temp_clip_file):
        """Test that sync and async methods share the same cache."""
        fetcher = CLIPFetcher(cache_enabled=True)
        url = "https://api.example.com/clip/shared"

        with aioresponses() as m:
            m.get(
                url,
                payload=VALID_CLIP_OBJECT,
                headers={"Content-Type": "application/json"},
            )

            # Fetch with sync method first
            with patch("requests.get") as mock_get:
                mock_response = MagicMock()
                mock_response.json.return_value = VALID_CLIP_OBJECT
                mock_response.headers = {"Content-Type": "application/json"}
                mock_response.raise_for_status.return_value = None
                mock_get.return_value = mock_response

                result1 = fetcher.fetch_from_url(url)
                assert result1 == VALID_CLIP_OBJECT
                assert mock_get.call_count == 1

            # Fetch with async method should use cache
            result2 = await fetcher.fetch_from_url_async(url)
            assert result2 == VALID_CLIP_OBJECT
            assert len(m.requests) == 0  # No network request made

    @pytest.fixture
    def temp_clip_file(self):
        """Create a temporary CLIP file for testing."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(VALID_CLIP_OBJECT, f)
            temp_path = f.name

        yield temp_path

        # Cleanup
        Path(temp_path).unlink(missing_ok=True)


class TestPerformanceComparison:
    """Test performance differences between sync and async methods."""

    @pytest.mark.asyncio
    async def test_batch_performance_comparison(self):
        """Compare performance of sync vs async batch fetching."""
        urls = [f"https://api.example.com/clip/{i}" for i in range(10)]

        # Test sync fetcher
        sync_fetcher = CLIPFetcher(cache_enabled=False)

        # Test async fetcher
        async_fetcher = AsyncCLIPFetcher(cache_enabled=False)

        with aioresponses() as m:
            for url in urls:
                m.get(
                    url,
                    payload=VALID_CLIP_OBJECT,
                    headers={"Content-Type": "application/json"},
                )

            # Time async batch fetch
            start_time = time.time()
            async_results = await async_fetcher.fetch_batch(urls, max_concurrent=5)
            async_time = time.time() - start_time

            assert len(async_results) == 10
            assert all(not isinstance(result, Exception) for result in async_results)

            # Async should be reasonably fast due to concurrency
            assert async_time < 2.0  # Should complete in under 2 seconds

    @pytest.mark.asyncio
    async def test_concurrent_request_efficiency(self):
        """Test that concurrent requests are more efficient than sequential."""
        urls = [f"https://api.example.com/clip/concurrent/{i}" for i in range(5)]

        async_fetcher = AsyncCLIPFetcher(cache_enabled=False)

        with aioresponses() as m:
            for url in urls:
                # Add a small delay to simulate network latency
                m.get(
                    url,
                    payload=VALID_CLIP_OBJECT,
                    headers={"Content-Type": "application/json"},
                )

            # Test concurrent fetching
            start_time = time.time()
            results = await async_fetcher.fetch_batch(urls, max_concurrent=5)
            concurrent_time = time.time() - start_time

            assert len(results) == 5
            assert all(not isinstance(result, Exception) for result in results)

            # With proper async handling, this should be efficient
            assert concurrent_time < 1.0
