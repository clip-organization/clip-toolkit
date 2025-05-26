#!/usr/bin/env python3
"""
Example script demonstrating CLIP object fetching using the Python SDK.
"""

import json
import tempfile
from pathlib import Path

from clip_sdk import CLIPFetcher, CLIPObject


def create_sample_clip_files(temp_dir: Path):
    """Create sample CLIP files for demonstration."""
    # Sample venue CLIP
    venue_clip = {
        "@context": "https://clipprotocol.org/v1",
        "type": "Venue",
        "id": "clip:example:venue:library-001",
        "name": "Central Public Library",
        "description": (
            "A modern public library with extensive resources and community programs."
        ),
        "lastUpdated": "2024-01-15T14:30:00Z",
        "location": {
            "address": "100 Library Ave, Book City, BC 12345",
            "coordinates": {"latitude": 40.7500, "longitude": -73.9900},
            "timezone": "America/New_York",
        },
        "features": [
            {
                "name": "Books",
                "type": "resource",
                "count": 50000,
                "metadata": {
                    "description": "Wide collection of books across all genres"
                },
            },
            {
                "name": "Computer Lab",
                "type": "facility",
                "available": 20,
                "metadata": {"description": "Public computer access with internet"},
            },
        ],
        "actions": [
            {
                "label": "Check Catalog",
                "type": "link",
                "endpoint": "https://library.example.com/catalog",
                "description": "Search the library's online catalog",
            }
        ],
    }

    # Sample device CLIP
    device_clip = {
        "@context": "https://clipprotocol.org/v1",
        "type": "Device",
        "id": "clip:example:device:printer-002",
        "name": "Office Laser Printer",
        "description": "High-speed laser printer for office documents.",
        "lastUpdated": "2024-01-15T09:15:00Z",
        "features": [
            {
                "name": "Print Status",
                "type": "sensor",
                "value": "ready",
                "metadata": {"lastUpdated": "2024-01-15T09:15:00Z"},
            },
            {
                "name": "Paper Level",
                "type": "sensor",
                "value": 75,
                "metadata": {"unit": "percent"},
            },
        ],
        "actions": [
            {
                "label": "Print Document",
                "type": "api",
                "endpoint": "https://printer.example.com/api/print",
                "description": "Send a document to print",
            }
        ],
    }

    # Save files
    venue_file = temp_dir / "venue.json"
    device_file = temp_dir / "device.json"

    with open(venue_file, "w") as f:
        json.dump(venue_clip, f, indent=2)

    with open(device_file, "w") as f:
        json.dump(device_clip, f, indent=2)

    return [str(venue_file), str(device_file)]


def example_local_files(fetcher, clip_files):
    """Example 1: Fetch from local files."""
    print("\n1. Fetching CLIP objects from local files:")
    for file_path in clip_files:
        try:
            clip_object = fetcher.fetch_from_file(file_path)
            print(f"✓ Loaded {clip_object['name']} ({clip_object['type']})")
            print(f"   ID: {clip_object['id']}")
            print(f"   Features: {len(clip_object.get('features', []))}")
            print(f"   Actions: {len(clip_object.get('actions', []))}")
        except Exception as e:
            print(f"❌ Failed to load {file_path}: {e}")


def example_batch_fetch(fetcher, clip_files):
    """Example 2: Fetch multiple files at once."""
    print("\n2. Fetching multiple CLIP objects at once:")
    try:
        clip_objects = fetcher.fetch_multiple(clip_files)
        print(f"✓ Successfully fetched {len(clip_objects)} CLIP objects")

        for obj in clip_objects:
            print(f"   - {obj['name']} ({obj['type']})")

        # Check for any failures
        failed = fetcher.get_failed_sources()
        if failed:
            print(f"❌ {len(failed)} sources failed:")
            for failure in failed:
                print(f"   - {failure['source']}: {failure['error']}")
    except Exception as e:
        print(f"❌ Batch fetch failed: {e}")


