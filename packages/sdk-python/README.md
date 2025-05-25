# CLIP Python SDK

A comprehensive Python SDK for working with CLIP (Context Link Interface Protocol) objects. This SDK provides validation, fetching, and manipulation capabilities for CLIP data structures.

## Features

- 🔍 **Schema Validation** - Validate CLIP objects against the official schema
- 📥 **Multi-source Fetching** - Load CLIP objects from files, URLs, and directories  
- 🏗️ **Object Modeling** - Rich Pydantic models for type-safe CLIP object manipulation
- 📊 **Statistics & Analysis** - Comprehensive analysis of CLIP object completeness and structure
- 🚀 **High Performance** - Efficient caching and batch operations
- 🛡️ **Type Safety** - Full TypeScript-style type hints and validation
- 🔧 **Extensible** - Easy to extend and customize for specific use cases

## Installation

### From PyPI (when published)
```bash
pip install clip-sdk
```

### Development Installation
```bash
git clone https://github.com/clip-organization/clip-toolkit.git
cd clip-toolkit/packages/sdk-python
pip install -e .
```

### With Development Dependencies
```bash
pip install -e ".[dev]"
```

## Quick Start

### Basic Validation

```python
from clip_sdk import CLIPValidator

# Create a validator
validator = CLIPValidator()

# Validate a CLIP object
clip_object = {
    "@context": "https://clipprotocol.org/v1",
    "type": "Venue",
    "id": "clip:example:venue:cafe-123",
    "name": "The Example Café",
    "description": "A cozy café serving excellent coffee."
}

result = validator.validate(clip_object)
print(f"Valid: {result['valid']}")
print(f"Completeness: {result['stats']['completeness']}%")
```

### Fetching CLIP Objects

```python
from clip_sdk import CLIPFetcher

# Create a fetcher
fetcher = CLIPFetcher()

# Fetch from file
clip_object = fetcher.fetch_from_file("venue.json")

# Fetch from URL
clip_object = fetcher.fetch_from_url("https://example.com/clip.json")

# Fetch multiple sources
clip_objects = fetcher.fetch_multiple([
    "venue1.json",
    "venue2.json", 
    "https://example.com/device.json"
])
```

### Working with CLIPObject Models

```python
from clip_sdk import CLIPObject

# Create from dictionary
clip_obj = CLIPObject.from_dict({
    "@context": "https://clipprotocol.org/v1",
    "type": "Device",
    "id": "clip:example:device:sensor-456",
    "name": "Temperature Sensor",
    "description": "IoT temperature sensor"
})

# Add features and actions
clip_obj.add_feature("Temperature", "sensor", value=22.5)
clip_obj.add_action("Get Reading", "api", "https://sensor.com/api/reading")

# Set location
clip_obj.set_location(
    address="Building A, Floor 2",
    coordinates={"latitude": 40.7128, "longitude": -74.0060}
)

# Update timestamp
clip_obj.update_timestamp()

# Export to JSON
json_output = clip_obj.to_json()
```

## Core Components

### CLIPValidator

Validates CLIP objects against the official JSON schema with detailed error reporting.

```python
from clip_sdk import CLIPValidator

validator = CLIPValidator(
    schema_url="https://custom-schema.com/clip.json",  # Custom schema URL
    cache_schema=True,                                 # Enable schema caching
    strict_mode=False                                  # Strict validation mode
)

# Validate with detailed results
result = validator.validate(clip_object)

# Check validation results
if result['valid']:
    print("✅ CLIP object is valid!")
    print(f"Completeness: {result['stats']['completeness']}%")
else:
    print("❌ Validation errors:")
    for error in result['errors']:
        print(f"  - {error['field']}: {error['message']}")
        if error['suggestion']:
            print(f"    💡 {error['suggestion']}")

# Handle warnings
if result['warnings']:
    print("⚠️ Warnings:")
    for warning in result['warnings']:
        print(f"  - {warning}")
```

### CLIPFetcher

Fetches CLIP objects from various sources with caching and error handling.

```python
from clip_sdk import CLIPFetcher

fetcher = CLIPFetcher(
    timeout=30.0,                    # Request timeout
    max_retries=3,                   # Maximum retry attempts
    cache_enabled=True,              # Enable local caching
    cache_dir="~/.clip_sdk/cache"    # Cache directory
)

# Fetch single object
try:
    clip_object = fetcher.fetch("source.json")  # Auto-detects file vs URL
    print(f"Loaded: {clip_object['name']}")
except CLIPFetchError as e:
    print(f"Fetch failed: {e}")

# Batch fetching
sources = ["file1.json", "file2.json", "https://example.com/clip.json"]
clip_objects = fetcher.fetch_multiple(sources)

# Check for failures
failed = fetcher.get_failed_sources()
for failure in failed:
    print(f"Failed: {failure['source']} - {failure['error']}")

# Discover CLIP files in directory
clip_files = fetcher.discover_from_directory("/path/to/clips", recursive=True)
```

