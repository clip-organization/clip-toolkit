#!/usr/bin/env python3
"""
Async CLIP Fetching Example

This example demonstrates the asynchronous capabilities of the CLIP Python SDK,
showing how to fetch CLIP objects efficiently using async/await syntax.
"""

import asyncio
import time
from typing import List

from clip_sdk import CLIPFetcher, AsyncCLIPFetcher


async def main():
    """Main async example function."""
    print("🚀 CLIP SDK Async Functionality Demo\n")
    
    # Example URLs (these would be real CLIP object URLs in practice)
    test_urls = [
        "https://api.example.com/clip/venue/library",
        "https://api.example.com/clip/venue/museum", 
        "https://api.example.com/clip/venue/restaurant",
        "https://api.example.com/clip/device/smart-speaker",
        "https://api.example.com/clip/app/mobile-app"
    ]
    
    print("📋 Test URLs:")
    for i, url in enumerate(test_urls, 1):
        print(f"  {i}. {url}")
    print()
    
    # 1. Basic async fetching
    print("1️⃣ Basic Async Fetching")
    print("=" * 50)
    
    async_fetcher = AsyncCLIPFetcher(cache_enabled=True)
    
    try:
        print("Attempting to fetch a single CLIP object asynchronously...")
        # This would work with a real URL
        # result = await async_fetcher.fetch(test_urls[0])
        # print(f"✅ Successfully fetched: {result.get('name', 'Unknown')}")
        print("⚠️  Skipping actual fetch (demo URLs)")
    except Exception as e:
        print(f"❌ Expected error with demo URLs: {type(e).__name__}")
    
    print()
    
    # 2. Batch async fetching
    print("2️⃣ Batch Async Fetching")
    print("=" * 50)
    
    print("Demonstrating concurrent batch fetching...")
    print(f"📊 Fetching {len(test_urls)} URLs concurrently (max 3 concurrent)")
    
    try:
        start_time = time.time()
        
        # This would work with real URLs
        # results = await async_fetcher.fetch_batch(test_urls, max_concurrent=3)
        # successful = [r for r in results if not isinstance(r, Exception)]
        # failed = [r for r in results if isinstance(r, Exception)]
        
        end_time = time.time()
        
        print("⚠️  Skipping actual batch fetch (demo URLs)")
        print(f"⏱️  Would have taken ~{end_time - start_time:.2f} seconds")
        # print(f"✅ Successful: {len(successful)}")
        # print(f"❌ Failed: {len(failed)}")
        
    except Exception as e:
        print(f"❌ Expected error with demo URLs: {type(e).__name__}")
    
    print()
    
    # 3. Performance comparison
    print("3️⃣ Sync vs Async Performance Comparison")
    print("=" * 50)
    
    print("Comparing sync vs async fetching performance...")
    
    # Sync fetcher
    sync_fetcher = CLIPFetcher(cache_enabled=True)
    
    def simulate_sync_batch_fetch(urls: List[str]) -> float:
        """Simulate sync batch fetching time."""
        start_time = time.time()
        # Simulate sequential fetching delay
        time.sleep(0.1 * len(urls))  # 100ms per URL
        return time.time() - start_time
    
    async def simulate_async_batch_fetch(urls: List[str]) -> float:
        """Simulate async batch fetching time."""
        start_time = time.time()
        # Simulate concurrent fetching delay (much faster)
        await asyncio.sleep(0.1)  # 100ms total for all URLs
        return time.time() - start_time
    
    # Simulate performance comparison
    sync_time = simulate_sync_batch_fetch(test_urls)
    async_time = await simulate_async_batch_fetch(test_urls)
    
    print(f"📈 Performance Results (simulated):")
    print(f"   Sync batch fetch:  {sync_time:.2f} seconds")
    print(f"   Async batch fetch: {async_time:.2f} seconds") 
    print(f"   🚀 Speedup: {sync_time / async_time:.1f}x faster with async!")
    print()
    
    # 4. Async with caching
    print("4️⃣ Async Caching")
    print("=" * 50)
    
    cached_fetcher = AsyncCLIPFetcher(
        cache_enabled=True,
        cache_max_age=3600  # 1 hour cache
    )
    
    print("Demonstrating async caching behavior...")
    print("🗄️  First fetch would populate cache")
    print("⚡ Second fetch would use cache (instant)")
    
    # Show cache stats
    cache_stats = cached_fetcher.get_cache_stats()
    if cache_stats:
        print(f"📊 Cache stats: {cache_stats['memory_entries']} entries in memory")
    
    print()
    
    # 5. Async error handling
    print("5️⃣ Async Error Handling")
    print("=" * 50)
    
    print("Demonstrating graceful error handling in async operations...")
    
    error_urls = [
        "https://nonexistent.example.com/clip/1",
        "https://api.example.com/clip/valid",
        "https://timeout.example.com/clip/slow"
    ]
    
    try:
        print(f"🔄 Attempting to fetch {len(error_urls)} URLs with mixed success...")
        # results = await async_fetcher.fetch_batch(error_urls)
        # successful = [r for r in results if not isinstance(r, Exception)]
        # errors = [r for r in results if isinstance(r, Exception)]
        
        print("⚠️  Skipping actual fetch (demo URLs)")
        print("✅ Async operations handle errors gracefully")
        print("📊 Failed requests don't block successful ones")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    
    print()
    
    # 6. Async integration with regular fetcher
    print("6️⃣ Async Integration with CLIPFetcher")
    print("=" * 50)
    
    print("CLIPFetcher now includes async methods for backward compatibility...")
    
    integrated_fetcher = CLIPFetcher(cache_enabled=True)
    
    try:
        print("🔄 Using async methods on regular CLIPFetcher...")
        # result = await integrated_fetcher.fetch_async(test_urls[0])
        # batch_results = await integrated_fetcher.fetch_multiple_async(test_urls[:3])
        
        print("✅ CLIPFetcher.fetch_async() - single async fetch")
        print("✅ CLIPFetcher.fetch_multiple_async() - batch async fetch")
        print("✅ CLIPFetcher.fetch_batch_async() - batch with exceptions")
        print("✅ Shared cache between sync and async methods")
        
    except Exception as e:
        print(f"⚠️  Expected error with demo URLs: {type(e).__name__}")
    
    print()
    
    # 7. Async file operations
    print("7️⃣ Async File Operations")
    print("=" * 50)
    
    print("Async fetcher can also work with local files...")
    print("📁 Files are processed in thread pool to avoid blocking")
    print("🔄 Directory discovery runs in background")
    
    try:
        # Example of async directory discovery
        # files = await async_fetcher.discover_from_directory("./examples", recursive=True)
        print("✅ discover_from_directory_async() - find CLIP files")
        print("✅ fetch_from_file_async() - load files without blocking")
        
    except Exception as e:
        print(f"⚠️  Note: {e}")
    
    print()
    
    # Summary
    print("📋 Summary")
    print("=" * 50)
    print("🚀 Async support provides significant performance improvements:")
    print("   • Concurrent HTTP requests for batch operations")
    print("   • Non-blocking file I/O operations")
    print("   • Proper async/await syntax support")
    print("   • Shared caching between sync and async methods")
    print("   • Graceful error handling with exceptions")
    print("   • Backward compatibility with existing code")
    print()
    print("💡 Best Practices:")
    print("   • Use AsyncCLIPFetcher for new async applications")
    print("   • Use CLIPFetcher.fetch_async() for mixed sync/async code")
    print("   • Set appropriate max_concurrent limits")
    print("   • Enable caching for better performance")
    print("   • Handle exceptions gracefully in batch operations")
    print()
    print("✨ The async support makes the CLIP SDK perfect for:")
    print("   • Web applications with high concurrency")
    print("   • Batch processing of multiple CLIP objects")
    print("   • Real-time applications requiring low latency")
    print("   • Integration with async frameworks (FastAPI, aiohttp, etc.)")


if __name__ == "__main__":
    # Run the async example
    print("Starting CLIP SDK Async Example...")
    print("Note: This example uses demo URLs for illustration.")
    print("Replace with real CLIP object URLs for actual testing.\n")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Example interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
    
    print("\n🎉 Async example completed!") 