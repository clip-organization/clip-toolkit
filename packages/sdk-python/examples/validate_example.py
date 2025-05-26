#!/usr/bin/env python3
"""
Example script demonstrating CLIP object validation using the Python SDK.
"""

import json

from clip_sdk import CLIPValidator


def main():
    """Main example function."""
    print("CLIP Python SDK - Validation Example")
    print("=" * 40)

    # Create a validator instance
    validator = CLIPValidator()

    # Example 1: Validate a CLIP object from a dictionary
    print("\n1. Validating a CLIP object from dictionary:")
    clip_object = {
        "@context": "https://clipprotocol.org/v1",
        "type": "Venue",
        "id": "clip:example:venue:cafe-123",
        "name": "The Example Café",
        "description": "A cozy café in downtown serving excellent coffee and pastries.",
        "lastUpdated": "2024-01-15T10:30:00Z",
        "location": {
            "address": "123 Main Street, Example City, ST 12345",
            "coordinates": {"latitude": 40.7589, "longitude": -73.9851},
            "timezone": "America/New_York",
        },
        "features": [
            {
                "name": "WiFi",
                "type": "facility",
                "available": 1,
                "metadata": {"description": "Free high-speed internet"},
            },
            {"name": "Seating", "type": "facility", "count": 30, "available": 25},
        ],
        "actions": [
            {
                "label": "View Menu",
                "type": "link",
                "endpoint": "https://example-cafe.com/menu",
                "description": "View our current menu and prices",
            }
        ],
    }

    try:
        result = validator.validate(clip_object)

        print(f"✓ Valid: {result['valid']}")
        print(f"📊 Completeness: {result['stats']['completeness']}%")
        print(f"📏 Size: {result['stats']['estimatedSize']} bytes")
        print(f"🏷️  Type: {result['stats']['type']}")
        print(f"🔧 Features: {result['stats']['featureCount']}")
        print(f"⚡ Actions: {result['stats']['actionCount']}")

        if result["warnings"]:
            print("⚠️  Warnings:")
            for warning in result["warnings"]:
                print(f"   - {warning}")

        if result["errors"]:
            print("❌ Errors:")
            for error in result["errors"]:
                print(f"   - {error['field']}: {error['message']}")

    except Exception as e:
        print(f"❌ Validation failed: {e}")

    # Example 2: Validate an invalid CLIP object
    print("\n2. Validating an invalid CLIP object:")
    invalid_clip = {
        "@context": "https://invalid-context.com/v1",
        "type": "InvalidType",
        "name": "Missing required fields",
        # Missing id and description
    }

    try:
        result = validator.validate(invalid_clip)

        print(f"✓ Valid: {result['valid']}")

        if result["errors"]:
            print("❌ Errors found:")
            for error in result["errors"]:
                print(f"   - {error['field']}: {error['message']}")
                if "suggestion" in error and error["suggestion"]:
                    print(f"     💡 {error['suggestion']}")

    except Exception as e:
        print(f"❌ Validation failed: {e}")

    # Example 3: Validate from JSON string
    print("\n3. Validating from JSON string:")
    json_string = json.dumps(
        {
            "@context": "https://clipprotocol.org/v1",
            "type": "Device",
            "id": "clip:example:device:sensor-456",
            "name": "Temperature Sensor",
            "description": "IoT temperature sensor for environmental monitoring",
            "features": [
                {
                    "name": "Temperature Reading",
                    "type": "sensor",
                    "value": 22.5,
                    "metadata": {"unit": "celsius", "accuracy": "±0.1°C"},
                }
            ],
        }
    )

    try:
        result = validator.validate(json_string)
        print(f"✓ Valid: {result['valid']}")
        print(f"📊 Completeness: {result['stats']['completeness']}%")
        print(f"🏷️  Type: {result['stats']['type']}")

    except Exception as e:
        print(f"❌ Validation failed: {e}")

    print("\n" + "=" * 40)
    print("Validation examples completed!")


if __name__ == "__main__":
    main()
