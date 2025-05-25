# @clip-toolkit/validator-core

Core validation and schema management for CLIP (Context Link Interface Protocol).

## Features

- **Schema Fetching**: Automatically fetches the latest CLIP schema from the official repository
- **CLIP Validation**: Validates CLIP objects against JSON Schema with detailed error reporting
- **Caching**: Caches schemas locally for offline use
- **Fallback Strategy**: Tries remote → cache → local schema sources
- **Statistics**: Generates comprehensive statistics about CLIP objects
- **Warnings**: Provides helpful warnings for common issues
- **Batch Validation**: Validates multiple CLIP objects efficiently
- **Error Handling**: Comprehensive error handling with specific error types and suggestions

## Installation

```bash
npm install @clip-toolkit/validator-core
```

## Usage

### Quick Start (Recommended)

```typescript
import { CLIPToolkit } from '@clip-toolkit/validator-core';

const toolkit = new CLIPToolkit();

// Validate a CLIP object (automatically fetches schema)
const clipObject = {
  "@context": "https://clipprotocol.org/v1",
  "type": "Venue",
  "id": "clip:us:ny:coffee:joes-manhattan",
  "name": "Joe's Coffee",
  "description": "Cozy neighborhood coffee shop",
  "lastUpdated": "2023-12-01T10:30:00Z"
};

const result = await toolkit.validate(clipObject);

if (result.valid) {
  console.log('✅ Valid CLIP!');
  console.log(`Completeness: ${result.stats.completeness}%`);
} else {
  console.log('❌ Validation errors:');
  result.errors.forEach(error => {
    console.log(`  ${error.field}: ${error.message}`);
    if (error.suggestion) {
      console.log(`  💡 ${error.suggestion}`);
    }
  });
}

// Check warnings
if (result.warnings?.length) {
  console.log('⚠️ Warnings:');
  result.warnings.forEach(warning => console.log(`  ${warning}`));
}
```

### One-off Validation

```typescript
import { validateCLIP } from '@clip-toolkit/validator-core';

// Quick validation without creating a toolkit instance
const result = await validateCLIP(clipObject);
console.log(`Valid: ${result.valid}, Completeness: ${result.stats.completeness}%`);
```

### Advanced Validation

```typescript
import { CLIPValidator, SchemaManager } from '@clip-toolkit/validator-core';

// Get the schema
const schemaManager = new SchemaManager();
const schemaInfo = await schemaManager.getSchema();

// Create validator with custom options
const validator = new CLIPValidator(schemaInfo.schema, {
  strict: true,
  validateFormats: true
});

// Validate with detailed results
const result = validator.validate(clipObject);

console.log('Validation Result:');
console.log(`Valid: ${result.valid}`);
console.log(`Type: ${result.stats.type}`);
console.log(`Features: ${result.stats.featureCount}`);
console.log(`Actions: ${result.stats.actionCount}`);
console.log(`Estimated size: ${result.stats.estimatedSize} bytes`);

// Handle specific error types
result.errors.forEach(error => {
  switch (error.severity) {
    case 'error':
      console.error(`❌ ${error.field}: ${error.message}`);
      break;
    case 'warning':
      console.warn(`⚠️ ${error.field}: ${error.message}`);
      break;
  }
});
```

### Batch Validation

```typescript
import { CLIPToolkit } from '@clip-toolkit/validator-core';

const toolkit = new CLIPToolkit();
const clipObjects = [clip1, clip2, clip3];

const results = await toolkit.validateBatch(clipObjects);

results.forEach((result, index) => {
  console.log(`CLIP ${index + 1}: ${result.valid ? '✅' : '❌'}`);
  if (!result.valid) {
    console.log(`  Errors: ${result.errors.length}`);
  }
});
```

### Basic Schema Management

```typescript
import { SchemaManager } from '@clip-toolkit/validator-core';

const schemaManager = new SchemaManager();

// Get the latest schema (tries remote, falls back to cache)
const schemaInfo = await schemaManager.getSchema();

console.log(`Schema version: ${schemaInfo.version}`);
console.log(`Source: ${schemaInfo.source}`); // 'remote', 'cache', or 'local'
console.log(`Last fetched: ${schemaInfo.lastFetched}`);
```

### Custom Configuration