### CLIPObject

Rich Pydantic model for type-safe CLIP object manipulation.

```python
from clip_sdk import CLIPObject

# Create from various sources
clip_obj = CLIPObject.from_dict(data)
clip_obj = CLIPObject.from_json(json_string)

# Manipulate the object
clip_obj.add_feature("WiFi", "facility", available=True)
clip_obj.add_action("Book Table", "api", "https://restaurant.com/api/book")
clip_obj.add_service("mcp", "mcp://restaurant.com/service")

clip_obj.set_location(
    address="123 Main St, City, State 12345",
    coordinates={"latitude": 40.7589, "longitude": -73.9851},
    timezone="America/New_York"
)

clip_obj.set_persona(
    role="Restaurant Assistant",
    personality="friendly and helpful",
    expertise=["dining", "reservations", "menu"],
    prompt="You are a helpful restaurant assistant."
)

# Analysis and statistics
stats = clip_obj.get_statistics()
completeness = clip_obj.validate_completeness()

print(f"Type: {stats['type']}")
print(f"Features: {stats['featureCount']}")
print(f"Actions: {stats['actionCount']}")
print(f"Completeness: {completeness['completeness']}%")

# Export in various formats
dict_data = clip_obj.to_dict()
json_string = clip_obj.to_json(indent=2)

# Clone and merge
cloned = clip_obj.clone()
merged = clip_obj.merge_with(other_clip_obj)
```

## Advanced Usage

### Custom Validation

```python
from clip_sdk import CLIPValidator

# Use custom schema
validator = CLIPValidator(schema_path="./custom-clip-schema.json")

# Strict mode validation
strict_validator = CLIPValidator(strict_mode=True)

# Validate file directly
result = validator.validate_file("clip-object.json")

# Validate from URL
result = validator.validate_url("https://example.com/clip.json")
```

### Caching and Performance

```python
from clip_sdk import CLIPFetcher

# Enable caching for better performance
fetcher = CLIPFetcher(
    cache_enabled=True,
    cache_dir="./clip_cache"
)

# Fetch with caching (subsequent requests will use cache)
clip_object = fetcher.fetch_from_url("https://api.example.com/clip.json")

# Clear cache when needed
fetcher.clear_cache()
```

### Batch Processing

```python
from clip_sdk import CLIPFetcher, CLIPValidator
import json

fetcher = CLIPFetcher()
validator = CLIPValidator()

# Discover and validate all CLIP files in a directory
clip_files = fetcher.discover_from_directory("./clips")
results = []

for file_path in clip_files:
    try:
        clip_object = fetcher.fetch_from_file(file_path)
        validation_result = validator.validate(clip_object)
        
        results.append({
            'file': file_path,
            'valid': validation_result['valid'],
            'completeness': validation_result['stats']['completeness'],
            'errors': len(validation_result['errors'])
        })
    except Exception as e:
        results.append({
            'file': file_path,
            'valid': False,
            'error': str(e)
        })

# Generate report
print(json.dumps(results, indent=2))
```

### Working with Different CLIP Types

```python
from clip_sdk import CLIPObject

# Venue CLIP
venue = CLIPObject(
    **{
        "@context": "https://clipprotocol.org/v1",
        "type": "Venue",
        "id": "clip:restaurant:example:123",
        "name": "Example Restaurant",
        "description": "Fine dining experience"
    }
)

venue.set_location(address="123 Food St")
venue.add_feature("Outdoor Seating", "facility", available=True)
venue.add_action("Make Reservation", "link", "https://restaurant.com/reserve")

# Device CLIP
device = CLIPObject(
    **{
        "@context": "https://clipprotocol.org/v1",
        "type": "Device", 
        "id": "clip:device:thermostat:456",
        "name": "Smart Thermostat",
        "description": "WiFi-enabled thermostat"
    }
)

device.add_feature("Temperature", "sensor", value=72.5)
device.add_action("Set Temperature", "api", "https://thermostat.com/api/set")
device.add_service("http", "https://thermostat.com/api")

# Software App CLIP
app = CLIPObject(
    **{
        "@context": "https://clipprotocol.org/v1", 
        "type": "SoftwareApp",
        "id": "clip:app:calendar:789",
        "name": "Calendar App",
        "description": "Personal calendar application"
    }
)

app.add_feature("Event Management", "capability")
app.add_action("Create Event", "api", "https://calendar.com/api/events")
app.add_service("mcp", "mcp://calendar.com/service")
```

