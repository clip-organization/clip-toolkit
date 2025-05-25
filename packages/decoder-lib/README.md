# CLIP Decoder Library (TypeScript)

A TypeScript library for visual encoding and decoding of CLIP (Context Link Interface Protocol) objects. This package provides the foundation for converting CLIP data into visual formats like QR codes, DataMatrix codes, and the upcoming HexMatrix format.

[![npm version](https://badge.fury.io/js/%40clip%2Fdecoder-lib.svg)](https://badge.fury.io/js/%40clip%2Fdecoder-lib)
[![TypeScript CI](https://github.com/your-org/clip-toolkit/workflows/TypeScript%20CI/badge.svg)](https://github.com/your-org/clip-toolkit/actions)

> **⚠️ Note**: This is currently a stub implementation providing interfaces and structure for future development. The visual encoding/decoding functionality is planned for future releases.

## 🚀 Quick Start

### Installation

```bash
# npm
npm install @clip/decoder-lib

# yarn
yarn add @clip/decoder-lib

# pnpm
pnpm add @clip/decoder-lib
```

### Basic Usage

```typescript
import { CLIPDecoder, CLIPEncoder, VisualFormat } from '@clip/decoder-lib';

// Create encoder/decoder instances
const encoder = new CLIPEncoder();
const decoder = new CLIPDecoder();

// Encode CLIP to QR code (future implementation)
const clipData = {
  type: 'venue',
  version: '1.0.0',
  name: 'Example Venue',
  // ... more CLIP data
};

try {
  const qrCode = await encoder.encodeToQR(clipData);
  console.log('QR Code generated:', qrCode.data);
} catch (error) {
  console.log('Not implemented yet:', error.message);
}

// Decode QR code back to CLIP (future implementation)
try {
  const decodedClip = await decoder.decodeFromQR(qrCodeData);
  console.log('Decoded CLIP:', decodedClip);
} catch (error) {
  console.log('Not implemented yet:', error.message);
}
```

## 📦 Core Interfaces

### CLIPEncoder

The main encoding interface for converting CLIP objects to visual formats:

```typescript
import { CLIPEncoder, EncodeOptions, VisualFormat } from '@clip/decoder-lib';

const encoder = new CLIPEncoder();

// Available encoding methods (future implementation)
interface CLIPEncoder {
  // QR Code encoding
  encodeToQR(data: CLIPData, options?: QREncodeOptions): Promise<QRCodeResult>;
  
  // DataMatrix encoding
  encodeToDataMatrix(data: CLIPData, options?: DataMatrixOptions): Promise<DataMatrixResult>;
  
  // HexMatrix encoding (planned format)
  encodeToHexMatrix(data: CLIPData, options?: HexMatrixOptions): Promise<HexMatrixResult>;
  
  // Generic visual encoding
  encode(data: CLIPData, format: VisualFormat, options?: EncodeOptions): Promise<VisualResult>;
  
  // Utility methods
  estimateSize(data: CLIPData, format: VisualFormat): Promise<SizeEstimate>;
  validateForEncoding(data: CLIPData): Promise<ValidationResult>;
  getSupportedFormats(): VisualFormat[];
}

// Example configuration
const options: QREncodeOptions = {
  errorCorrection: 'M',
  version: 'auto',
  maskPattern: 'auto',
  quietZone: 4,
  scale: 8,
  margin: 10,
  color: {
    dark: '#000000',
    light: '#FFFFFF'
  }
};
```

### CLIPDecoder

The main decoding interface for extracting CLIP objects from visual formats:

```typescript
import { CLIPDecoder, DecodeOptions } from '@clip/decoder-lib';

const decoder = new CLIPDecoder();

// Available decoding methods (future implementation)
interface CLIPDecoder {
  // QR Code decoding
  decodeFromQR(image: ImageData | Buffer | string): Promise<CLIPData>;
  
  // DataMatrix decoding
  decodeFromDataMatrix(image: ImageData | Buffer | string): Promise<CLIPData>;
  
  // HexMatrix decoding (planned format)
  decodeFromHexMatrix(image: ImageData | Buffer | string): Promise<CLIPData>;
  
  // Generic visual decoding
  decode(image: ImageData | Buffer | string, format?: VisualFormat): Promise<CLIPData>;
  
  // Utility methods
  detectFormat(image: ImageData | Buffer | string): Promise<VisualFormat | null>;
  validateImage(image: ImageData | Buffer | string): Promise<boolean>;
  getImageInfo(image: ImageData | Buffer | string): Promise<ImageInfo>;
}

// Example usage (when implemented)
const decodeOptions: DecodeOptions = {
  formats: ['qr', 'datamatrix'],
  errorCorrection: true,
  timeout: 5000,
  preprocessImage: true
};
```

## 🔧 Visual Formats

### Supported Formats (Planned)

```typescript
type VisualFormat = 'qr' | 'datamatrix' | 'hexmatrix' | 'aztec' | 'pdf417';

// QR Code - Most common format
interface QRCodeResult {
  format: 'qr';
  data: string;          // Base64 encoded image
  rawData: Buffer;       // Raw image data
  version: number;       // QR version (1-40)
  errorCorrection: 'L' | 'M' | 'Q' | 'H';
  modules: number;       // Size in modules
  quietZone: number;     // Quiet zone size
  metadata: QRMetadata;
}

// DataMatrix - Compact format for small data
interface DataMatrixResult {
  format: 'datamatrix';
  data: string;
  rawData: Buffer;
  symbolSize: string;    // e.g., "32x32"
  capacity: number;      // Data capacity in bytes
  metadata: DataMatrixMetadata;
}

// HexMatrix - Future CLIP-specific format
interface HexMatrixResult {
  format: 'hexmatrix';
  data: string;
  rawData: Buffer;
  hexSize: number;       // Hexagon grid size
  layers: number;        // Number of concentric layers
  compression: string;   // Compression algorithm used
  metadata: HexMatrixMetadata;
}
```

### Format Capabilities

```typescript
// Get format information
const formatInfo = encoder.getFormatInfo('qr');

interface FormatInfo {
  name: string;
  description: string;
  maxCapacity: number;        // Maximum bytes
  errorCorrection: boolean;   // Supports error correction
  scalable: boolean;         // Can be resized
  commonUsage: string[];     // Common use cases
  browserSupport: {
    encode: boolean;
    decode: boolean;
  };
}

// Example format information
const qrInfo: FormatInfo = {
  name: 'QR Code',
  description: 'Quick Response code, widely supported 2D barcode',
  maxCapacity: 4296,
  errorCorrection: true,
  scalable: true,
  commonUsage: ['mobile', 'print', 'display'],
  browserSupport: { encode: true, decode: true }
};
```

## 🎯 Use Cases (Planned)

### Mobile App Integration

```typescript
import { CLIPEncoder } from '@clip/decoder-lib';

// Generate QR code for mobile app
async function generateMobileQR(venueData: CLIPData) {
  const encoder = new CLIPEncoder();
  
  const qrOptions = {
    size: 'large',
    errorCorrection: 'H', // High error correction for mobile
    format: 'png',
    scale: 8
  };
  
  try {
    const qrCode = await encoder.encodeToQR(venueData, qrOptions);
    return qrCode.data; // Base64 image data
  } catch (error) {
    throw new Error(`QR generation failed: ${error.message}`);
  }
}

// Decode from camera input
async function decodeFromCamera(imageData: ImageData) {
  const decoder = new CLIPDecoder();
  
  try {
    const clipData = await decoder.decode(imageData);
    return clipData;
  } catch (error) {
    throw new Error(`Decode failed: ${error.message}`);
  }
}
```

### Print Applications

```typescript
// Generate high-resolution codes for printing
async function generatePrintableCode(clipData: CLIPData, format: 'qr' | 'datamatrix' = 'qr') {
  const encoder = new CLIPEncoder();
  
  const printOptions = {
    resolution: 300, // 300 DPI
    size: { width: 2, height: 2 }, // 2x2 inches
    format: 'svg', // Vector format for scaling
    errorCorrection: 'H',
    quietZone: 8 // Larger quiet zone for print
  };
  
  if (format === 'qr') {
    return await encoder.encodeToQR(clipData, printOptions);
  } else {
    return await encoder.encodeToDataMatrix(clipData, printOptions);
  }
}
```

### Web Integration

```typescript
// Browser-based encoding/decoding
class WebCLIPDecoder {
  private decoder: CLIPDecoder;
  
  constructor() {
    this.decoder = new CLIPDecoder();
  }
  
  // Decode from file upload
  async decodeFromFile(file: File): Promise<CLIPData> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      
      reader.onload = async (event) => {
        try {
          const imageData = event.target?.result as ArrayBuffer;
          const clipData = await this.decoder.decode(new Uint8Array(imageData));
          resolve(clipData);
        } catch (error) {
          reject(error);
        }
      };
      
      reader.readAsArrayBuffer(file);
    });
  }
  
  // Decode from webcam
  async decodeFromWebcam(video: HTMLVideoElement): Promise<CLIPData> {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d')!;
    
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    ctx.drawImage(video, 0, 0);
    
    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    return await this.decoder.decode(imageData);
  }
}
```

## 🧪 Testing (Current Implementation)

The current stub implementation includes comprehensive tests that validate the interface structure:

### Running Tests

```bash
# Install dependencies
npm install

# Run tests
npm test

# Run with coverage
npm run test:coverage

# Watch mode
npm run test:watch
```

### Test Structure

```typescript
import { CLIPEncoder, CLIPDecoder, VisualFormat } from '@clip/decoder-lib';
import { describe, it, expect } from '@jest/globals';

describe('CLIPEncoder', () => {
  let encoder: CLIPEncoder;
  
  beforeEach(() => {
    encoder = new CLIPEncoder();
  });
  
  it('should be instantiable', () => {
    expect(encoder).toBeInstanceOf(CLIPEncoder);
  });
  
  it('should throw NotImplementedError for encoding methods', async () => {
    const clipData = { type: 'venue', version: '1.0.0', name: 'Test' };
    
    await expect(encoder.encodeToQR(clipData)).rejects.toThrow('Not implemented');
    await expect(encoder.encodeToDataMatrix(clipData)).rejects.toThrow('Not implemented');
    await expect(encoder.encodeToHexMatrix(clipData)).rejects.toThrow('Not implemented');
  });
  
  it('should validate parameters before throwing NotImplementedError', async () => {
    // Should validate input parameters even in stub implementation
    await expect(encoder.encodeToQR(null as any)).rejects.toThrow('Invalid CLIP data');
    await expect(encoder.encodeToQR({})).rejects.toThrow('Missing required');
  });
});

describe('CLIPDecoder', () => {
  let decoder: CLIPDecoder;
  
  beforeEach(() => {
    decoder = new CLIPDecoder();
  });
  
  it('should validate image data before processing', async () => {
    await expect(decoder.decodeFromQR(null as any)).rejects.toThrow('Invalid image data');
    await expect(decoder.decodeFromQR('')).rejects.toThrow('Empty image data');
  });
  
  it('should provide format detection interface', async () => {
    const mockImageData = new Uint8Array([1, 2, 3, 4]);
    
    // Should throw NotImplementedError but validate input first
    await expect(decoder.detectFormat(mockImageData)).rejects.toThrow('Not implemented');
  });
});
```

## 🔮 Future Implementation

### Roadmap

**Phase 1: QR Code Support**
- Basic QR code encoding/decoding
- Error correction levels
- Custom styling options
- Browser and Node.js support

**Phase 2: DataMatrix Support**
- Compact encoding for small CLIP objects
- Industrial printing applications
- Mobile scanning optimization

**Phase 3: HexMatrix Format**
- CLIP-specific visual format
- Optimized for CLIP data structure
- Enhanced error correction
- Aesthetic appeal for consumer applications

**Phase 4: Advanced Features**
- Multi-format detection
- Batch processing
- Real-time camera scanning
- Performance optimizations

### Architecture Goals

```typescript
// Future architecture will support:

// Plugin-based format system
interface VisualFormatPlugin {
  name: VisualFormat;
  encoder: FormatEncoder;
  decoder: FormatDecoder;
  capabilities: FormatCapabilities;
}

// Streaming support for large data
interface StreamingEncoder {
  encodeStream(data: ReadableStream<CLIPData>): Promise<ReadableStream<VisualResult>>;
  decodeStream(images: ReadableStream<ImageData>): Promise<ReadableStream<CLIPData>>;
}

// Real-time processing
interface RealtimeDecoder {
  startScanning(video: HTMLVideoElement): void;
  onDetected(callback: (clip: CLIPData) => void): void;
  stopScanning(): void;
}
```

## 📚 API Reference

### Current Interfaces

```typescript
// Core classes (stub implementation)
export class CLIPEncoder {
  encodeToQR(data: CLIPData, options?: QREncodeOptions): Promise<QRCodeResult>;
  encodeToDataMatrix(data: CLIPData, options?: DataMatrixOptions): Promise<DataMatrixResult>;
  encodeToHexMatrix(data: CLIPData, options?: HexMatrixOptions): Promise<HexMatrixResult>;
  encode(data: CLIPData, format: VisualFormat, options?: EncodeOptions): Promise<VisualResult>;
}

export class CLIPDecoder {
  decodeFromQR(image: ImageSource): Promise<CLIPData>;
  decodeFromDataMatrix(image: ImageSource): Promise<CLIPData>;
  decodeFromHexMatrix(image: ImageSource): Promise<CLIPData>;
  decode(image: ImageSource, format?: VisualFormat): Promise<CLIPData>;
}

// Type definitions
export type VisualFormat = 'qr' | 'datamatrix' | 'hexmatrix' | 'aztec' | 'pdf417';
export type ImageSource = ImageData | Buffer | Uint8Array | string;

export interface CLIPData {
  type: string;
  version: string;
  [key: string]: any;
}

export interface EncodeOptions {
  format?: string;
  size?: number | { width: number; height: number };
  errorCorrection?: 'L' | 'M' | 'Q' | 'H';
  margin?: number;
}

export interface VisualResult {
  format: VisualFormat;
  data: string;
  rawData: Buffer;
  metadata: any;
}
```

### Exception Types

```typescript
export class NotImplementedError extends Error {
  constructor(feature: string) {
    super(`${feature} is not yet implemented`);
    this.name = 'NotImplementedError';
  }
}

export class InvalidInputError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'InvalidInputError';
  }
}

export class EncodingError extends Error {
  constructor(message: string, public readonly format: VisualFormat) {
    super(message);
    this.name = 'EncodingError';
  }
}

export class DecodingError extends Error {
  constructor(message: string, public readonly format?: VisualFormat) {
    super(message);
    this.name = 'DecodingError';
  }
}
```

## 🔗 Related

- **[Decoder Library (Python)](../decoder-python/README.md)** - Python implementation
- **[Encoder CLI](../encoder-cli/README.md)** - Command-line tool for CLIP objects
- **[Python SDK](../sdk-python/README.md)** - Python library for CLIP manipulation
- **[Validator Core](../validator-core/README.md)** - Core validation logic

## 📄 License

MIT License - see [LICENSE](../../LICENSE) for details.

---

**Part of the [CLIP Toolkit](../../README.md) ecosystem** 