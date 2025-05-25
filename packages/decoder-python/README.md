# clip-decoder

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![pytest](https://img.shields.io/badge/Test-pytest-red.svg)](https://pytest.org/)
[![Type Hints](https://img.shields.io/badge/Type%20Hints-Yes-brightgreen.svg)](https://docs.python.org/3/library/typing.html)

**Stub Implementation** - Visual CLIP representation decoder library for Python

> ⚠️ **Note**: This is currently a stub implementation. Visual encoding/decoding features are planned for a future release.

## Overview

The CLIP Decoder Library provides placeholder implementations for encoding and decoding visual CLIP representations, including QR codes and HexMatrix formats. This stub implementation defines the classes and validates parameters while raising `NotImplementedError` for the actual encoding/decoding operations.

## Installation

```bash
pip install clip-decoder
```

Or for development:

```bash
pip install -e .
```

## Usage

### Basic Import

```python
from decoder_lib import (
    DecodeOptions,
    EncodeOptions,
    VisualData,
    decode_visual,
    encode_visual,
    is_format_supported,
    get_library_info,
    get_supported_formats
)
```

### Decode Visual CLIP (Stub)

```python
from decoder_lib import decode_visual, DecodeOptions

image_data = b'\x89PNG\r\n\x1a\n...'  # QR code or HexMatrix data
options = DecodeOptions(format='qr', error_correction='medium')

try:
    clip_object = decode_visual(image_data, options)
    # This will raise: NotImplementedError("Visual CLIP decoding is planned for a future release")
except NotImplementedError as e:
    print(f'Expected: {e}')
```

### Encode CLIP Object (Stub)

```python
from decoder_lib import encode_visual, EncodeOptions

clip_object = {
    '@context': 'https://clipprotocol.org/v1',
    'type': 'Venue',
    'id': 'clip:venue:example-123',
    'name': 'Example Venue',
    'description': 'A sample venue for demonstration'
}

options = EncodeOptions(format='qr', error_correction='high', size=256)

try:
    visual_data = encode_visual(clip_object, options)
    # This will raise: NotImplementedError("Visual CLIP encoding is planned for a future release")
except NotImplementedError as e:
    print(f'Expected: {e}')
```

### Check Format Support

```python
from decoder_lib import is_format_supported, get_library_info

print(is_format_supported('qr'))        # True (planned)
print(is_format_supported('hexmatrix')) # True (planned)  
print(is_format_supported('barcode'))   # False

info = get_library_info()
print(info)
# {
#     'name': 'clip-decoder-python',
#     'version': '0.1.0',
#     'status': 'stub-implementation',
#     'supported_formats': [],
#     'planned_formats': ['qr', 'hexmatrix']
# }
```

### Working with Data Classes

```python
from decoder_lib import DecodeOptions, EncodeOptions, VisualData

# Create decode options
decode_opts = DecodeOptions(
    format='qr',
    error_correction='high',
    strict_mode=True
)

# Create encode options
encode_opts = EncodeOptions(
    format='hexmatrix',
    error_correction='medium',
    size=512,
    margin=4
)

# Create visual data structure
visual = VisualData(
    format='qr',
    data=b'encoded_data',
    width=256,
    height=256,
    metadata={'version': '1.0', 'timestamp': '2024-01-01T00:00:00Z'}
)
```

## API Reference

### Data Classes

#### `DecodeOptions`
```python
@dataclass
class DecodeOptions:
    format: Optional[str] = None
    error_correction: Optional[str] = None
    strict_mode: bool = False
```

**Valid values:**
- `format`: 'qr' | 'hexmatrix' | None
- `error_correction`: 'low' | 'medium' | 'high' | None

#### `EncodeOptions`
```python
@dataclass
class EncodeOptions:
    format: str
    error_correction: str = 'medium'
    size: Optional[int] = None
    margin: Optional[int] = None
```

**Valid values:**
- `format`: 'qr' | 'hexmatrix' (required)
- `error_correction`: 'low' | 'medium' | 'high'

#### `VisualData`
```python
@dataclass
class VisualData:
    format: str
    data: bytes
    width: Optional[int] = None
    height: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
```

### Functions

#### `decode_visual(image_data, options=None)`
Placeholder for decoding visual CLIP representations.

**Parameters:**
- `image_data: Union[bytes, str]` - Image data to decode
- `options: Optional[DecodeOptions]` - Decode options

**Returns:** `Dict[str, Any]` (when implemented)

**Raises:** `NotImplementedError` - This is a stub implementation

#### `encode_visual(clip_object, options)`
Placeholder for encoding CLIP objects as visual representations.

**Parameters:**
- `clip_object: Dict[str, Any]` - CLIP object dictionary to encode
- `options: EncodeOptions` - Encode options

**Returns:** `VisualData` (when implemented)

**Raises:** `NotImplementedError` - This is a stub implementation

#### `is_format_supported(format_name)`
Check if a format is planned to be supported.

**Parameters:**
- `format_name: str` - Format name to check

**Returns:** `bool` - True if format is recognized

#### `get_library_info()`
Get information about the decoder library.

**Returns:** `Dict[str, Any]` - Library information

#### `get_supported_formats()`
Get list of planned supported formats.

**Returns:** `List[str]` - List of format names

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/clip-organization/clip-toolkit.git
cd clip-toolkit/packages/decoder-python

# Install development dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=decoder_lib

# Run specific test file
pytest tests/test_decoder_lib.py

# Run with verbose output
pytest -v
```

### Code Quality

```bash
# Format code
black decoder_lib/ tests/

# Sort imports
isort decoder_lib/ tests/

# Type checking
mypy decoder_lib/

# Linting
flake8 decoder_lib/ tests/
```

## Test Coverage

The stub implementation includes comprehensive tests covering:

- ✅ Data class construction and validation
- ✅ Parameter validation for all functions
- ✅ Error handling and expected exceptions
- ✅ Function existence and callability
- ✅ Module exports and imports
- ✅ Type safety and consistency

**Test Results:** 33/33 tests passing (100% success rate)

## Planned Features

When the full implementation is available, this library will support:

### Visual Formats
- **QR Codes**: Standard QR code generation and reading with PIL/qrcode
- **HexMatrix**: Custom hexagonal matrix format optimized for CLIP

### Encoding Features
- Multiple error correction levels
- Customizable size and margins
- Metadata embedding
- Batch processing
- Image format outputs (PNG, SVG, etc.)

### Decoding Features
- Automatic format detection
- Error correction and recovery
- Strict/lenient parsing modes
- Multi-threaded batch processing
- Support for various input formats

### Advanced Features
- Image preprocessing (rotation, scaling, noise reduction)
- Performance optimizations with NumPy
- Integration with computer vision libraries
- Real-time camera decoding support

## Error Handling

The stub implementation provides comprehensive parameter validation:

```python
# These will raise ValueError during construction/validation
DecodeOptions(format='invalid')                      # "Format must be 'qr' or 'hexmatrix'"
EncodeOptions(format='invalid')                      # "Format must be 'qr' or 'hexmatrix'"
decode_visual(None)                                  # "Image data is required"
decode_visual(b'')                                   # "Image data is required"
encode_visual(None, options)                         # "CLIP object is required"
encode_visual({}, options)                           # "CLIP object is required"
encode_visual({'@context': 'test'}, options)        # "Required CLIP field missing: type"
```

## Type Safety

This library uses Python type hints extensively:

```python
from typing import Dict, Any, Union, Optional, List

# All functions are fully typed
def decode_visual(
    image_data: Union[bytes, str], 
    options: Optional[DecodeOptions] = None
) -> Dict[str, Any]:
    ...

# Data classes use proper typing
@dataclass
class VisualData:
    format: str
    data: bytes
    width: Optional[int] = None
    height: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
```

## Integration Examples

### With CLIP SDK

```python
# Future integration example
from clip_sdk import CLIPValidator
from decoder_lib import decode_visual

# Decode and validate in one step
image_data = load_qr_code('clip.png')
clip_dict = decode_visual(image_data)  # When implemented
validator = CLIPValidator()
is_valid = validator.validate_dict(clip_dict)
```

### With CLI Tools

```python
# Future CLI integration example
import sys
from decoder_lib import decode_visual

def main():
    if len(sys.argv) != 2:
        print("Usage: decode_clip <image_file>")
        return
    
    with open(sys.argv[1], 'rb') as f:
        image_data = f.read()
    
    try:
        clip_object = decode_visual(image_data)  # When implemented
        print(json.dumps(clip_object, indent=2))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
```

## Contributing

This is part of the CLIP Toolkit monorepo. See the main repository for contribution guidelines.

### Development Workflow

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Run the test suite
5. Submit a pull request

## License

MIT © CLIP Organization

## Related Packages

- `clip-sdk` - Core Python SDK for CLIP operations
- `@clip-toolkit/decoder-lib` - TypeScript decoder library (this package's counterpart)
- `@clip-toolkit/encoder-cli` - Command-line encoding tools
- `@clip-toolkit/validator-core` - CLIP object validation 