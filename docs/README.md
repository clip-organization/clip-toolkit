# CLIP Toolkit Documentation

Welcome to the comprehensive documentation for CLIP Toolkit - a collection of SDKs, validation tools, and utilities for working with the Context Link Interface Protocol (CLIP).

## 📚 Table of Contents

- [Getting Started](#getting-started)
- [API Reference](#api-reference)
- [Examples](#examples)
- [Development](#development)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)

## 🚀 Getting Started

### What is CLIP?

CLIP (Context Link Interface Protocol) is a standardized format for describing linkable content and contexts. CLIP objects provide a structured way to:

- Link physical and digital content
- Provide contextual metadata
- Enable cross-platform interoperability
- Support various encoding formats (JSON, QR codes, etc.)

### Installation Guides

#### CLI Tool
```bash
npm install -g @clip/encoder-cli
clip --help
```

#### Python SDK
```bash
pip install clip-sdk
```

```python
from clip_sdk import CLIPValidator
validator = CLIPValidator()
```

### First Steps

1. **[Validate your first CLIP](./guides/validation.md)** - Learn basic validation
2. **[Generate CLIP templates](./guides/generation.md)** - Create new CLIP objects
3. **[Fetch remote CLIPs](./guides/fetching.md)** - Work with URLs
4. **[Batch processing](./guides/batch.md)** - Handle multiple files

## 📖 API Reference

### Command-Line Interface

- **[CLI Commands](./api/cli/README.md)** - Complete command reference
  - [`clip validate`](./api/cli/validate.md) - Validate CLIP objects
  - [`clip generate`](./api/cli/generate.md) - Generate CLIP templates
  - [`clip stats`](./api/cli/stats.md) - Analyze CLIP statistics

### Python SDK

- **[Python API](./api/python/README.md)** - Complete Python reference
  - [`CLIPValidator`](./api/python/validator.md) - Validation functionality
  - [`CLIPFetcher`](./api/python/fetcher.md) - Remote fetching with caching
  - [`CLIPObject`](./api/python/object.md) - CLIP object manipulation
  - [`CLIPUtils`](./api/python/utils.md) - Utility functions

### TypeScript/JavaScript

- **[TypeScript API](./api/typescript/README.md)** - Complete TypeScript reference
  - [Validator Core](./api/typescript/validator.md) - Core validation logic
  - [CLI Implementation](./api/typescript/cli.md) - CLI tool internals
  - [Decoder Library](./api/typescript/decoder.md) - Visual encoding/decoding

## 💡 Examples

### Basic Usage

#### Validate a CLIP File
```bash
# CLI
clip validate my-clip.json

# Python
python -c "
from clip_sdk import CLIPValidator
import json

with open('my-clip.json') as f:
    result = CLIPValidator().validate(json.load(f))
    print('Valid!' if result.is_valid else f'Errors: {result.errors}')
"
```

#### Generate Templates
```bash
# CLI - Generate venue template
clip generate --type venue

# CLI - Generate event template  
clip generate --type event --output event.json
```

#### Fetch Remote CLIPs
```python
from clip_sdk import CLIPFetcher

fetcher = CLIPFetcher()
clip = fetcher.fetch('https://example.com/venue.json')
print(f"Name: {clip.data.get('name', 'Unknown')}")
print(f"Type: {clip.get_type()}")
```

### Advanced Examples

- **[Batch Processing](./examples/batch-processing.md)** - Handle multiple files
- **[Custom Validation](./examples/custom-validation.md)** - Add custom rules
- **[Error Handling](./examples/error-handling.md)** - Robust error management
- **[Performance Optimization](./examples/performance.md)** - Tips for large datasets
- **[Integration Patterns](./examples/integration.md)** - Common integration scenarios

## 🛠️ Development

### Architecture Overview

```
CLIP Toolkit Architecture
┌─────────────────────────────────────────────────────────────┐
│                     User Interface                          │
├─────────────────────┬───────────────────┬───────────────────┤
│     CLI Tool        │    Python SDK     │   Future: Web UI  │
│   (TypeScript)      │    (Python)       │   (React/Vue)     │
├─────────────────────┼───────────────────┼───────────────────┤
│                   Core Libraries                           │
├─────────────────────┬───────────────────┬───────────────────┤
│  Validator Core     │   Decoder Lib     │    Utilities      │
│  (TypeScript)       │ (TS + Python)     │   (Shared)        │
├─────────────────────┴───────────────────┴───────────────────┤
│                    CLIP Protocol                           │
│              (JSON Schema + Spec)                         │
└─────────────────────────────────────────────────────────────┘
```

### Development Guides

- **[Setting up Development Environment](./development/setup.md)**
- **[Contributing Guidelines](./development/contributing.md)**
- **[Testing Strategy](./development/testing.md)**
- **[Release Process](./development/releases.md)**
- **[Code Style Guide](./development/style.md)**

### Package Development

Each package can be developed independently:

#### TypeScript Packages
```bash
cd packages/encoder-cli
npm run dev        # Development mode
npm run build      # Production build
npm test          # Run tests
npm run lint      # Check code style
```

#### Python Packages
```bash
cd packages/sdk-python
pip install -e ".[dev]"    # Development install
pytest                     # Run tests
black .                   # Format code
mypy clip_sdk             # Type checking
```

## 🚀 Deployment

### CI/CD Pipeline

Our enterprise-grade CI/CD system provides:

- **Multi-platform testing** (Ubuntu, Windows, macOS)
- **Multi-version support** (Node.js 18-21, Python 3.8-3.12)
- **Comprehensive security scanning**
- **Automated publishing** to npm and PyPI
- **Code coverage reporting**
- **Dependency vulnerability checking**

#### Workflow Files
- [TypeScript CI](./.github/workflows/typescript-ci.yml)
- [Python CI](./.github/workflows/python-ci.yml) 
- [Publishing](./.github/workflows/publish.yml)

#### Setting Up Secrets

Required repository secrets:
```
NPM_TOKEN         # npm publishing token
PYPI_API_TOKEN    # PyPI publishing token
CODECOV_TOKEN     # Code coverage reporting
```

### Production Deployment

#### Publishing Process
1. **Version Bump**: Update version numbers
2. **Testing**: All CI checks must pass
3. **Security Scan**: No high/critical vulnerabilities
4. **Manual Approval**: Required for production releases
5. **Dual Publishing**: npm + PyPI simultaneously

#### Monitoring
- **Code Coverage**: [Codecov integration](https://codecov.io)
- **Security**: Automated vulnerability scanning
- **Performance**: Benchmark tracking in CI

## 🔧 Troubleshooting

### Common Issues

#### Installation Problems

**Node.js Version Issues**
```bash
# Check Node.js version
node --version  # Should be 18+

# Update Node.js
nvm install node    # If using nvm
```

**Python Dependencies**
```bash
# Clear pip cache
pip cache purge

# Reinstall dependencies
pip install --force-reinstall clip-sdk
```

#### Validation Errors

**Schema Validation Failures**
```python
from clip_sdk import CLIPValidator

validator = CLIPValidator()
result = validator.validate(clip_data)

if not result.is_valid:
    print("Validation errors:")
    for error in result.errors:
        print(f"  Path: {error.path}")
        print(f"  Message: {error.message}")
        print(f"  Value: {error.value}")
```

**Remote Fetch Issues**
```python
from clip_sdk import CLIPFetcher
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

fetcher = CLIPFetcher(
    timeout=30,         # Increase timeout
    retries=5,          # More retry attempts
    cache_enabled=True  # Enable caching
)
```

#### Performance Issues

**Large File Processing**
```bash
# Use streaming for large files
clip validate --stream large-file.json

# Batch processing with progress
clip validate *.json --progress
```

### Debug Mode

Enable debug output for troubleshooting:

```bash
# CLI debug mode
DEBUG=clip:* clip validate file.json

# Python debug logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Getting Help

1. **Check the FAQ**: [Frequently Asked Questions](./faq.md)
2. **Search Issues**: [GitHub Issues](https://github.com/clip-organization/clip-toolkit/issues)
3. **Community Discussion**: [GitHub Discussions](https://github.com/clip-organization/clip-toolkit/discussions)
4. **Report Bug**: [New Issue](https://github.com/clip-organization/clip-toolkit/issues/new)

## 🔗 External Resources

- **[CLIP Specification](https://github.com/clip-organization/spec)** - Official protocol specification
- **[JSON Schema](https://json-schema.org/)** - Schema validation standard
- **[TypeScript Handbook](https://www.typescriptlang.org/docs/)** - TypeScript documentation
- **[Python Packaging Guide](https://packaging.python.org/)** - Python package development

---

**Last Updated**: December 2024  
**Version**: 1.0.0  
**Maintainers**: CLIP Toolkit Team 
