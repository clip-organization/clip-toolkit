# @clip-toolkit/encoder-cli

A powerful command-line interface for validating and generating CLIP (Context Link Interface Protocol) JSON objects.

## Features

- ✅ **Validate** CLIP objects against the official schema
- 🏗️ **Generate** CLIP templates for venues, devices, and applications
- 📊 **Analyze** CLIP objects with detailed statistics and recommendations
- 🎨 **Beautiful output** with colors and progress indicators
- 🔄 **Multiple formats** - support for both text and JSON output
- 🌐 **URL support** - validate CLIP objects from remote URLs
- 🔧 **Flexible options** - extensive configuration and customization

## Installation

### Global Installation (Recommended)
```bash
npm install -g @clip-toolkit/encoder-cli
```

### Local Installation
```bash
npm install @clip-toolkit/encoder-cli
```

## Quick Start

### Validate a CLIP Object
```bash
# Validate a local file
clip validate my-venue.json

# Validate from URL
clip validate https://example.com/my-device.json

# Validate with JSON output
clip validate my-app.json --output json
```

### Generate CLIP Templates
```bash
# Generate a venue template
clip generate --type venue

# Generate minimal device template
clip generate --type device --minimal

# Save to file
clip generate --type app --output my-app.json
```

### Analyze CLIP Objects
```bash
# Basic statistics
clip stats my-venue.json

# Detailed analysis
clip stats my-device.json --detailed

# JSON output for scripts
clip stats my-app.json --output json
```

## Command Reference

### Global Options

| Option | Description |
|--------|-------------|
| `-v, --verbose` | Enable verbose logging |
| `--no-color` | Disable colored output |
| `-V, --version` | Show version number |
| `-h, --help` | Show help information |

### `clip validate <file>`

Validate a CLIP JSON file against the official schema.

**Arguments:**
- `<file>` - Path to CLIP JSON file or URL

**Options:**
| Option | Description | Default |
|--------|-------------|---------|
| `-s, --schema <file>` | Custom schema file path | Official CLIP schema |
| `-o, --output <format>` | Output format (text, json) | `text` |
| `--strict` | Enable strict validation mode | `false` |
| `--no-warnings` | Suppress warnings | Show warnings |
| `--exit-code` | Return non-zero exit code on failure | `false` |

**Examples:**
```bash
# Basic validation
clip validate venue.json

# Strict validation with custom schema
clip validate device.json --strict --schema ./custom-schema.json

# JSON output for CI/CD
clip validate app.json --output json --exit-code
```

### `clip generate`

Generate a CLIP template for different object types.

**Required Options:**
| Option | Description | Values |
|--------|-------------|--------|
| `-t, --type <type>` | Type of CLIP object | `venue`, `device`, `app` |

**Optional:**
| Option | Description | Default |
|--------|-------------|---------|
| `-o, --output <file>` | Output file | stdout |
| `--template <name>` | Use specific template | default |
| `--interactive` | Interactive mode | `false` |
| `--minimal` | Generate minimal template | `false` |

**Examples:**
```bash
# Generate venue template
clip generate --type venue

# Minimal device template to file
clip generate --type device --minimal --output device-template.json

# Interactive app generation (coming soon)
clip generate --type app --interactive
```

### `clip stats <file>`

Show detailed statistics and analysis of a CLIP object.

**Arguments:**
- `<file>` - Path to CLIP JSON file or URL

**Options:**
| Option | Description | Default |
|--------|-------------|---------|
| `-o, --output <format>` | Output format (text, json) | `text` |
| `--detailed` | Show detailed breakdown | `false` |

**Examples:**
```bash
# Basic statistics
clip stats venue.json

# Detailed analysis
clip stats device.json --detailed

# JSON output for analysis tools
clip stats app.json --output json
```

## Output Examples

### Validation Output
```
CLIP Validation Report
──────────────────────────────────────────────────
File: venue.json
Status: ✓ Valid

Statistics:
  Type: Venue
  Completeness: 85%
  Size: 2.1 KB
  Features: 3
  Actions: 2
  Services: 1
  Has Location: Yes
  Has Persona: Yes

✓ CLIP object is valid!
ℹ️  Consider adding more optional fields for better completeness.
```

