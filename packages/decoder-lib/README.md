# @clip-toolkit/decoder-lib

[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue.svg)](https://www.typescriptlang.org/)
[![Node.js](https://img.shields.io/badge/Node.js-18+-green.svg)](https://nodejs.org/)
[![Jest](https://img.shields.io/badge/Test-Jest-red.svg)](https://jestjs.io/)

**Stub Implementation** - Visual CLIP representation decoder library for TypeScript/Node.js

> ⚠️ **Note**: This is currently a stub implementation. Visual encoding/decoding features are planned for a future release.

## Overview

The CLIP Decoder Library provides placeholder implementations for encoding and decoding visual CLIP representations, including QR codes and HexMatrix formats. This stub implementation defines the interfaces and validates parameters while throwing "Not implemented" errors for the actual encoding/decoding operations.

## Installation

```bash
npm install @clip-toolkit/decoder-lib
```

## Usage

### Basic Import

```typescript
import {
  decodeVisual,
  encodeVisual,
  isFormatSupported,
  getLibraryInfo,
  DecodeOptions,
  EncodeOptions,
  VisualData,
  CLIPObject
} from '@clip-toolkit/decoder-lib';
```

### Decode Visual CLIP (Stub)

```typescript
import { decodeVisual, DecodeOptions } from '@clip-toolkit/decoder-lib';

const imageData = new Uint8Array([/* QR code or HexMatrix data */]);
const options: DecodeOptions = {
  format: 'qr',
  errorCorrection: 'medium'
};

try {
  const clipObject = decodeVisual(imageData, options);
  // This will throw: "Not implemented: Visual CLIP decoding is planned for a future release"
} catch (error) {
  console.log('Expected:', error.message);
}
```

### Encode CLIP Object (Stub)

```typescript
import { encodeVisual, EncodeOptions } from '@clip-toolkit/decoder-lib';

const clipObject: CLIPObject = {
  '@context': 'https://clipprotocol.org/v1',
  type: 'Venue',
  id: 'clip:venue:example-123',
  name: 'Example Venue',
  description: 'A sample venue for demonstration'
};

const options: EncodeOptions = {
  format: 'qr',
  errorCorrection: 'high',
  size: 256
};

try {
  const visualData = encodeVisual(clipObject, options);
  // This will throw: "Not implemented: Visual CLIP encoding is planned for a future release"
} catch (error) {
  console.log('Expected:', error.message);
}
```

### Check Format Support

```typescript
import { isFormatSupported, getLibraryInfo } from '@clip-toolkit/decoder-lib';

console.log(isFormatSupported('qr'));        // true (planned)
console.log(isFormatSupported('hexmatrix')); // true (planned)
console.log(isFormatSupported('barcode'));   // false

const info = getLibraryInfo();
console.log(info);
// {
//   name: '@clip-toolkit/decoder-lib',
//   version: '0.1.0',
//   status: 'stub-implementation',
//   supportedFormats: []
// }
```

## API Reference

### Interfaces

#### `DecodeOptions`
```typescript
interface DecodeOptions {
  format?: 'qr' | 'hexmatrix';
  errorCorrection?: 'low' | 'medium' | 'high';
  strictMode?: boolean;
}
```

#### `EncodeOptions`
```typescript
interface EncodeOptions {
  format: 'qr' | 'hexmatrix';
  errorCorrection?: 'low' | 'medium' | 'high';
  size?: number;
  margin?: number;
}
```

#### `VisualData`
```typescript
interface VisualData {
  format: string;
  data: Uint8Array | string;
  width?: number;
  height?: number;
  metadata?: {
    version?: string;
    timestamp?: string;
    [key: string]: any;
  };
}
```

#### `CLIPObject`
```typescript
interface CLIPObject {
  '@context': string;
  type: string;
  id: string;
  name: string;
  description: string;
  [key: string]: any;
}
```

### Functions

#### `decodeVisual(imageData, options?)`
Placeholder for decoding visual CLIP representations.

**Parameters:**
- `imageData: Uint8Array | string` - Image data to decode
- `options?: DecodeOptions` - Decode options

**Returns:** `CLIPObject` (when implemented)

**Throws:** `NotImplementedError` - This is a stub implementation

#### `encodeVisual(clipObject, options)`
Placeholder for encoding CLIP objects as visual representations.

**Parameters:**
- `clipObject: CLIPObject` - CLIP object to encode
- `options: EncodeOptions` - Encode options

**Returns:** `VisualData` (when implemented)

**Throws:** `NotImplementedError` - This is a stub implementation

#### `isFormatSupported(format)`
Check if a format is planned to be supported.

**Parameters:**
- `format: string` - Format name to check

**Returns:** `boolean` - True if format is recognized

#### `getLibraryInfo()`
Get information about the decoder library.

**Returns:** Library information object

## Development

### Build

```bash
npm run build
```

### Test

```bash
npm test
```

### Watch Mode

```bash
npm run dev
```

### Linting

```bash
npm run lint
```

### Clean

```bash
npm run clean
```

## Test Coverage

The stub implementation includes comprehensive tests covering:

- ✅ Interface exports and type safety
- ✅ Parameter validation
- ✅ Error handling and expected exceptions
- ✅ Function existence and callability
- ✅ Consistent return values

**Test Results:** 22/22 tests passing (100% success rate)

## Planned Features

When the full implementation is available, this library will support:

### Visual Formats
- **QR Codes**: Standard QR code generation and reading
- **HexMatrix**: Custom hexagonal matrix format for CLIP

### Encoding Features
- Multiple error correction levels
- Customizable size and margins
- Metadata embedding
- Format-specific optimizations

### Decoding Features
- Automatic format detection
- Error correction and recovery
- Strict/lenient parsing modes
- Batch processing support

## Error Handling

The stub implementation provides proper parameter validation:

```typescript
// These will throw validation errors
decodeVisual('');                                    // "Image data is required"
decodeVisual(data, { format: 'invalid' });         // "Invalid format specified"
encodeVisual(null, options);                        // "CLIP object is required"
encodeVisual(clip, { format: 'invalid' });         // "Invalid format specified"
encodeVisual(incompleteClip, options);              // "Required CLIP field missing: [field]"
```

## Contributing

This is part of the CLIP Toolkit monorepo. See the main repository for contribution guidelines.

## License

MIT © CLIP Organization

## Related Packages

- `@clip-toolkit/validator-core` - CLIP object validation
- `@clip-toolkit/encoder-cli` - Command-line encoding tools
- `clip-sdk` - Python SDK for CLIP operations 