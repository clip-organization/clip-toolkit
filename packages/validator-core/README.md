# @clip-toolkit/validator-core

Core validation and schema management for CLIP (Context Link Interface Protocol).

## Features

- **Schema Fetching**: Automatically fetches the latest CLIP schema from the official repository
- **Caching**: Caches schemas locally for offline use
- **Fallback Strategy**: Tries remote → cache → local schema sources
- **Version Tracking**: Tracks schema versions and update times
- **Error Handling**: Comprehensive error handling with specific error types

## Installation

```bash
npm install @clip-toolkit/validator-core
```

## Usage

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

### SchemaManager

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
interface SchemaInfo {
  schema: object;
  version: string;
  lastFetched: Date;
  source: 'remote' | 'cache' | 'local';
}

interface SchemaManagerOptions {
  cachePath?: string;
  remoteUrl?: string;
  localSchemaPath?: string;
}
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