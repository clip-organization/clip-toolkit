# CLIP Validator Core

Core validation logic for CLIP (Context Link Interface Protocol) objects. This TypeScript library provides the foundational validation engine used across the CLIP Toolkit ecosystem.

[![npm version](https://badge.fury.io/js/%40clip%2Fvalidator-core.svg)](https://badge.fury.io/js/%40clip%2Fvalidator-core)
[![TypeScript CI](https://github.com/your-org/clip-toolkit/workflows/TypeScript%20CI/badge.svg)](https://github.com/your-org/clip-toolkit/actions)

## 🚀 Quick Start

### Installation

```bash
# npm
npm install @clip/validator-core

# yarn
yarn add @clip/validator-core

# pnpm
pnpm add @clip/validator-core
```

### Basic Usage

```typescript
import { CLIPValidator, ValidationOptions } from '@clip/validator-core';

// Create validator
const validator = new CLIPValidator();

// Validate CLIP object
const clipData = {
  type: 'venue',
  version: '1.0.0',
  name: 'Example Venue',
  // ... more CLIP data
};

const result = await validator.validate(clipData);

if (result.isValid) {
  console.log('✅ CLIP is valid!');
  console.log(`Score: ${result.score}/100`);
} else {
  console.log('❌ Validation errors:');
  result.errors.forEach(error => {
    console.log(`  - ${error.path}: ${error.message}`);
  });
}
```

## 📦 Core Features

### CLIPValidator

The main validation engine with comprehensive error reporting:

```typescript
import { CLIPValidator, ValidationOptions } from '@clip/validator-core';

// Configure validator
const options: ValidationOptions = {
  strictMode: true,
  schemaVersion: '1.0.0',
  allowRemoteRefs: false,
  customRules: []
};

const validator = new CLIPValidator(options);

// Validate single object
const result = await validator.validate(clipData);

// Batch validation
const results = await validator.validateBatch([clip1, clip2, clip3]);

// Validate with custom schema
const customResult = await validator.validateWithSchema(clipData, customSchema);
```

### Schema Management

```typescript
import { SchemaManager, SchemaLoader } from '@clip/validator-core';

// Load official CLIP schema
const schemaManager = new SchemaManager();
const schema = await schemaManager.loadSchema('1.0.0');

// Load custom schema
const customSchema = await schemaManager.loadFromUrl('https://example.com/schema.json');

// Cache schemas for performance
schemaManager.enableCache(true);
const cachedSchema = await schemaManager.loadSchema('1.0.0'); // Uses cache
```

### Custom Validation Rules

```typescript
import { ValidationRule, RuleContext, RuleResult } from '@clip/validator-core';

// Define custom rule
const venueCoordinatesRule: ValidationRule = {
  name: 'venue-coordinates',
  description: 'Venues must have valid coordinates',
  
  applies: (context: RuleContext): boolean => {
    return context.data.type === 'venue';
  },
  
  validate: (context: RuleContext): RuleResult => {
    const location = context.data.location;
    const coords = location?.coordinates;
    
    if (!coords) {
      return {
        valid: false,
        severity: 'error',
        message: 'Venues must include coordinates',
        path: 'location.coordinates'
      };
    }
    
    const { latitude, longitude } = coords;
    if (latitude < -90 || latitude > 90 || longitude < -180 || longitude > 180) {
      return {
        valid: false,
        severity: 'error',
        message: 'Invalid coordinate values',
        path: 'location.coordinates'
      };
    }
    
    return { valid: true };
  }
};

// Use custom rule
const validator = new CLIPValidator({
  customRules: [venueCoordinatesRule]
});
```

## 🔧 Advanced Usage

### Async Validation

```typescript
import { CLIPValidator, AsyncValidationOptions } from '@clip/validator-core';

// Configure for async validation
const validator = new CLIPValidator({
  async: true,
  concurrency: 5, // Max concurrent validations
  timeout: 30000  // 30 second timeout
});

// Validate multiple objects concurrently
const urls = [
  'https://example.com/venue1.json',
  'https://example.com/venue2.json',
  'https://example.com/venue3.json'
];

const results = await Promise.all(
  urls.map(url => validator.validateFromUrl(url))
);

results.forEach((result, index) => {
  console.log(`${urls[index]}: ${result.isValid ? '✅' : '❌'}`);
});
```

### Error Handling and Reporting

```typescript
import { ValidationError, ErrorSeverity } from '@clip/validator-core';

const result = await validator.validate(clipData);

// Group errors by severity
const errorsBySeverity = result.errors.reduce((acc, error) => {
  if (!acc[error.severity]) acc[error.severity] = [];
  acc[error.severity].push(error);
  return acc;
}, {} as Record<ErrorSeverity, ValidationError[]>);

// Generate detailed report
const report = {
  summary: {
    valid: result.isValid,
    score: result.score,
    totalErrors: result.errors.length,
    critical: errorsBySeverity.critical?.length || 0,
    errors: errorsBySeverity.error?.length || 0,
    warnings: errorsBySeverity.warning?.length || 0
  },
  
  errors: result.errors.map(error => ({
    path: error.path,
    message: error.message,
    severity: error.severity,
    code: error.code,
    suggestion: error.suggestion
  }))
};

console.log(JSON.stringify(report, null, 2));
```

### Performance Optimization

```typescript
import { CLIPValidator, PerformanceOptions } from '@clip/validator-core';

// Configure for high performance
const validator = new CLIPValidator({
  performance: {
    enableCache: true,
    cacheSize: 1000,
    parallelValidation: true,
    skipOptionalValidation: false,
    fastFail: false // Continue validation after first error
  }
});

// Benchmark validation performance
const startTime = performance.now();
const result = await validator.validate(largeClipData);
const endTime = performance.now();

console.log(`Validation took ${endTime - startTime} milliseconds`);
console.log(`Performance score: ${result.performanceMetrics?.score}`);
```

## 🧪 Testing

### Unit Testing

```typescript
import { CLIPValidator } from '@clip/validator-core';
import { describe, it, expect } from '@jest/globals';

describe('CLIPValidator', () => {
  const validator = new CLIPValidator();
  
  it('should validate a valid venue CLIP', async () => {
    const venueData = {
      type: 'venue',
      version: '1.0.0',
      name: 'Test Venue',
      location: {
        coordinates: {
          latitude: 40.7589,
          longitude: -73.9851
        }
      }
    };
    
    const result = await validator.validate(venueData);
    
    expect(result.isValid).toBe(true);
    expect(result.score).toBeGreaterThan(80);
    expect(result.errors).toHaveLength(0);
  });
  
  it('should detect missing required fields', async () => {
    const invalidData = {
      type: 'venue'
      // Missing required fields
    };
    
    const result = await validator.validate(invalidData);
    
    expect(result.isValid).toBe(false);
    expect(result.errors.length).toBeGreaterThan(0);
    expect(result.errors[0].path).toContain('version');
  });
  
  it('should handle custom validation rules', async () => {
    const customRule = {
      name: 'test-rule',
      applies: () => true,
      validate: () => ({ valid: false, message: 'Test error' })
    };
    
    const validator = new CLIPValidator({
      customRules: [customRule]
    });
    
    const result = await validator.validate({ type: 'venue' });
    
    expect(result.isValid).toBe(false);
    expect(result.errors.some(e => e.message === 'Test error')).toBe(true);
  });
});
```

### Integration Testing

```typescript
import { CLIPValidator, SchemaManager } from '@clip/validator-core';

describe('Integration Tests', () => {
  it('should validate against remote schema', async () => {
    const schemaManager = new SchemaManager();
    const schema = await schemaManager.loadFromUrl(
      'https://schema.clipprotocol.org/v1/clip.schema.json'
    );
    
    const validator = new CLIPValidator();
    const result = await validator.validateWithSchema(clipData, schema);
    
    expect(result).toBeDefined();
  });
  
  it('should handle network timeouts gracefully', async () => {
    const validator = new CLIPValidator({ timeout: 100 }); // Very short timeout
    
    const result = await validator.validateFromUrl(
      'https://httpbin.org/delay/5' // 5 second delay
    );
    
    expect(result.errors[0].code).toBe('NETWORK_TIMEOUT');
  });
});
```

## 📊 Performance Benchmarks

### Benchmark Results

Validation performance on typical CLIP objects:

- **Simple CLIP** (< 1KB): ~0.5ms
- **Medium CLIP** (1-10KB): ~2-5ms
- **Complex CLIP** (10-50KB): ~10-25ms
- **Large CLIP** (50KB+): ~50-100ms

### Running Benchmarks

```bash
# Install dependencies
npm install

# Run performance tests
npm run benchmark

# Run memory profiling
npm run profile
```

### Custom Benchmarks

```typescript
import { CLIPValidator, BenchmarkSuite } from '@clip/validator-core';

const suite = new BenchmarkSuite();

// Add benchmark cases
suite.add('Simple Venue Validation', async () => {
  const validator = new CLIPValidator();
  await validator.validate(simpleVenueData);
});

suite.add('Complex Event Validation', async () => {
  const validator = new CLIPValidator();
  await validator.validate(complexEventData);
});

// Run benchmarks
const results = await suite.run();
console.log(results.summary);
```

## 🔌 Integration

### Express.js Integration

```typescript
import express from 'express';
import { CLIPValidator } from '@clip/validator-core';

const app = express();
const validator = new CLIPValidator();

app.use(express.json());

app.post('/validate', async (req, res) => {
  try {
    const result = await validator.validate(req.body);
    
    res.json({
      valid: result.isValid,
      score: result.score,
      errors: result.errors.map(e => ({
        path: e.path,
        message: e.message,
        severity: e.severity
      }))
    });
  } catch (error) {
    res.status(500).json({ error: 'Validation failed' });
  }
});
```

### Next.js API Route

```typescript
// pages/api/validate.ts
import type { NextApiRequest, NextApiResponse } from 'next';
import { CLIPValidator } from '@clip/validator-core';

const validator = new CLIPValidator();

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ message: 'Method not allowed' });
  }
  
  try {
    const result = await validator.validate(req.body);
    
    res.status(200).json({
      valid: result.isValid,
      score: result.score,
      errors: result.errors
    });
  } catch (error) {
    res.status(500).json({ error: 'Validation failed' });
  }
}
```

### Browser Usage

```html
<!DOCTYPE html>
<html>
<head>
  <title>CLIP Validator</title>
  <script src="https://unpkg.com/@clip/validator-core/dist/browser.js"></script>
</head>
<body>
  <script>
    const validator = new CLIPValidatorCore.CLIPValidator();
    
    async function validateClip(clipData) {
      const result = await validator.validate(clipData);
      
      if (result.isValid) {
        console.log('✅ Valid CLIP');
      } else {
        console.log('❌ Invalid CLIP:', result.errors);
      }
    }
    
    // Example usage
    validateClip({
      type: 'venue',
      version: '1.0.0',
      name: 'Browser Test Venue'
    });
  </script>
</body>
</html>
```

## 📚 API Reference

### CLIPValidator

```typescript
class CLIPValidator {
  constructor(options?: ValidationOptions);
  
  validate(data: unknown): Promise<ValidationResult>;
  validateBatch(data: unknown[]): Promise<ValidationResult[]>;
  validateWithSchema(data: unknown, schema: JSONSchema): Promise<ValidationResult>;
  validateFromUrl(url: string): Promise<ValidationResult>;
  
  addRule(rule: ValidationRule): void;
  removeRule(name: string): void;
  getRules(): ValidationRule[];
  
  getSchema(): JSONSchema | null;
  setSchema(schema: JSONSchema): void;
}
```

### ValidationResult

```typescript
interface ValidationResult {
  isValid: boolean;
  score: number; // 0-100
  errors: ValidationError[];
  warnings: ValidationError[];
  performanceMetrics?: PerformanceMetrics;
}
```

### ValidationError

```typescript
interface ValidationError {
  path: string;
  message: string;
  severity: 'critical' | 'error' | 'warning';
  code: string;
  value?: unknown;
  expected?: unknown;
  suggestion?: string;
}
```

### ValidationOptions

```typescript
interface ValidationOptions {
  strictMode?: boolean;
  schemaVersion?: string;
  allowRemoteRefs?: boolean;
  timeout?: number;
  customRules?: ValidationRule[];
  performance?: PerformanceOptions;
}
```

## 🔧 Configuration

### Environment Variables

```bash
# Schema configuration
CLIP_SCHEMA_URL=https://schema.clipprotocol.org/v1/clip.schema.json
CLIP_SCHEMA_CACHE_ENABLED=true
CLIP_SCHEMA_CACHE_TTL=3600

# Validation configuration
CLIP_STRICT_MODE=false
CLIP_ALLOW_REMOTE_REFS=true
CLIP_VALIDATION_TIMEOUT=30000

# Performance configuration
CLIP_ENABLE_CACHE=true
CLIP_CACHE_SIZE=1000
CLIP_PARALLEL_VALIDATION=true
```

### Configuration File

Create `clip.config.js`:

```javascript
module.exports = {
  validation: {
    strictMode: false,
    schemaVersion: '1.0.0',
    allowRemoteRefs: true,
    timeout: 30000
  },
  
  performance: {
    enableCache: true,
    cacheSize: 1000,
    parallelValidation: true,
    fastFail: false
  },
  
  customRules: [
    // Load custom rules from files
    require('./rules/venue-rules'),
    require('./rules/event-rules')
  ]
};
```

## 🐛 Troubleshooting

### Common Issues

**Schema Loading Errors**
```typescript
import { CLIPValidator, SchemaManager } from '@clip/validator-core';

try {
  const validator = new CLIPValidator();
  const result = await validator.validate(data);
} catch (error) {
  if (error.code === 'SCHEMA_LOAD_FAILED') {
    console.log('Failed to load schema:', error.message);
    // Fallback to local schema
    const localSchema = require('./local-schema.json');
    const result = await validator.validateWithSchema(data, localSchema);
  }
}
```

**Memory Issues with Large Objects**
```typescript
// Use streaming validation for large objects
const validator = new CLIPValidator({
  performance: {
    streamingValidation: true,
    maxObjectSize: 10 * 1024 * 1024 // 10MB limit
  }
});
```

**TypeScript Type Issues**
```typescript
// Ensure proper types
import type { CLIPData, ValidationResult } from '@clip/validator-core';

const clipData: CLIPData = {
  type: 'venue',
  version: '1.0.0',
  name: 'Typed Venue'
};

const result: ValidationResult = await validator.validate(clipData);
```

## 🔗 Related

- **[Encoder CLI](../encoder-cli/README.md)** - Command-line tool using this validator
- **[Python SDK](../sdk-python/README.md)** - Python implementation
- **[Decoder Library](../decoder-lib/README.md)** - Visual encoding/decoding

## 📄 License

MIT License - see [LICENSE](../../LICENSE) for details.

---

**Part of the [CLIP Toolkit](../../README.md) ecosystem** 