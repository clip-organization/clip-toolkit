#!/usr/bin/env python3
"""
CLIP Toolkit - Python SDK Cache Performance Example

This example demonstrates the performance benefits of the new caching system
in the CLIP Python SDK, including memory and disk caching with HTTP header support.
"""

import json
import sys
import time
from pathlib import Path
from typing import List

# Add the SDK to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "packages" / "sdk-python"))

from clip_sdk import CLIPFetcher, CLIPCache, CLIPFetchError, get_default_cache_dir


def demonstrate_basic_caching():
    """Demonstrate basic caching functionality."""
    print("🔄 Basic Caching Demonstration")
    print("=" * 50)
    
    # Create a fetcher with caching enabled (default)
    fetcher = CLIPFetcher(cache_max_age=300)  # 5 minutes cache
    
    # Use local file for consistent demonstration
    examples_dir = Path(__file__).parent.parent / "sample-clips"
    
    if examples_dir.exists():
        sample_files = list(examples_dir.glob("*.json"))[:3]
        
        print(f"📁 Found {len(sample_files)} sample files to test with")
        
        for file_path in sample_files:
            # Convert to file:// URL for cache testing
            file_url = f"file://{file_path.absolute()}"
            
            print(f"\n📄 Testing: {file_path.name}")
            
            # First fetch
            start_time = time.time()
            try:
                clip_obj = fetcher.fetch(file_url)
                first_time = time.time() - start_time
                print(f"  First fetch: {first_time:.4f}s")
                print(f"  Object: {clip_obj.get('name', 'Unknown')}")
            except CLIPFetchError as e:
                print(f"  ❌ Error: {e}")
                continue
            
            # Second fetch (should hit cache for URLs)
            start_time = time.time()
            try:
                clip_obj = fetcher.fetch(file_url)
                second_time = time.time() - start_time
                print(f"  Second fetch: {second_time:.4f}s")
                
                if second_time < first_time:
                    speedup = first_time / second_time
                    print(f"  🚀 Speedup: {speedup:.1f}x faster!")
                else:
                    print("  📝 Note: File fetching doesn't use caching")
            except CLIPFetchError as e:
                print(f"  ❌ Error: {e}")
        
        # Show cache statistics
        stats = fetcher.get_cache_stats()
        if stats:
            print(f"\n📊 Cache Statistics:")
            print(f"  Total requests: {stats['total_requests']}")
            print(f"  Cache hits: {stats['hits']}")
            print(f"  Cache misses: {stats['misses']}")
            print(f"  Hit rate: {stats['hit_rate']:.1%}")
            print(f"  Memory entries: {stats['memory_entries']}")
    else:
        print("❌ Sample files not found")


def demonstrate_cache_configuration():
    """Demonstrate different cache configurations."""
    print("\n⚙️  Cache Configuration Examples")
    print("=" * 50)
    
    # Memory-only cache
    print("\n1. Memory-only cache:")
    memory_cache = CLIPCache(cache_dir=None, max_age=60, max_memory_entries=100)
    fetcher_memory = CLIPFetcher(cache=memory_cache)
    print(f"   Cache directory: {memory_cache.cache_dir}")
    print(f"   Max age: {memory_cache.max_age} seconds")
    print(f"   Max memory entries: {memory_cache.max_memory_entries}")
    
    # Disk cache with custom settings
    print("\n2. Disk cache with custom settings:")
    import tempfile
    with tempfile.TemporaryDirectory() as temp_dir:
        disk_cache = CLIPCache(
            cache_dir=temp_dir,
            max_age=1800,  # 30 minutes
            max_memory_entries=500,
            max_disk_size_mb=50
        )
        fetcher_disk = CLIPFetcher(cache=disk_cache)
        print(f"   Cache directory: {temp_dir}")
        print(f"   Max age: {disk_cache.max_age} seconds")
        print(f"   Max memory entries: {disk_cache.max_memory_entries}")
        print(f"   Max disk size: {disk_cache.max_disk_size_mb} MB")
    
    # No cache
    print("\n3. No cache:")
    fetcher_no_cache = CLIPFetcher(cache_enabled=False)
    print(f"   Cache enabled: {fetcher_no_cache.cache_enabled}")
    print(f"   Cache instance: {fetcher_no_cache.cache}")