### Statistics Output
```
CLIP Object Statistics
══════════════════════════════════════════════════
File: venue.json
Type: Venue

📊 Basic Statistics
  Size: 2.1 KB
  Completeness: 85%
  Features: 3
  Actions: 2
  Services: 1

🏗️  Structure
  Top-level fields: 8
  Required fields: 5
  Optional fields: 3
  Nested objects: 2
  Arrays: 3

📝 Content
  Has context: Yes
  Has timestamp: Yes
  Timestamp age: 2 days ago
  Name length: 15 characters
  Description length: 127 characters

✅ Compliance
  Valid ID format: Yes
  Has location: Yes
  Has persona: Yes
  Has actions: Yes
  Has features: Yes
  Has services: No

💡 Recommendations
  1. Consider adding services for better integration
  2. Consider updating the lastUpdated timestamp
```

### Template Generation
```json
{
  "@context": "https://clipprotocol.org/v1",
  "type": "Venue",
  "id": "clip:us:state:venue:example-abc123",
  "name": "Example Venue",
  "description": "An example venue template for CLIP. Replace with your venue description.",
  "lastUpdated": "2024-01-15T10:30:00.000Z",
  "location": {
    "address": "123 Example St, Example City, ST 12345",
    "coordinates": {
      "latitude": 40.7589,
      "longitude": -73.9851
    },
    "timezone": "America/New_York"
  },
  "features": [
    {
      "name": "Example Feature",
      "type": "facility",
      "count": 1,
      "available": 1,
      "metadata": {
        "description": "Description of this feature"
      }
    }
  ],
  "actions": [
    {
      "label": "Visit Website",
      "type": "link",
      "endpoint": "https://example.com",
      "description": "Visit our website for more information"
    }
  ],
  "persona": {
    "role": "Assistant",
    "personality": "helpful, friendly",
    "expertise": ["customer service", "information"],
    "prompt": "You are a helpful assistant for this venue. Provide information and help visitors."
  }
}
```

## Integration

### CI/CD Pipeline
```yaml
# GitHub Actions example
- name: Validate CLIP Objects
  run: |
    clip validate assets/venue.json --output json --exit-code
    clip validate assets/device.json --output json --exit-code
```

### npm Scripts
```json
{
  "scripts": {
    "validate:clip": "clip validate assets/*.json --exit-code",
    "generate:venue": "clip generate --type venue --output templates/venue.json",
    "stats:all": "clip stats assets/*.json --detailed"
  }
}
```

### Programmatic Usage
```typescript
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

// Validate and get JSON result
const { stdout } = await execAsync('clip validate venue.json --output json');
const result = JSON.parse(stdout);

if (result.valid) {
  console.log('CLIP object is valid!');
  console.log(`Completeness: ${result.stats.completeness}%`);
}
```

## Error Handling

The CLI provides detailed error messages and suggestions:

- **File not found**: Clear message with file path
- **Invalid JSON**: Syntax error location
- **Schema validation**: Field-specific errors with suggestions
- **Network errors**: Connection and timeout information
- **Permission errors**: File access issues

## Troubleshooting

### Common Issues

**Command not found**
```bash
# Ensure global installation
npm list -g @clip-toolkit/encoder-cli

# Or use npx
npx @clip-toolkit/encoder-cli validate file.json
```

**Module import errors**
```bash
# Update to latest version
npm update -g @clip-toolkit/encoder-cli

# Clear npm cache
npm cache clean --force
```

**Validation fails for valid CLIP**
```bash
# Use verbose mode for details
clip validate file.json --verbose

# Check with official schema
clip validate file.json --schema https://raw.githubusercontent.com/clip-organization/spec/main/clip.schema.json
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Run the test suite: `npm test`
5. Submit a pull request

## License

MIT License - see [LICENSE](../../LICENSE) file for details.

## Related Packages

- [@clip-toolkit/validator-core](../validator-core) - Core validation engine
- [@clip-toolkit/decoder-lib](../decoder-lib) - CLIP object decoder
- [@clip-toolkit/sdk-python](../sdk-python) - Python SDK

## Support

- 📖 [Documentation](../../docs)
- 🐛 [Issues](../../issues)
- 💬 [Discussions](../../discussions)
- 📧 [Email Support](mailto:support@clipprotocol.org) 