def example_discover(fetcher, temp_dir):
    """Example 3: Discover CLIP files in directory."""
    print("\n3. Discovering CLIP files in directory:")
    try:
        discovered_files = fetcher.discover_from_directory(temp_dir)
        print(f"✓ Discovered {len(discovered_files)} CLIP files:")
        for file_path in discovered_files:
            filename = Path(file_path).name
            print(f"   - {filename}")
    except Exception as e:
        print(f"❌ Discovery failed: {e}")


def example_clip_object(fetcher, clip_files):
    """Example 4: Work with CLIPObject class."""
    print("\n4. Working with CLIPObject class:")
    try:
        # Fetch and convert to CLIPObject
        raw_clip = fetcher.fetch_from_file(clip_files[0])
        clip_obj = CLIPObject.from_dict(raw_clip)

        print("✓ Created CLIPObject: " + str(clip_obj))
        print(f"   Type: {clip_obj.type}")
        print(f"   Name: {clip_obj.name}")

        # Get statistics
        stats = clip_obj.get_statistics()
        print("   Statistics:")
        print(f"     - Features: {stats['featureCount']}")
        print(f"     - Actions: {stats['actionCount']}")
        print(f"     - Has Location: {stats['hasLocation']}")
        print(f"     - Size: {stats['estimatedSize']} bytes")

        # Check completeness
        completeness = clip_obj.validate_completeness()
        print(f"   Completeness: {completeness['completeness']}%")

        if completeness["missingFields"]:
            print(f"   Missing fields: {', '.join(completeness['missingFields'])}")

        # Modify the object
        clip_obj.update_timestamp()
        clip_obj.add_feature("New Feature", "example", value="test")
        print("   ✓ Added feature, updated timestamp")
    except Exception as e:
        print(f"❌ CLIPObject example failed: {e}")


def example_caching(temp_path, clip_files):
    """Example 5: Demonstrate fetcher with caching."""
    print("\n5. Fetcher with caching enabled:")
    try:
        cached_fetcher = CLIPFetcher(
            cache_enabled=True, cache_dir=str(temp_path / "cache")
        )

        # This would work with URLs in a real scenario
        clip_object = cached_fetcher.fetch_from_file(clip_files[0])
        print(f"✓ Fetched with caching: {clip_object['name']}")
        print(f"   Cache directory: {cached_fetcher.cache_dir}")
    except Exception as e:
        print(f"❌ Cached fetch failed: {e}")


def main():
    """Main example function."""
    print("CLIP Python SDK - Fetching Example")
    print("=" * 40)

    # Create a fetcher instance
    fetcher = CLIPFetcher(timeout=10.0, max_retries=2)

    # Create temporary files for demonstration
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        print(f"\n📁 Created temporary directory: {temp_dir}")

        # Create sample CLIP files
        clip_files = create_sample_clip_files(temp_path)
        print(f"📄 Created {len(clip_files)} sample CLIP files")

        # Run examples
        example_local_files(fetcher, clip_files)
        example_batch_fetch(fetcher, clip_files)
        example_discover(fetcher, temp_dir)
        example_clip_object(fetcher, clip_files)
        example_caching(temp_path, clip_files)

    # Example 6: Demonstrate URL fetching (simulated)
    print("\n6. URL fetching (example - would work with real URLs):")
    print("   Example usage:")
    print("   fetcher.fetch_from_url('https://example.com/clip.json')")
    print(
        "   fetcher.fetch('https://example.com/clip.json')  "
        "# Auto-detects URL vs file"
    )

    print("\n" + "=" * 40)
    print("Fetching examples completed!")
    print("\n💡 Tips:")
    print("   - Use CLIPFetcher for loading CLIP objects from various sources")
    print("   - Enable caching for better performance with remote URLs")
    print("   - Use fetch_multiple() for batch operations")
    print("   - CLIPObject provides a rich interface for working with CLIP data")


if __name__ == "__main__":
    main()
