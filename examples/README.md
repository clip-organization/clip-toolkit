# CLIP Toolkit Examples

This directory contains comprehensive examples demonstrating how to use all components of the CLIP Toolkit. Each example is designed to be practical and educational, showing real-world usage patterns.

## 📁 Directory Structure

```
examples/
├── encoder-cli/          # CLI tool examples
├── python-sdk/          # Python SDK examples
├── validator-core/      # TypeScript validator examples
├── decoder-lib/         # Visual encoding/decoding examples
├── integration/         # Cross-package integration examples
├── sample-clips/        # Sample CLIP objects for testing
└── README.md           # This file
```

## 🚀 Quick Start

### Prerequisites

```bash
# Install CLI tool globally
npm install -g @clip/encoder-cli

# Install Python SDK
pip install clip-sdk

# Clone repository for development examples
git clone https://github.com/your-org/clip-toolkit.git
cd clip-toolkit
npm install
```

### Running Examples

Each subdirectory contains its own README with specific instructions. Here's a quick overview:

```bash
# CLI examples
cd examples/encoder-cli
./validate-example.sh

# Python examples
cd examples/python-sdk
python validate_example.py

# Integration examples
cd examples/integration
python cli_python_integration.py
```

## 📋 Example Categories

### 1. Basic Usage Examples

**Encoder CLI**
- [Basic validation](./encoder-cli/basic-validation.sh)
- [Template generation](./encoder-cli/template-generation.sh)
- [Statistics analysis](./encoder-cli/statistics-analysis.sh)

**Python SDK**
- [Simple validation](./python-sdk/simple_validation.py)
- [Remote fetching](./python-sdk/remote_fetching.py)
- [Object manipulation](./python-sdk/object_manipulation.py)

### 2. Advanced Usage Examples

**Batch Processing**
- [CLI batch validation](./encoder-cli/batch-processing.sh)
- [Python batch operations](./python-sdk/batch_processing.py)

**Custom Validation**
- [Custom CLI rules](./encoder-cli/custom-validation.js)
- [Python custom validators](./python-sdk/custom_validation.py)

**Error Handling**
- [Robust error handling](./python-sdk/error_handling.py)
- [CLI error scenarios](./encoder-cli/error-handling.sh)

### 3. Integration Examples

**Web Applications**
- [FastAPI integration](./integration/fastapi_example.py)
- [Express.js integration](./integration/express_example.js)
- [Django integration](./integration/django_example.py)

**CI/CD Integration**
- [GitHub Actions workflow](./integration/github-actions.yml)
- [Jenkins pipeline](./integration/Jenkinsfile)
- [Docker examples](./integration/docker/)

### 4. Performance Examples

**Optimization**
- [High-performance validation](./python-sdk/performance_optimization.py)
- [Memory-efficient processing](./python-sdk/memory_efficient.py)
- [Concurrent operations](./python-sdk/concurrent_processing.py)

**Benchmarking**
- [Performance benchmarks](./python-sdk/benchmarks.py)
- [Load testing](./integration/load_testing.py)

## 🎯 Use Case Examples

### E-commerce Integration

```python
# examples/use-cases/ecommerce.py
from clip_sdk import CLIPValidator, CLIPObject

def validate_product_clip(product_data):
    """Validate e-commerce product CLIP"""
    validator = CLIPValidator()
    result = validator.validate(product_data)
    
    if result.is_valid:
        clip = CLIPObject(product_data)
        return {
            'valid': True,
            'product_name': clip.get_name(),
            'features': len(clip.get_features()),
            'completeness': clip.get_statistics().completeness
        }
    else:
        return {
            'valid': False,
            'errors': [error.message for error in result.errors]
        }
```

### Event Management

```bash
# examples/use-cases/events.sh
#!/bin/bash

# Generate event template
clip generate --type event --output event-template.json

# Validate event CLIP
clip validate event.json --verbose

# Get event statistics
clip stats event.json --detailed
```

### Venue Management

```python
# examples/use-cases/venues.py
from clip_sdk import CLIPFetcher, CLIPObject

def process_venue_clips(venue_urls):
    """Process multiple venue CLIPs"""
    fetcher = CLIPFetcher(cache_enabled=True)
    results = []
    
    for url in venue_urls:
        try:
            clip_data = fetcher.fetch(url)
            venue = CLIPObject(clip_data)
            
            results.append({
                'url': url,
                'name': venue.get_name(),
                'location': venue.has_location(),
                'features': len(venue.get_features())
            })
        except Exception as e:
            results.append({
                'url': url,
                'error': str(e)
            })
    
    return results
```

## 🔧 Development Examples

### Custom Validation Rules

```javascript
// examples/development/custom-rules.js
module.exports = {
  rules: [
    {
      name: 'venue-hours',
      description: 'Venues should include operating hours',
      applies: (clip) => clip.type === 'venue',
      validate: (clip) => {
        if (!clip.hours || !clip.hours.open) {
          return {
            valid: false,
            message: 'Venues should include operating hours',
            suggestion: 'Add hours.open and hours.close fields'
          };
        }
        return { valid: true };
      }
    }
  ]
};
```