```typescript
import { SchemaManager } from '@clip-toolkit/validator-core';

const schemaManager = new SchemaManager({
  cachePath: '/custom/cache/path',
  remoteUrl: 'https://custom-schema-url.com/schema.json',
  localSchemaPath: './local-schema.json'
});

// Force refresh the cache
await schemaManager.refreshCache();

// Check if cache is stale (older than 1 hour)
const isStale = schemaManager.isCacheStale(60 * 60 * 1000);

// Clear the cache
await schemaManager.clearCache();
```

### Error Handling

```typescript
import { 
  SchemaManager, 
  SchemaFetchError, 
  SchemaCacheError 
} from '@clip-toolkit/validator-core';

try {
  const schema = await schemaManager.getSchema();
} catch (error) {
  if (error instanceof SchemaFetchError) {
    console.error('Failed to fetch schema:', error.url, error.statusCode);
  } else if (error instanceof SchemaCacheError) {
    console.error('Cache error:', error.cachePath);
  }
}
```

## API Reference

### CLIPToolkit (Recommended)

High-level interface that combines schema management and validation.

#### Constructor Options

```typescript
interface CLIPToolkitOptions {
  schema?: SchemaManagerOptions;
  validator?: CLIPValidatorOptions;
  autoRefreshSchema?: boolean; // Default: true
  maxSchemaAge?: number; // Default: 24 hours
}
```

#### Methods

- `validate(clipObject: any): Promise<ValidationResult>` - Validate a CLIP object
- `validateBatch(clipObjects: any[]): Promise<ValidationResult[]>` - Validate multiple objects
- `getSchemaInfo(): Promise<SchemaInfo>` - Get current schema information
- `refreshSchema(): Promise<SchemaInfo>` - Force refresh schema
- `clearCache(): Promise<void>` - Clear schema cache
- `isSchemaStale(): boolean` - Check if schema needs refresh

### CLIPValidator

Core validation engine using Ajv.

#### Constructor

```typescript
new CLIPValidator(schema: object, options?: CLIPValidatorOptions)
```

#### Options

```typescript
interface CLIPValidatorOptions {
  strict?: boolean; // Default: true
  allowUnknownFields?: boolean; // Default: false
  validateFormats?: boolean; // Default: true
}
```

#### Methods

- `validate(clipObject: any): ValidationResult` - Validate a CLIP object
- `validateBatch(clipObjects: any[]): ValidationResult[]` - Validate multiple objects

### SchemaManager

Low-level schema fetching and caching.

#### Constructor Options

- `cachePath?: string` - Path to cache directory (default: `~/.clip-toolkit/schemas`)
- `remoteUrl?: string` - URL to fetch schema from (default: official CLIP schema)
- `localSchemaPath?: string` - Path to local fallback schema

#### Methods

- `getSchema(): Promise<SchemaInfo>` - Get schema with fallback strategy
- `fetchLatestSchema(): Promise<SchemaInfo>` - Fetch directly from remote
- `getCachedSchema(): SchemaInfo` - Get from cache only
- `getLocalSchema(): SchemaInfo` - Get from local file only
- `isCacheStale(maxAge?: number): boolean` - Check if cache is stale
- `refreshCache(): Promise<SchemaInfo>` - Force refresh cache
- `clearCache(): Promise<void>` - Clear cache files

### Types

```typescript
interface ValidationResult {
  valid: boolean;
  errors: FormattedError[];
  stats: CLIPStats;
  warnings?: string[];
}

interface FormattedError {
  field: string;
  message: string;
  value?: any;
  suggestion?: string;
  severity: 'error' | 'warning';
}

interface CLIPStats {
  type: string;
  hasLocation: boolean;
  featureCount: number;
  actionCount: number;
  serviceCount: number;
  hasPersona: boolean;
  estimatedSize: number; // in bytes
  lastUpdated?: string;
  completeness: number; // 0-100 percentage
}

interface SchemaInfo {
  schema: object;
  version: string;
  lastFetched: Date;
  source: 'remote' | 'cache' | 'local';
}
```

### Convenience Functions

```typescript
// Quick validation functions
validateCLIP(clipObject: any, options?: CLIPToolkitOptions): Promise<ValidationResult>
validateCLIPBatch(clipObjects: any[], options?: CLIPToolkitOptions): Promise<ValidationResult[]>
```

## Development

```bash
# Build
npm run build

# Test
npm run test

# Watch mode
npm run dev
```

## License

MIT 