# CLIP Encoder CLI

A powerful command-line tool for validating, generating, and analyzing CLIP (Context Link Interface Protocol) objects. Built with TypeScript and designed for developers working with CLIP objects.

[![npm version](https://badge.fury.io/js/%40clip%2Fencoder-cli.svg)](https://badge.fury.io/js/%40clip%2Fencoder-cli)
[![Node.js CI](https://github.com/clip-organization/clip-toolkit/workflows/TypeScript%20CI/badge.svg)](https://github.com/clip-organization/clip-toolkit/actions)

## 🚀 Quick Start

### Installation

```bash
# Install globally
npm install -g @clip/encoder-cli

# Or run directly with npx
npx @clip/encoder-cli --help
```

### Basic Usage

```bash
# Validate a CLIP file
clip validate my-clip.json

# Generate a CLIP template
clip generate --type venue

# Get statistics about a CLIP
clip stats my-clip.json
```

## 📋 Commands

### `clip validate`

Validate CLIP objects against the JSON schema and custom rules.

#### Usage
```bash
clip validate <file> [options]
clip validate <url> [options]
clip validate *.json [options]
```

#### Options
- `--verbose, -v` - Show detailed validation output
- `--format <format>` - Output format: `json`, `table`, `minimal` (default: `table`)
- `--schema <file>` - Custom schema file to use
- `--rules <file>` - Custom validation rules file
- `--strict` - Enable strict validation mode
- `--allow-remote` - Allow validation of remote URLs

#### Examples
```bash
# Basic validation
clip validate venue.json

# Validate with verbose output
clip validate venue.json --verbose

# Validate from URL
clip validate https://example.com/clip.json --allow-remote

# Batch validation
clip validate *.json --format json

# Custom schema validation
clip validate venue.json --schema custom-schema.json
```

#### Output
```bash
✅ venue.json is valid
   Type: venue
   Version: 1.0.0
   Features: 5 detected
   
❌ invalid.json has errors:
   - Missing required property 'type' at root
   - Invalid format for 'url' at /links/0/url
```

### `clip generate`

Generate CLIP object templates for different types.

#### Usage
```bash
clip generate [options]
```

#### Options
- `--type <type>` - CLIP type: `venue`, `event`, `product`, `article`, `person`, `organization`
- `--output <file>` - Output file (default: stdout)
- `--minimal` - Generate minimal template
- `--example` - Include example data
- `--schema-version <version>` - Schema version to use (default: latest)

#### Examples
```bash
# Generate venue template
clip generate --type venue

# Generate with example data
clip generate --type venue --example

# Save to file
clip generate --type event --output event-template.json

# Minimal template
clip generate --type product --minimal
```

#### Sample Output
```json
{
  "type": "venue",
  "version": "1.0.0",
  "name": "",
  "description": "",
  "url": "",
  "location": {
    "address": "",
    "coordinates": {
      "latitude": 0,
      "longitude": 0
    }
  },
  "features": [],
  "links": [],
  "metadata": {
    "created": "2024-01-01T00:00:00Z",
    "updated": "2024-01-01T00:00:00Z"
  }
}
```

### `clip stats`

Analyze CLIP objects and provide detailed statistics.

#### Usage
```bash
clip stats <file> [options]
clip stats <url> [options]
```

#### Options
- `--format <format>` - Output format: `json`, `table`, `csv` (default: `table`)
- `--detailed` - Show detailed breakdown
- `--export <file>` - Export results to file

#### Examples
```bash
# Basic statistics
clip stats venue.json

# Detailed analysis
clip stats venue.json --detailed

# Export to CSV
clip stats venue.json --format csv --export stats.csv
```

#### Sample Output
```
📊 CLIP Statistics for venue.json

Basic Information:
├── Type: venue
├── Version: 1.0.0
├── Size: 2.4 KB
└── Valid: ✅ Yes

Content Analysis:
├── Name: Present (32 characters)
├── Description: Present (156 characters)
├── URLs: 3 total, 3 valid
├── Features: 5 detected
└── Links: 7 total

Structure Metrics:
├── Depth: 4 levels
├── Properties: 23 total
├── Arrays: 3 found
└── Objects: 8 nested

Validation Score: 95/100
└── Excellent CLIP structure
```

## 🔧 Configuration

### Config File

Create a `.cliprc.json` file in your project root or home directory:

```json
{
  "defaultSchemaVersion": "1.0.0",
  "validation": {
    "strict": false,
    "allowRemote": true,
    "timeout": 30000
  },
  "output": {
    "format": "table",
    "verbose": false
  },
  "generation": {
    "includeExamples": false,
    "schemaVersion": "latest"
  }
}
```

### Environment Variables

- `CLIP_SCHEMA_URL` - Default schema URL
- `CLIP_CACHE_DIR` - Cache directory for remote schemas
- `CLIP_LOG_LEVEL` - Log level: `debug`, `info`, `warn`, `error`
- `DEBUG` - Enable debug output: `clip:*`

## 🎯 Use Cases

### Development Workflow

```bash
# 1. Generate template
clip generate --type venue --output venue.json

# 2. Edit the file with your data
# ... edit venue.json ...

# 3. Validate before using
clip validate venue.json --verbose

# 4. Analyze the structure
clip stats venue.json --detailed
```

### CI/CD Integration

```yaml
# GitHub Actions example
- name: Validate CLIP files
  run: |
    npm install -g @clip/encoder-cli
    clip validate data/*.json --format json > validation-results.json
```

### Batch Processing

```bash
# Validate all JSON files
clip validate data/*.json

# Generate multiple templates
for type in venue event product; do
  clip generate --type $type --output "templates/${type}.json"
done

# Analyze multiple files
find data/ -name "*.json" -exec clip stats {} \;
```

## 🔌 Advanced Features

### Custom Validation Rules

Create custom validation rules in a JavaScript file:

```javascript
// custom-rules.js
module.exports = {
  rules: [
    {
      name: 'venue-coordinates',
      description: 'Venues must have valid coordinates',
      applies: (clip) => clip.type === 'venue',
      validate: (clip) => {
        const coords = clip.location?.coordinates;
        if (!coords) return { valid: false, message: 'Missing coordinates' };
        
        const { latitude, longitude } = coords;
        if (latitude < -90 || latitude > 90) {
          return { valid: false, message: 'Invalid latitude' };
        }
        if (longitude < -180 || longitude > 180) {
          return { valid: false, message: 'Invalid longitude' };
        }
        
        return { valid: true };
      }
    }
  ]
};
```

Use with CLI:
```bash
clip validate venue.json --rules custom-rules.js
```

### Custom Templates

Create custom templates:

```json
{
  "name": "custom-venue",
  "template": {
    "type": "venue",
    "version": "1.0.0",
    "name": "${name}",
    "category": "${category}",
    "custom_field": "${custom_value}"
  },
  "variables": {
    "name": { "type": "string", "required": true },
    "category": { "type": "string", "default": "other" },
    "custom_value": { "type": "string", "required": false }
  }
}
```

## 🐛 Troubleshooting

### Common Issues

**Permission Errors on Global Install**
```bash
# Use npm prefix to install locally
npm config set prefix ~/.npm-global
export PATH=~/.npm-global/bin:$PATH
npm install -g @clip/encoder-cli
```

**Schema Validation Failures**
```bash
# Update to latest schema
clip validate file.json --schema latest

# Use verbose mode for details
clip validate file.json --verbose
```

**Remote URL Timeouts**
```bash
# Increase timeout
CLIP_TIMEOUT=60000 clip validate https://slow-server.com/clip.json

# Use local cache
clip validate https://example.com/clip.json --cache
```

### Debug Mode

Enable detailed logging:

```bash
# Enable all debug output
DEBUG=clip:* clip validate file.json

# Enable specific components
DEBUG=clip:validator clip validate file.json
DEBUG=clip:generator clip generate --type venue
```

## 📚 API Reference

### Programmatic Usage

You can also use the CLI programmatically:

```typescript
import { CLIValidator, CLIGenerator, CLIStats } from '@clip/encoder-cli';

// Validation
const validator = new CLIValidator();
const result = await validator.validate('file.json');

// Generation
const generator = new CLIGenerator();
const template = generator.generate('venue', { minimal: true });

// Statistics
const stats = new CLIStats();
const analysis = await stats.analyze('file.json');
```

### Core Classes

- **`CLIValidator`** - Handles CLIP validation
- **`CLIGenerator`** - Generates CLIP templates  
- **`CLIStats`** - Provides statistical analysis
- **`CLIConfig`** - Manages configuration
- **`CLICache`** - Handles caching for remote resources

## 🚀 Performance

### Benchmarks

- **Validation**: ~1000 files/second (typical CLIP objects)
- **Generation**: ~5000 templates/second
- **Statistics**: ~500 files/second (detailed analysis)

### Optimization Tips

```bash
# Use batch processing for multiple files
clip validate *.json  # Faster than individual calls

# Enable caching for remote validation
export CLIP_CACHE_ENABLED=true

# Use minimal output for CI/CD
clip validate file.json --format minimal
```

## 🔗 Related

- **[Python SDK](../sdk-python/README.md)** - Python library for CLIP objects
- **[Validator Core](../validator-core/README.md)** - Core validation logic
- **[Decoder Library](../decoder-lib/README.md)** - Visual encoding/decoding

## 📄 License

MIT License - see [LICENSE](../../LICENSE) for details.

---

**Part of the [CLIP Toolkit](../../README.md) ecosystem** 
