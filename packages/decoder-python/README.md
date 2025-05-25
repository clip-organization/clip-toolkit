# CLIP Decoder Library (Python)

A Python library for visual encoding and decoding of CLIP (Context Link Interface Protocol) objects. This package provides the foundation for converting CLIP data into visual formats like QR codes, DataMatrix codes, and the upcoming HexMatrix format.

[![PyPI version](https://badge.fury.io/py/clip-decoder.svg)](https://badge.fury.io/py/clip-decoder)
[![Python CI](https://github.com/your-org/clip-toolkit/workflows/Python%20CI/badge.svg)](https://github.com/your-org/clip-toolkit/actions)

> **⚠️ Note**: This is currently a stub implementation providing interfaces and structure for future development. The visual encoding/decoding functionality is planned for future releases.

## 🚀 Quick Start

### Installation

```bash
# Install from PyPI
pip install clip-decoder

# Or install with optional dependencies
pip install clip-decoder[all]  # Includes image processing and development tools
```

### Basic Usage

```python
from clip_decoder import CLIPEncoder, CLIPDecoder, VisualFormat

# Create encoder/decoder instances
encoder = CLIPEncoder()
decoder = CLIPDecoder()

# Encode CLIP to QR code (future implementation)
clip_data = {
    'type': 'venue',
    'version': '1.0.0',
    'name': 'Example Venue',
    # ... more CLIP data
}

try:
    qr_code = encoder.encode_to_qr(clip_data)
    print('QR Code generated:', qr_code.data)
except NotImplementedError as e:
    print('Not implemented yet:', e)

# Decode QR code back to CLIP (future implementation)
try:
    decoded_clip = decoder.decode_from_qr(qr_code_data)
    print('Decoded CLIP:', decoded_clip)
except NotImplementedError as e:
    print('Not implemented yet:', e)
```

## 📦 Core Classes

### CLIPEncoder

The main encoding class for converting CLIP objects to visual formats:

```python
from clip_decoder import CLIPEncoder, QREncodeOptions
from typing import Dict, Any

encoder = CLIPEncoder()

# Available encoding methods (future implementation)
class CLIPEncoder:
    def encode_to_qr(self, data: Dict[str, Any], options: QREncodeOptions = None) -> QRCodeResult:
        """Encode CLIP data to QR code"""
        pass
    
    def encode_to_datamatrix(self, data: Dict[str, Any], options: DataMatrixOptions = None) -> DataMatrixResult:
        """Encode CLIP data to DataMatrix code"""
        pass
    
    def encode_to_hexmatrix(self, data: Dict[str, Any], options: HexMatrixOptions = None) -> HexMatrixResult:
        """Encode CLIP data to HexMatrix format"""
        pass
    
    def encode(self, data: Dict[str, Any], format: VisualFormat, options: EncodeOptions = None) -> VisualResult:
        """Generic encoding method"""
        pass
    
    def estimate_size(self, data: Dict[str, Any], format: VisualFormat) -> SizeEstimate:
        """Estimate encoded size"""
        pass
    
    def validate_for_encoding(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate data for encoding"""
        pass
    
    def get_supported_formats(self) -> List[VisualFormat]:
        """Get list of supported formats"""
        pass

# Example configuration
options = QREncodeOptions(
    error_correction='M',
    version='auto',
    mask_pattern='auto',
    quiet_zone=4,
    scale=8,
    margin=10,
    color=QRColor(dark='#000000', light='#FFFFFF')
)
```

### CLIPDecoder

The main decoding class for extracting CLIP objects from visual formats:

```python
from clip_decoder import CLIPDecoder, DecodeOptions
from typing import Union, Optional
import numpy as np

decoder = CLIPDecoder()

# Available decoding methods (future implementation)
class CLIPDecoder:
    def decode_from_qr(self, image: Union[np.ndarray, bytes, str]) -> Dict[str, Any]:
        """Decode CLIP data from QR code"""
        pass
    
    def decode_from_datamatrix(self, image: Union[np.ndarray, bytes, str]) -> Dict[str, Any]:
        """Decode CLIP data from DataMatrix code"""
        pass
    
    def decode_from_hexmatrix(self, image: Union[np.ndarray, bytes, str]) -> Dict[str, Any]:
        """Decode CLIP data from HexMatrix format"""
        pass
    
    def decode(self, image: Union[np.ndarray, bytes, str], format: Optional[VisualFormat] = None) -> Dict[str, Any]:
        """Generic decoding method"""
        pass
    
    def detect_format(self, image: Union[np.ndarray, bytes, str]) -> Optional[VisualFormat]:
        """Detect visual format from image"""
        pass
    
    def validate_image(self, image: Union[np.ndarray, bytes, str]) -> bool:
        """Validate image data"""
        pass
    
    def get_image_info(self, image: Union[np.ndarray, bytes, str]) -> ImageInfo:
        """Get image information"""
        pass

# Example usage (when implemented)
decode_options = DecodeOptions(
    formats=['qr', 'datamatrix'],
    error_correction=True,
    timeout=5000,
    preprocess_image=True
)
```

## 🔧 Visual Formats

### Supported Formats (Planned)

```python
from enum import Enum
from dataclasses import dataclass
from typing import Optional

class VisualFormat(Enum):
    QR = 'qr'
    DATAMATRIX = 'datamatrix'
    HEXMATRIX = 'hexmatrix'
    AZTEC = 'aztec'
    PDF417 = 'pdf417'

@dataclass
class QRCodeResult:
    format: str = 'qr'
    data: str = ''              # Base64 encoded image
    raw_data: bytes = b''       # Raw image data
    version: int = 0            # QR version (1-40)
    error_correction: str = ''  # L, M, Q, H
    modules: int = 0            # Size in modules
    quiet_zone: int = 0         # Quiet zone size
    metadata: Optional[dict] = None

@dataclass
class DataMatrixResult:
    format: str = 'datamatrix'
    data: str = ''
    raw_data: bytes = b''
    symbol_size: str = ''       # e.g., "32x32"
    capacity: int = 0           # Data capacity in bytes
    metadata: Optional[dict] = None

@dataclass
class HexMatrixResult:
    format: str = 'hexmatrix'
    data: str = ''
    raw_data: bytes = b''
    hex_size: int = 0           # Hexagon grid size
    layers: int = 0             # Number of concentric layers
    compression: str = ''       # Compression algorithm used
    metadata: Optional[dict] = None
```

### Format Capabilities

```python
from clip_decoder import CLIPEncoder

encoder = CLIPEncoder()

# Get format information
format_info = encoder.get_format_info('qr')

@dataclass
class FormatInfo:
    name: str
    description: str
    max_capacity: int           # Maximum bytes
    error_correction: bool      # Supports error correction
    scalable: bool             # Can be resized
    common_usage: List[str]    # Common use cases
    browser_support: dict      # Browser support info

# Example format information
qr_info = FormatInfo(
    name='QR Code',
    description='Quick Response code, widely supported 2D barcode',
    max_capacity=4296,
    error_correction=True,
    scalable=True,
    common_usage=['mobile', 'print', 'display'],
    browser_support={'encode': True, 'decode': True}
)
```

## 🎯 Use Cases (Planned)

### Mobile App Integration

```python
from clip_decoder import CLIPEncoder
from typing import Dict, Any

async def generate_mobile_qr(venue_data: Dict[str, Any]) -> str:
    """Generate QR code for mobile app"""
    encoder = CLIPEncoder()
    
    qr_options = QREncodeOptions(
        size='large',
        error_correction='H',  # High error correction for mobile
        format='png',
        scale=8
    )
    
    try:
        qr_code = await encoder.encode_to_qr(venue_data, qr_options)
        return qr_code.data  # Base64 image data
    except Exception as e:
        raise RuntimeError(f"QR generation failed: {e}")

async def decode_from_camera(image_data: np.ndarray) -> Dict[str, Any]:
    """Decode from camera input"""
    decoder = CLIPDecoder()
    
    try:
        clip_data = await decoder.decode(image_data)
        return clip_data
    except Exception as e:
        raise RuntimeError(f"Decode failed: {e}")
```

### Print Applications

```python
from clip_decoder import CLIPEncoder, VisualFormat

def generate_printable_code(clip_data: Dict[str, Any], format: VisualFormat = VisualFormat.QR) -> VisualResult:
    """Generate high-resolution codes for printing"""
    encoder = CLIPEncoder()
    
    print_options = EncodeOptions(
        resolution=300,  # 300 DPI
        size={'width': 2, 'height': 2},  # 2x2 inches
        format='svg',  # Vector format for scaling
        error_correction='H',
        quiet_zone=8  # Larger quiet zone for print
    )
    
    if format == VisualFormat.QR:
        return encoder.encode_to_qr(clip_data, print_options)
    else:
        return encoder.encode_to_datamatrix(clip_data, print_options)
```

### Web Integration

```python
import asyncio
from typing import List, Union
import base64

class WebCLIPDecoder:
    """Browser-based encoding/decoding"""
    
    def __init__(self):
        self.decoder = CLIPDecoder()
    
    async def decode_from_file(self, file_data: bytes) -> Dict[str, Any]:
        """Decode from file upload"""
        try:
            clip_data = await self.decoder.decode(file_data)
            return clip_data
        except Exception as e:
            raise RuntimeError(f"File decode failed: {e}")
    
    async def decode_from_base64(self, base64_data: str) -> Dict[str, Any]:
        """Decode from base64 image data"""
        try:
            image_data = base64.b64decode(base64_data)
            clip_data = await self.decoder.decode(image_data)
            return clip_data
        except Exception as e:
            raise RuntimeError(f"Base64 decode failed: {e}")
    
    async def batch_decode(self, images: List[Union[bytes, str]]) -> List[Dict[str, Any]]:
        """Decode multiple images"""
        tasks = [self.decoder.decode(img) for img in images]
        return await asyncio.gather(*tasks, return_exceptions=True)
```

## 🧪 Testing (Current Implementation)

The current stub implementation includes comprehensive tests that validate the interface structure:

### Running Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run with coverage
pytest --cov=clip_decoder

# Run specific test categories
pytest tests/test_encoder.py
pytest tests/test_decoder.py
pytest tests/test_formats.py

# Run performance tests
pytest tests/test_performance.py -v
```

### Test Structure

```python
import pytest
from clip_decoder import CLIPEncoder, CLIPDecoder, VisualFormat, NotImplementedError

class TestCLIPEncoder:
    def setup_method(self):
        self.encoder = CLIPEncoder()
    
    def test_encoder_instantiation(self):
        """Test encoder can be instantiated"""
        assert isinstance(self.encoder, CLIPEncoder)
    
    def test_encoding_methods_not_implemented(self):
        """Test encoding methods throw NotImplementedError"""
        clip_data = {'type': 'venue', 'version': '1.0.0', 'name': 'Test'}
        
        with pytest.raises(NotImplementedError, match="Not implemented"):
            self.encoder.encode_to_qr(clip_data)
        
        with pytest.raises(NotImplementedError, match="Not implemented"):
            self.encoder.encode_to_datamatrix(clip_data)
        
        with pytest.raises(NotImplementedError, match="Not implemented"):
            self.encoder.encode_to_hexmatrix(clip_data)
    
    def test_parameter_validation(self):
        """Test parameter validation before NotImplementedError"""
        with pytest.raises(ValueError, match="Invalid CLIP data"):
            self.encoder.encode_to_qr(None)
        
        with pytest.raises(ValueError, match="Missing required"):
            self.encoder.encode_to_qr({})

class TestCLIPDecoder:
    def setup_method(self):
        self.decoder = CLIPDecoder()
    
    def test_image_validation(self):
        """Test image data validation"""
        with pytest.raises(ValueError, match="Invalid image data"):
            self.decoder.decode_from_qr(None)
        
        with pytest.raises(ValueError, match="Empty image data"):
            self.decoder.decode_from_qr(b'')
    
    def test_format_detection_interface(self):
        """Test format detection interface"""
        mock_image_data = b'\x89PNG\r\n\x1a\n'  # PNG header
        
        with pytest.raises(NotImplementedError, match="Not implemented"):
            self.decoder.detect_format(mock_image_data)
```

## 🔮 Future Implementation

### Roadmap

**Phase 1: QR Code Support**
- Basic QR code encoding/decoding using `qrcode` and `pyzbar`
- Error correction levels
- Custom styling options
- PIL/Pillow integration

**Phase 2: DataMatrix Support**
- Compact encoding for small CLIP objects using `pylibdmtx`
- Industrial printing applications
- Mobile scanning optimization

**Phase 3: HexMatrix Format**
- CLIP-specific visual format
- Custom hexagonal grid implementation
- Enhanced error correction
- Aesthetic appeal for consumer applications

**Phase 4: Advanced Features**
- Multi-format detection using `opencv-python`
- Batch processing with `asyncio`
- Real-time camera scanning
- Performance optimizations with `numba`

### Architecture Goals

```python
from abc import ABC, abstractmethod
from typing import Protocol, runtime_checkable

# Future architecture will support:

@runtime_checkable
class VisualFormatPlugin(Protocol):
    """Plugin interface for visual formats"""
    name: str
    encoder: 'FormatEncoder'
    decoder: 'FormatDecoder'
    capabilities: 'FormatCapabilities'

class StreamingEncoder(ABC):
    """Streaming support for large data"""
    
    @abstractmethod
    async def encode_stream(self, data_stream) -> AsyncIterator[VisualResult]:
        pass
    
    @abstractmethod
    async def decode_stream(self, image_stream) -> AsyncIterator[Dict[str, Any]]:
        pass

class RealtimeDecoder(ABC):
    """Real-time processing"""
    
    @abstractmethod
    def start_scanning(self, video_source) -> None:
        pass
    
    @abstractmethod
    def on_detected(self, callback) -> None:
        pass
    
    @abstractmethod
    def stop_scanning(self) -> None:
        pass
```

## 📚 API Reference

### Current Classes

```python
# Core classes (stub implementation)
class CLIPEncoder:
    def encode_to_qr(self, data: Dict[str, Any], options: QREncodeOptions = None) -> QRCodeResult:
        """Encode CLIP data to QR code (not implemented)"""
        raise NotImplementedError("QR encoding not yet implemented")
    
    def encode_to_datamatrix(self, data: Dict[str, Any], options: DataMatrixOptions = None) -> DataMatrixResult:
        """Encode CLIP data to DataMatrix (not implemented)"""
        raise NotImplementedError("DataMatrix encoding not yet implemented")
    
    def encode_to_hexmatrix(self, data: Dict[str, Any], options: HexMatrixOptions = None) -> HexMatrixResult:
        """Encode CLIP data to HexMatrix (not implemented)"""
        raise NotImplementedError("HexMatrix encoding not yet implemented")

class CLIPDecoder:
    def decode_from_qr(self, image: ImageSource) -> Dict[str, Any]:
        """Decode CLIP data from QR code (not implemented)"""
        raise NotImplementedError("QR decoding not yet implemented")
    
    def decode_from_datamatrix(self, image: ImageSource) -> Dict[str, Any]:
        """Decode CLIP data from DataMatrix (not implemented)"""
        raise NotImplementedError("DataMatrix decoding not yet implemented")
    
    def decode_from_hexmatrix(self, image: ImageSource) -> Dict[str, Any]:
        """Decode CLIP data from HexMatrix (not implemented)"""
        raise NotImplementedError("HexMatrix decoding not yet implemented")

# Type definitions
ImageSource = Union[np.ndarray, bytes, str, 'PIL.Image.Image']

@dataclass
class EncodeOptions:
    format: Optional[str] = None
    size: Optional[Union[int, Dict[str, int]]] = None
    error_correction: Optional[str] = None
    margin: Optional[int] = None

@dataclass
class VisualResult:
    format: str
    data: str
    raw_data: bytes
    metadata: Optional[Dict[str, Any]] = None
```

### Exception Types

```python
class NotImplementedError(Exception):
    """Raised when a feature is not yet implemented"""
    def __init__(self, feature: str):
        super().__init__(f"{feature} is not yet implemented")
        self.feature = feature

class InvalidInputError(ValueError):
    """Raised when input data is invalid"""
    pass

class EncodingError(Exception):
    """Raised when encoding fails"""
    def __init__(self, message: str, format: str):
        super().__init__(message)
        self.format = format

class DecodingError(Exception):
    """Raised when decoding fails"""
    def __init__(self, message: str, format: Optional[str] = None):
        super().__init__(message)
        self.format = format
```

## 🔧 Configuration

### Environment Variables

```bash
# Image processing configuration
export CLIP_DECODER_BACKEND=PIL  # PIL, OpenCV, or auto
export CLIP_DECODER_CACHE_DIR=/tmp/clip-decoder-cache
export CLIP_DECODER_MAX_IMAGE_SIZE=10485760  # 10MB

# Performance configuration
export CLIP_DECODER_THREADS=4
export CLIP_DECODER_TIMEOUT=30
export CLIP_DECODER_BATCH_SIZE=10

# Logging
export CLIP_DECODER_LOG_LEVEL=INFO
```

### Configuration File

Create `~/.clip-decoder.yaml`:

```yaml
encoding:
  default_format: qr
  quality: high
  error_correction: M

decoding:
  auto_detect: true
  preprocess: true
  timeout: 30

image_processing:
  backend: PIL
  max_size: 10485760
  cache_enabled: true

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
pip uninstall clip-decoder
pip install clip-decoder
```

**Image Processing Issues**
```python
from clip_decoder import CLIPDecoder
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

decoder = CLIPDecoder()

# Test image validation
try:
    result = decoder.validate_image(image_data)
    print(f"Image valid: {result}")
except Exception as e:
    print(f"Image validation failed: {e}")
```

**Performance Issues**
```python
# Use async processing for multiple images
import asyncio
from clip_decoder import CLIPDecoder

async def process_images_async(images):
    decoder = CLIPDecoder()
    tasks = [decoder.decode(img) for img in images]
    return await asyncio.gather(*tasks, return_exceptions=True)

# Batch processing
def process_images_batch(images, batch_size=10):
    decoder = CLIPDecoder()
    results = []
    
    for i in range(0, len(images), batch_size):
        batch = images[i:i + batch_size]
        batch_results = [decoder.decode(img) for img in batch]
        results.extend(batch_results)
    
    return results
```

## 🔗 Related

- **[Decoder Library (TypeScript)](../decoder-lib/README.md)** - TypeScript implementation
- **[Encoder CLI](../encoder-cli/README.md)** - Command-line tool for CLIP objects
- **[Python SDK](../sdk-python/README.md)** - Python library for CLIP manipulation
- **[Validator Core](../validator-core/README.md)** - Core validation logic

## 📄 License

MIT License - see [LICENSE](../../LICENSE) for details.

---

**Part of the [CLIP Toolkit](../../README.md) ecosystem** 