def demonstrate_cache_management():
    """Demonstrate cache management features."""
    print("\n🗄️  Cache Management")
    print("=" * 50)
    
    # Create cache with test data
    cache = CLIPCache(cache_dir=None, max_age=None)
    fetcher = CLIPFetcher(cache=cache)
    
    # Add some test entries
    test_entries = {
        "https://example.com/venue1.json": {
            "@context": "https://clipprotocol.org/context/v1",
            "type": "Venue",
            "id": "clip:test:venue1",
            "name": "Test Venue 1"
        },
        "https://example.com/device1.json": {
            "@context": "https://clipprotocol.org/context/v1",
            "type": "Device", 
            "id": "clip:test:device1",
            "name": "Test Device 1"
        },
        "https://api.example.com/clip.json": {
            "@context": "https://clipprotocol.org/context/v1",
            "type": "Venue",
            "id": "clip:api:venue",
            "name": "API Venue"
        }
    }
    
    print("📝 Adding test entries to cache...")
    for url, data in test_entries.items():
        cache.set(url, data)
    
    # Show initial stats
    stats = fetcher.get_cache_stats()
    print(f"\n📊 Initial stats:")
    print(f"   Memory entries: {stats['memory_entries']}")
    
    # Demonstrate cache clearing with pattern
    print(f"\n🧹 Clearing cache entries matching 'example.com'...")
    cleared = fetcher.clear_cache("example.com")
    print(f"   Cleared {cleared} entries")
    
    # Show updated stats
    stats = fetcher.get_cache_stats()
    print(f"\n📊 After pattern clear:")
    print(f"   Memory entries: {stats['memory_entries']}")
    
    # Clear all remaining
    print(f"\n🧹 Clearing all cache entries...")
    cleared = fetcher.clear_cache()
    print(f"   Cleared {cleared} entries")
    
    # Final stats
    stats = fetcher.get_cache_stats()
    print(f"\n📊 Final stats:")
    print(f"   Memory entries: {stats['memory_entries']}")


def demonstrate_cache_expiration():
    """Demonstrate cache expiration functionality."""
    print("\n⏰ Cache Expiration")
    print("=" * 50)
    
    # Create cache with short expiration
    cache = CLIPCache(cache_dir=None, max_age=2)  # 2 seconds
    fetcher = CLIPFetcher(cache=cache)
    
    test_data = {
        "@context": "https://clipprotocol.org/context/v1",
        "type": "Venue",
        "id": "clip:test:expiry",
        "name": "Expiry Test Venue"
    }
    
    # Add entry to cache
    test_key = "https://example.com/expiry-test.json"
    cache.set(test_key, test_data)
    
    print(f"📝 Added entry with 2-second expiration")
    
    # Immediate retrieval should work
    cached = cache.get(test_key)
    print(f"   Immediate retrieval: {'✅ Success' if cached else '❌ Failed'}")
    
    # Wait for expiration
    print(f"⏳ Waiting 2.5 seconds for expiration...")
    time.sleep(2.5)
    
    # Should be expired now
    cached = cache.get(test_key)
    print(f"   After expiration: {'❌ Expired (expected)' if not cached else '⚠️  Still cached'}")
    
    # Test custom expiration
    print(f"\n📝 Testing custom max-age...")
    cache.set(test_key, test_data, max_age=1)  # 1 second override
    print(f"   Added with 1-second override")
    
    time.sleep(1.2)
    cached = cache.get(test_key)
    print(f"   After 1.2 seconds: {'❌ Expired (expected)' if not cached else '⚠️  Still cached'}")


