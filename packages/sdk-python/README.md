# CLIP Python SDK

A comprehensive Python library for working with CLIP (Context Link Interface Protocol) objects. Provides validation, fetching, manipulation, and analysis capabilities with full type safety and modern Python features.

[![PyPI version](https://badge.fury.io/py/clip-sdk.svg)](https://badge.fury.io/py/clip-sdk)
[![Python CI](https://github.com/clip-organization/clip-toolkit/workflows/Python%20CI/badge.svg)](https://github.com/clip-organization/clip-toolkit/actions)
[![codecov](https://codecov.io/gh/clip-organization/clip-toolkit/branch/main/graph/badge.svg)](https://codecov.io/gh/clip-organization/clip-toolkit)

## Features

- 🔍 **Schema Validation** - Validate CLIP objects against the official schema
- 📥 **Multi-source Fetching** - Load CLIP objects from files, URLs, and directories  
- 🏗️ **Object Modeling** - Rich Pydantic models for type-safe CLIP object manipulation
- 📊 **Statistics & Analysis** - Comprehensive analysis of CLIP object completeness and structure
- 🚀 **High Performance** - Efficient caching and batch operations
- 🛡️ **Type Safety** - Full TypeScript-style type hints and validation
- 🔧 **Extensible** - Easy to extend and customize for specific use cases

## 🚀 Quick Start

### Installation

```bash
# Install from PyPI
pip install clip-sdk

# Or install with optional dependencies
pip install clip-sdk[all]  # Includes async, caching, and development tools
```

### Basic Usage

```python
from clip_sdk import CLIPValidator, CLIPFetcher, CLIPObject

# Validate a CLIP object
validator = CLIPValidator()
result = validator.validate(clip_data)
print(f"Valid: {result.is_valid}")

# Fetch a CLIP from URL
fetcher = CLIPFetcher()
clip = fetcher.fetch('https://example.com/venue.json')
print(f"Type: {clip.get_type()}")

# Work with CLIP objects
clip_obj = CLIPObject(clip_data)
features = clip_obj.get_features()
statistics = clip_obj.get_statistics()
```

## 📦 Core Components

### CLIPValidator

Comprehensive validation with detailed error reporting:

```python
from clip_sdk import CLIPValidator, ValidationOptions

validator = CLIPValidator(
    strict_mode=True,
    schema_version="1.0.0"
)

# Validate with detailed results
result = validator.validate(clip_data)

if result.is_valid:
    print("✅ CLIP is valid!")
    print(f"Score: {result.score}/100")
else:
    print("❌ Validation errors:")
    for error in result.errors:
        print(f"  Path: {error.path}")
        print(f"  Message: {error.message}")
        print(f"  Severity: {error.severity}")

# Validate multiple objects
results = validator.validate_batch([clip1, clip2, clip3])
```

### CLIPFetcher

Remote CLIP fetching with caching and retry logic:

```python
from clip_sdk import CLIPFetcher, FetchOptions
import asyncio

# Configure fetcher
fetcher = CLIPFetcher(
    timeout=30,
    retries=3,
    cache_enabled=True,
    cache_ttl=3600  # 1 hour
)

# Fetch single CLIP
clip = fetcher.fetch('https://example.com/venue.json')

# Batch fetching
urls = [
    'https://example.com/venue1.json',
    'https://example.com/venue2.json',
    'https://example.com/venue3.json'
]
clips = fetcher.fetch_batch(urls)

# Async fetching (with async extra)
async def fetch_async():
    clips = await fetcher.fetch_async(urls)
    return clips

# Error handling
try:
    clip = fetcher.fetch('https://invalid-url.com/clip.json')
except CLIPFetchError as e:
    print(f"Fetch failed: {e.message}")
    print(f"Status code: {e.status_code}")
```

### CLIPObject

Type-safe CLIP object manipulation:

```python
from clip_sdk import CLIPObject
from datetime import datetime

# Create from data
clip = CLIPObject(clip_data)

# Basic properties
print(f"Type: {clip.get_type()}")
print(f"Version: {clip.get_version()}")
print(f"Name: {clip.get_name()}")
print(f"Description: {clip.get_description()}")

# Features analysis
features = clip.get_features()
print(f"Features count: {len(features)}")
for feature in features:
    print(f"  - {feature.name}: {feature.type}")

# Links and URLs
links = clip.get_links()
primary_url = clip.get_primary_url()

# Location data (if available)
if clip.has_location():
    location = clip.get_location()
    coords = location.get_coordinates()
    print(f"Location: {coords.latitude}, {coords.longitude}")

# Metadata
metadata = clip.get_metadata()
created = metadata.get('created')
updated = metadata.get('updated')

# Statistics
stats = clip.get_statistics()
print(f"Content completeness: {stats.completeness}%")
print(f"Structure complexity: {stats.complexity}")
print(f"Validation score: {stats.validation_score}")

# Modification
clip.set_name("Updated Name")
clip.set_description("New description")
clip.add_feature("wifi", "connectivity", available=True)
clip.update_metadata({"updated": datetime.now().isoformat()})

# Export
json_data = clip.to_dict()
json_string = clip.to_json(indent=2)
```

## 🔧 Advanced Features

### Custom Validation Rules

```python
from clip_sdk import CLIPValidator, ValidationRule

# Define custom rule
def venue_coordinates_rule(clip_data: dict) -> ValidationResult:
    """Ensure venues have valid coordinates"""
    if clip_data.get('type') != 'venue':
        return ValidationResult(valid=True)  # Skip non-venues
    
    location = clip_data.get('location', {})
    coords = location.get('coordinates', {})
    
    if not coords:
        return ValidationResult(
            valid=False,
            message="Venues must include coordinates",
            severity="error"
        )
    
    lat, lng = coords.get('latitude'), coords.get('longitude')
    if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
        return ValidationResult(
            valid=False,
            message="Invalid coordinate values",
            severity="error"
        )
    
    return ValidationResult(valid=True)

# Register custom rule
validator = CLIPValidator()
validator.add_rule(venue_coordinates_rule)

# Validate with custom rules
result = validator.validate(venue_data)
```

### Batch Processing

```python
from clip_sdk import CLIPProcessor
import json
from pathlib import Path

processor = CLIPProcessor()

# Process directory of CLIP files
def process_directory(directory: Path):
    clips = []
    for file_path in directory.glob("*.json"):
        with open(file_path) as f:
            clip_data = json.load(f)
            
        # Validate
        result = processor.validate(clip_data)
        if not result.is_valid:
            print(f"Invalid CLIP: {file_path}")
            continue
            
        # Process
        clip = CLIPObject(clip_data)
        clips.append(clip)
    
    return clips

# Batch statistics
clips = process_directory(Path("./clip-files"))
batch_stats = processor.analyze_batch(clips)

print(f"Total clips: {batch_stats.total}")
print(f"Valid clips: {batch_stats.valid}")
print(f"Average score: {batch_stats.average_score}")
print(f"Most common type: {batch_stats.most_common_type}")
```

### Caching Configuration

```python
from clip_sdk import CLIPFetcher, CacheConfig
import redis

# Memory cache (default)
fetcher = CLIPFetcher(cache_enabled=True)

# Redis cache
cache_config = CacheConfig(
    backend='redis',
    host='localhost',
    port=6379,
    db=0,
    ttl=3600
)
fetcher = CLIPFetcher(cache_config=cache_config)

# File-based cache
cache_config = CacheConfig(
    backend='file',
    directory='/tmp/clip-cache',
    ttl=3600
)
fetcher = CLIPFetcher(cache_config=cache_config)

# Custom cache backend
class CustomCache:
    def get(self, key: str) -> Optional[dict]:
        # Custom get logic
        pass
    
    def set(self, key: str, value: dict, ttl: int) -> None:
        # Custom set logic
        pass

fetcher = CLIPFetcher(cache=CustomCache())
```

## 🧪 Testing and Development

### Running Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run with coverage
pytest --cov=clip_sdk

# Run specific test categories
pytest tests/test_validation.py
pytest tests/test_fetching.py
pytest tests/test_objects.py

# Run performance tests
pytest tests/test_performance.py -v
```

### Code Quality

```bash
# Format code
black clip_sdk tests

# Sort imports
isort clip_sdk tests

# Type checking
mypy clip_sdk

# Linting
flake8 clip_sdk

# Security scanning
bandit -r clip_sdk
```

### Example Test

```python
import pytest
from clip_sdk import CLIPValidator, CLIPObject

def test_venue_validation():
    """Test venue CLIP validation"""
    venue_data = {
        "type": "venue",
        "version": "1.0.0",
        "name": "Test Venue",
        "location": {
            "coordinates": {
                "latitude": 40.7589,
                "longitude": -73.9851
            }
        }
    }
    
    validator = CLIPValidator()
    result = validator.validate(venue_data)
    
    assert result.is_valid
    assert result.score > 80
    
    clip = CLIPObject(venue_data)
    assert clip.get_type() == "venue"
    assert clip.has_location()

@pytest.mark.asyncio
async def test_async_fetching():
    """Test async CLIP fetching"""
    from clip_sdk import CLIPFetcher
    
    fetcher = CLIPFetcher()
    clips = await fetcher.fetch_async([
        'https://example.com/venue1.json',
        'https://example.com/venue2.json'
    ])
    
    assert len(clips) == 2
    for clip in clips:
        assert clip.get_type() in ['venue', 'event', 'product']
```

## 📊 Performance and Benchmarks

### Benchmarks

The SDK is optimized for performance:

- **Validation**: ~2000 objects/second (typical CLIP objects)
- **Fetching**: ~100 concurrent requests (with proper rate limiting)
- **Object manipulation**: ~10,000 operations/second
- **Batch processing**: Linear scaling with object count

### Performance Tips

```python
# Use batch operations when possible
validator = CLIPValidator()
results = validator.validate_batch(clip_objects)  # Faster than individual calls

# Enable caching for repeated fetches
fetcher = CLIPFetcher(cache_enabled=True, cache_ttl=3600)

# Use streaming for large datasets
def process_large_dataset(file_paths):
    for path in file_paths:
        with open(path) as f:
            clip_data = json.load(f)
            yield CLIPObject(clip_data)

# Async processing for I/O bound operations
async def fetch_many_clips(urls):
    fetcher = CLIPFetcher()
    tasks = [fetcher.fetch_async(url) for url in urls]
    return await asyncio.gather(*tasks)
```

## 🔌 Integration Examples

### FastAPI Integration

```python
from fastapi import FastAPI, HTTPException
from clip_sdk import CLIPValidator, CLIPObject
from pydantic import BaseModel

app = FastAPI()
validator = CLIPValidator()

class CLIPData(BaseModel):
    data: dict

@app.post("/validate")
async def validate_clip(clip_data: CLIPData):
    result = validator.validate(clip_data.data)
    return {
        "valid": result.is_valid,
        "score": result.score,
        "errors": [{"path": e.path, "message": e.message} for e in result.errors]
    }

@app.post("/analyze")
async def analyze_clip(clip_data: CLIPData):
    if not validator.validate(clip_data.data).is_valid:
        raise HTTPException(400, "Invalid CLIP object")
    
    clip = CLIPObject(clip_data.data)
    return {
        "type": clip.get_type(),
        "features": len(clip.get_features()),
        "statistics": clip.get_statistics()
    }
```

### Django Integration

```python
# models.py
from django.db import models
from clip_sdk import CLIPValidator, CLIPObject
import json

class CLIPRecord(models.Model):
    name = models.CharField(max_length=200)
    data = models.JSONField()
    is_valid = models.BooleanField(default=False)
    clip_type = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        # Validate on save
        validator = CLIPValidator()
        result = validator.validate(self.data)
        self.is_valid = result.is_valid
        
        if self.is_valid:
            clip = CLIPObject(self.data)
            self.clip_type = clip.get_type()
        
        super().save(*args, **kwargs)

# views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from clip_sdk import CLIPFetcher

@csrf_exempt
def fetch_and_store(request):
    url = request.POST.get('url')
    
    fetcher = CLIPFetcher()
    try:
        clip_data = fetcher.fetch(url)
        record = CLIPRecord.objects.create(
            name=f"Fetched from {url}",
            data=clip_data
        )
        return JsonResponse({"success": True, "id": record.id})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})
```

### Jupyter Notebook Usage

```python
# Install in notebook
!pip install clip-sdk

from clip_sdk import CLIPValidator, CLIPFetcher, CLIPObject
import pandas as pd
import matplotlib.pyplot as plt

# Fetch and analyze multiple CLIPs
urls = [
    'https://example.com/venue1.json',
    'https://example.com/venue2.json',
    'https://example.com/venue3.json'
]

fetcher = CLIPFetcher()
clips = [CLIPObject(fetcher.fetch(url)) for url in urls]

# Create analysis DataFrame
data = []
for clip in clips:
    stats = clip.get_statistics()
    data.append({
        'name': clip.get_name(),
        'type': clip.get_type(),
        'features': len(clip.get_features()),
        'completeness': stats.completeness,
        'score': stats.validation_score
    })

df = pd.DataFrame(data)

# Visualize
plt.figure(figsize=(10, 6))
plt.scatter(df['features'], df['completeness'])
plt.xlabel('Number of Features')
plt.ylabel('Completeness %')
plt.title('CLIP Feature vs Completeness Analysis')
plt.show()
```

## 🔧 Configuration

### Environment Variables

```bash
# Default schema URL
export CLIP_SCHEMA_URL="https://schema.clipprotocol.org/v1/clip.schema.json"

# Cache configuration
export CLIP_CACHE_ENABLED=true
export CLIP_CACHE_TTL=3600
export CLIP_CACHE_DIR="/tmp/clip-cache"

# Fetcher defaults
export CLIP_TIMEOUT=30
export CLIP_RETRIES=3
export CLIP_USER_AGENT="clip-sdk-python/1.0.0"

# Logging
export CLIP_LOG_LEVEL=INFO
```

### Configuration File

Create `~/.cliprc.yaml`:

```yaml
validation:
  strict_mode: false
  schema_version: "1.0.0"
  custom_rules_dir: "~/.clip/rules"

fetching:
  timeout: 30
  retries: 3
  cache_enabled: true
  cache_ttl: 3600
  user_agent: "clip-sdk-python/1.0.0"

logging:
  level: INFO
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

## 🐛 Troubleshooting

### Common Issues

**Import Errors**
```python
# Ensure proper installation
import sys
print(sys.path)

# Reinstall if needed
pip uninstall clip-sdk
pip install clip-sdk
```

**Validation Failures**
```python
from clip_sdk import CLIPValidator
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

validator = CLIPValidator()
result = validator.validate(clip_data)

if not result.is_valid:
    for error in result.errors:
        print(f"Error at {error.path}: {error.message}")
        print(f"Current value: {error.value}")
        print(f"Expected: {error.expected}")
```

**Network Issues**
```python
from clip_sdk import CLIPFetcher
import requests

# Test connectivity
try:
    response = requests.get('https://httpbin.org/status/200', timeout=10)
    print(f"Network OK: {response.status_code}")
except Exception as e:
    print(f"Network issue: {e}")

# Configure fetcher for slow networks
fetcher = CLIPFetcher(
    timeout=60,  # Increase timeout
    retries=5,   # More retries
    backoff_factor=2.0  # Exponential backoff
)
```

## 📚 API Reference

### Complete API Documentation

For detailed API documentation, see:

- **[CLIPValidator API](../../docs/api/python/validator.md)**
- **[CLIPFetcher API](../../docs/api/python/fetcher.md)**
- **[CLIPObject API](../../docs/api/python/object.md)**
- **[Utilities API](../../docs/api/python/utils.md)**

### Quick Reference

```python
# Core classes
from clip_sdk import (
    CLIPValidator,      # Validation functionality
    CLIPFetcher,       # Remote fetching with caching
    CLIPObject,        # CLIP object manipulation
    CLIPProcessor,     # Batch processing utilities
)

# Configuration classes
from clip_sdk import (
    ValidationOptions, # Validation configuration
    FetchOptions,     # Fetching configuration
    CacheConfig,      # Cache configuration
)

# Result classes
from clip_sdk import (
    ValidationResult, # Validation results
    ValidationError,  # Individual validation errors
    FetchResult,     # Fetch operation results
    Statistics,      # Object statistics
)

# Exceptions
from clip_sdk.exceptions import (
    CLIPError,           # Base exception
    CLIPValidationError, # Validation failures
    CLIPFetchError,     # Fetch failures
    CLIPCacheError,     # Cache failures
)
```

## 🔗 Related

- **[Encoder CLI](../encoder-cli/README.md)** - Command-line tool for CLIP validation
- **[Validator Core](../validator-core/README.md)** - Core validation logic (TypeScript)
- **[Decoder Library](../decoder-python/README.md)** - Visual encoding/decoding (Python)

## 📄 License

MIT License - see [LICENSE](../../LICENSE) for details.

---

**Part of the [CLIP Toolkit](../../README.md) ecosystem** 