## Utilities

The SDK includes several utility functions for common operations:

```python
from clip_sdk.utils import (
    generate_clip_id,
    is_valid_clip_id,
    is_valid_clip_type,
    create_minimal_clip_object,
    validate_clip_basic_structure,
    discover_clip_files
)

# Generate a CLIP ID
clip_id = generate_clip_id("venue", "restaurant", "cafe-123")
# Result: "clip:restaurant:venue:cafe-123"

# Validate ID format
if is_valid_clip_id("clip:example:venue:123"):
    print("Valid CLIP ID")

# Create minimal CLIP object
minimal_clip = create_minimal_clip_object(
    clip_type="Device",
    name="Test Device", 
    description="A test device"
)

# Basic structure validation
errors = validate_clip_basic_structure(clip_object)
if not errors:
    print("Basic structure is valid")

# Discover CLIP files
clip_files = discover_clip_files("./clips", recursive=True)
```

## Error Handling

The SDK provides specific exception types for different error scenarios:

```python
from clip_sdk import CLIPValidator, CLIPFetcher
from clip_sdk.validator import CLIPValidationError
from clip_sdk.fetcher import CLIPFetchError

try:
    validator = CLIPValidator()
    result = validator.validate(clip_object)
except CLIPValidationError as e:
    print(f"Validation error: {e}")
    if e.errors:
        for error in e.errors:
            print(f"  - {error}")

try:
    fetcher = CLIPFetcher()
    clip_object = fetcher.fetch_from_url("https://invalid-url.com/clip.json")
except CLIPFetchError as e:
    print(f"Fetch error: {e}")
```

## Testing

Run the test suite:

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=clip_sdk

# Run specific test file
pytest tests/test_validator.py
```

## Examples

The `examples/` directory contains comprehensive examples:

- `validate_example.py` - Validation examples
- `fetch_example.py` - Fetching and manipulation examples

Run examples:

```bash
python examples/validate_example.py
python examples/fetch_example.py
```

## API Reference

### CLIPValidator

| Method | Description |
|--------|-------------|
| `__init__(schema_url, schema_path, cache_schema, strict_mode)` | Initialize validator |
| `validate(clip_object)` | Validate CLIP object |
| `validate_file(file_path)` | Validate CLIP object from file |
| `validate_url(url)` | Validate CLIP object from URL |
| `load_schema()` | Load the CLIP schema |

### CLIPFetcher

| Method | Description |
|--------|-------------|
| `__init__(timeout, max_retries, cache_enabled, cache_dir)` | Initialize fetcher |
| `fetch(source)` | Fetch from file or URL (auto-detect) |
| `fetch_from_file(file_path)` | Fetch from local file |
| `fetch_from_url(url)` | Fetch from URL |
| `fetch_multiple(sources)` | Fetch multiple sources |
| `discover_from_directory(directory, recursive)` | Discover CLIP files |
| `get_failed_sources()` | Get list of failed sources |
| `clear_cache()` | Clear cached objects |

### CLIPObject

| Method | Description |
|--------|-------------|
| `from_dict(data)` | Create from dictionary |
| `from_json(json_str)` | Create from JSON string |
| `to_dict(by_alias, exclude_none)` | Convert to dictionary |
| `to_json(by_alias, exclude_none, indent)` | Convert to JSON |
| `add_feature(name, type, **kwargs)` | Add a feature |
| `add_action(label, type, endpoint, **kwargs)` | Add an action |
| `add_service(type, endpoint, **kwargs)` | Add a service |
| `set_location(address, coordinates, timezone)` | Set location |
| `set_persona(role, personality, expertise, prompt)` | Set persona |
| `get_statistics()` | Get object statistics |
| `validate_completeness()` | Check completeness |
| `update_timestamp()` | Update lastUpdated |
| `clone()` | Create a copy |
| `merge_with(other, prefer_other)` | Merge with another object |

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Run the test suite (`pytest`)
6. Commit your changes (`git commit -am 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## Development Setup

```bash
# Clone the repository
git clone https://github.com/clip-organization/clip-toolkit.git
cd clip-toolkit/packages/sdk-python

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run tests
pytest
```

## License

This project is licensed under the MIT License - see the [LICENSE](../../LICENSE) file for details.

## Related Projects

- [CLIP Specification](https://github.com/clip-organization/spec) - Official CLIP protocol specification
- [CLIP CLI Tool](../encoder-cli) - Command-line interface for CLIP objects
- [CLIP Validator Core](../validator-core) - TypeScript validation library

## Support

- 📖 [Documentation](../../docs)
- 🐛 [Issues](../../issues)
- 💬 [Discussions](../../discussions)
- 📧 [Email Support](mailto:support@clipprotocol.org) 