### Testing Utilities

```python
# examples/development/test_utilities.py
import pytest
from clip_sdk import CLIPValidator, CLIPObject

class CLIPTestHelper:
    """Helper class for testing CLIP objects"""
    
    def __init__(self):
        self.validator = CLIPValidator()
    
    def create_test_venue(self, name="Test Venue"):
        """Create a valid test venue CLIP"""
        return {
            'type': 'venue',
            'version': '1.0.0',
            'name': name,
            'description': f'A test venue named {name}',
            'location': {
                'coordinates': {
                    'latitude': 40.7589,
                    'longitude': -73.9851
                }
            }
        }
    
    def assert_valid_clip(self, clip_data):
        """Assert that a CLIP object is valid"""
        result = self.validator.validate(clip_data)
        assert result.is_valid, f"CLIP validation failed: {result.errors}"
        return CLIPObject(clip_data)
```

## 📊 Sample Data

The `sample-clips/` directory contains various CLIP objects for testing:

### Basic Examples
- `venue-basic.json` - Simple venue CLIP
- `event-basic.json` - Simple event CLIP
- `product-basic.json` - Simple product CLIP

### Complex Examples
- `venue-complex.json` - Venue with all optional fields
- `event-complex.json` - Event with multiple features
- `product-complex.json` - Product with rich metadata

### Edge Cases
- `minimal-clip.json` - Minimal valid CLIP
- `invalid-clips/` - Various invalid CLIPs for error testing

### Real-world Examples
- `restaurant.json` - Real restaurant CLIP
- `conference.json` - Conference event CLIP
- `smartphone.json` - Product CLIP for smartphone

## 🧪 Testing Examples

### Unit Testing

```python
# examples/testing/test_clip_validation.py
import pytest
from clip_sdk import CLIPValidator

class TestCLIPValidation:
    def setup_method(self):
        self.validator = CLIPValidator()
    
    def test_valid_venue(self):
        venue_data = {
            'type': 'venue',
            'version': '1.0.0',
            'name': 'Test Venue'
        }
        result = self.validator.validate(venue_data)
        assert result.is_valid
    
    def test_invalid_venue(self):
        invalid_data = {'type': 'venue'}  # Missing version
        result = self.validator.validate(invalid_data)
        assert not result.is_valid
        assert any('version' in error.path for error in result.errors)
```

### Integration Testing

```bash
#!/bin/bash
# examples/testing/integration-test.sh

echo "Running integration tests..."

# Test CLI validation
echo "Testing CLI validation..."
clip validate examples/sample-clips/venue-basic.json
if [ $? -eq 0 ]; then
    echo "✅ CLI validation passed"
else
    echo "❌ CLI validation failed"
    exit 1
fi

# Test Python SDK
echo "Testing Python SDK..."
python -c "
from clip_sdk import CLIPValidator
import json

with open('examples/sample-clips/venue-basic.json') as f:
    data = json.load(f)

validator = CLIPValidator()
result = validator.validate(data)
assert result.is_valid, 'Python validation failed'
print('✅ Python SDK validation passed')
"

echo "All integration tests passed!"
```

## 🔗 External Integration Examples

### GitHub Actions

```yaml
# examples/ci-cd/github-actions.yml
name: CLIP Validation
on: [push, pull_request]

jobs:
  validate-clips:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install CLI
        run: npm install -g @clip/encoder-cli
      
      - name: Validate CLIP files
        run: |
          find . -name "*.json" -path "./clips/*" | while read file; do
            echo "Validating $file"
            clip validate "$file" || exit 1
          done
```

### Docker Integration

```dockerfile
# examples/docker/Dockerfile
FROM node:18-alpine

# Install CLI tool
RUN npm install -g @clip/encoder-cli

# Install Python and SDK
RUN apk add --no-cache python3 py3-pip
RUN pip3 install clip-sdk

# Copy validation scripts
COPY validate-clips.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/validate-clips.sh

ENTRYPOINT ["validate-clips.sh"]
```

## 📖 Learning Path

### Beginner
1. Start with [Basic CLI Usage](./encoder-cli/basic-usage.sh)
2. Try [Simple Python Validation](./python-sdk/simple_validation.py)
3. Explore [Sample CLIP Objects](./sample-clips/)

### Intermediate
1. Learn [Batch Processing](./python-sdk/batch_processing.py)
2. Implement [Custom Validation](./python-sdk/custom_validation.py)
3. Try [Web Integration](./integration/fastapi_example.py)

### Advanced
1. Study [Performance Optimization](./python-sdk/performance_optimization.py)
2. Build [Custom Tools](./development/custom_tools.py)
3. Contribute to [Open Source](../CONTRIBUTING.md)

## 🆘 Getting Help

If you have questions about any examples:

1. **Check the README** in each subdirectory
2. **Run the examples** to see them in action
3. **Read the comments** in the code
4. **Open an issue** if something doesn't work
5. **Join discussions** in the GitHub repository

## 📄 License

All examples are provided under the MIT License. Feel free to use them in your own projects.

---

**Happy coding with CLIP Toolkit! 🚀** 