def demonstrate_http_cache_headers():
    """Demonstrate HTTP cache header simulation."""
    print("\n🌐 HTTP Cache Headers Simulation")
    print("=" * 50)
    
    cache = CLIPCache(cache_dir=None)
    
    test_data = {
        "@context": "https://clipprotocol.org/context/v1",
        "type": "Device",
        "id": "clip:test:headers",
        "name": "HTTP Headers Test"
    }
    
    # Test max-age header
    print("1. Testing Cache-Control: max-age=3")
    headers = {"Cache-Control": "max-age=3"}
    cache.set("test-max-age", test_data, from_http_headers=headers)
    
    # Should be available immediately
    cached = cache.get("test-max-age")
    print(f"   Immediate: {'✅ Cached' if cached else '❌ Not cached'}")
    
    # Test no-cache header
    print("\n2. Testing Cache-Control: no-cache")
    headers = {"Cache-Control": "no-cache"}
    cache.set("test-no-cache", test_data, from_http_headers=headers)
    
    # Should expire immediately
    time.sleep(0.01)
    cached = cache.get("test-no-cache")
    print(f"   After tiny delay: {'❌ Not cached (expected)' if not cached else '⚠️  Still cached'}")
    
    # Test no headers (uses default)
    print("\n3. Testing no cache headers (uses default)")
    cache.set("test-default", test_data)
    cached = cache.get("test-default")
    print(f"   With defaults: {'✅ Cached' if cached else '❌ Not cached'}")


def demonstrate_performance_comparison():
    """Demonstrate performance comparison between cached and non-cached fetching."""
    print("\n🏃 Performance Comparison")
    print("=" * 50)
    
    # Simulate slow network responses
    class MockSlowFetcher(CLIPFetcher):
        def fetch_from_url(self, url, use_cache=True, validate=True):
            # Simulate network delay only if not using cache
            if not use_cache or not self.cache or not self.cache.get(url):
                time.sleep(0.1)  # 100ms delay
            
            # Return mock data
            return {
                "@context": "https://clipprotocol.org/context/v1",
                "type": "Venue",
                "id": f"clip:mock:{hash(url) % 1000}",
                "name": f"Mock Venue for {Path(url).name}"
            }
    
    # Test URLs
    test_urls = [
        "https://example.com/venue1.json",
        "https://example.com/venue2.json", 
        "https://example.com/venue3.json"
    ]
    
    # Test with caching enabled
    print("🔄 With caching enabled:")
    cache = CLIPCache(cache_dir=None)
    fetcher_cached = MockSlowFetcher(cache=cache)
    
    start_time = time.time()
    for url in test_urls:
        fetcher_cached.fetch_from_url(url)
    first_run_time = time.time() - start_time
    print(f"   First run (cold cache): {first_run_time:.3f}s")
    
    start_time = time.time()
    for url in test_urls:
        fetcher_cached.fetch_from_url(url)
    second_run_time = time.time() - start_time
    print(f"   Second run (warm cache): {second_run_time:.3f}s")
    
    # Test without caching
    print("\n🚫 Without caching:")
    fetcher_no_cache = MockSlowFetcher(cache_enabled=False)
    
    start_time = time.time()
    for url in test_urls:
        fetcher_no_cache.fetch_from_url(url, use_cache=False)
    no_cache_time = time.time() - start_time
    print(f"   No cache run: {no_cache_time:.3f}s")
    
    # Show comparison
    if second_run_time > 0:
        speedup = no_cache_time / second_run_time
        print(f"\n🚀 Cache speedup: {speedup:.1f}x faster!")
        savings = ((no_cache_time - second_run_time) / no_cache_time) * 100
        print(f"💰 Time savings: {savings:.1f}%")


def main():
    """Main function demonstrating caching features."""
    print("💾 CLIP Toolkit - Cache Performance Examples")
    print("=" * 60)
    
    print(f"📂 Default cache directory: {get_default_cache_dir()}")
    
    # Run demonstrations
    try:
        demonstrate_basic_caching()
        demonstrate_cache_configuration()
        demonstrate_cache_management()
        demonstrate_cache_expiration()
        demonstrate_http_cache_headers()
        demonstrate_performance_comparison()
        
        print(f"\n✅ All caching demonstrations completed!")
        print(f"\n💡 Key Benefits:")
        print(f"   • Significant performance improvements for repeated fetches")
        print(f"   • Intelligent HTTP cache header support")
        print(f"   • Automatic memory and disk cache management")
        print(f"   • Configurable expiration and size limits")
        print(f"   • LRU eviction for memory efficiency")
        print(f"   • Pattern-based cache clearing")
        
    except Exception as e:
        print(f"❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 