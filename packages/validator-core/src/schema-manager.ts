import axios, { AxiosResponse } from 'axios';
import * as fs from 'fs-extra';
import * as path from 'path';
import * as os from 'os';

export interface SchemaManagerOptions {
  cachePath?: string;
  remoteUrl?: string;
  localSchemaPath?: string;
}

export interface SchemaInfo {
  schema: object;
  version: string;
  lastFetched: Date;
  source: 'remote' | 'cache' | 'local';
}

export interface CachedSchema {
  schema: object;
  version: string;
  lastFetched: string;
  url: string;
}

export class SchemaManager {
  private cachePath: string;
  private remoteUrl: string;
  private localSchemaPath?: string;
  private schemaFileName = 'clip.schema.json';
  private metadataFileName = 'schema-metadata.json';

  constructor(options: SchemaManagerOptions = {}) {
    this.cachePath = options.cachePath || path.join(os.homedir(), '.clip-toolkit', 'schemas');
    this.remoteUrl = options.remoteUrl || 'https://raw.githubusercontent.com/clip-organization/spec/main/clip.schema.json';
    this.localSchemaPath = options.localSchemaPath;
    
    // Ensure cache directory exists
    fs.ensureDirSync(this.cachePath);
  }

  /**
   * Gets the CLIP schema, trying remote first, then cache, then local fallback
   */
  async getSchema(): Promise<SchemaInfo> {
    try {
      return await this.fetchLatestSchema();
    } catch (error) {
      console.warn('Failed to fetch latest schema from remote:', error instanceof Error ? error.message : error);
      
      try {
        return this.getCachedSchema();
      } catch (cacheError) {
        console.warn('Failed to load cached schema:', cacheError instanceof Error ? cacheError.message : cacheError);
        
        if (this.localSchemaPath) {
          return this.getLocalSchema();
        }
        
        throw new Error('Unable to load CLIP schema from any source (remote, cache, or local)');
      }
    }
  }

  /**
   * Fetches the latest schema from the remote URL
   */
  async fetchLatestSchema(): Promise<SchemaInfo> {
    const response: AxiosResponse = await axios.get(this.remoteUrl, {
      timeout: 10000,
      headers: {
        'Accept': 'application/json',
        'User-Agent': 'clip-toolkit-validator-core'
      }
    });

    if (response.status !== 200) {
      throw new Error(`HTTP ${response.status}: Failed to fetch schema`);
    }

    const schema = response.data;
    
    // Validate that this looks like a JSON Schema
    if (!schema || typeof schema !== 'object' || !schema.$schema) {
      throw new Error('Invalid schema format: missing $schema property');
    }

    // Extract version from schema or use timestamp
    const version = this.extractSchemaVersion(schema);
    const lastFetched = new Date();

    // Cache the schema
    await this.cacheSchema(schema, version, lastFetched);

    return {
      schema,
      version,
      lastFetched,
      source: 'remote'
    };
  }

  /**
   * Gets the cached schema
   */
  getCachedSchema(): SchemaInfo {
    const schemaPath = path.join(this.cachePath, this.schemaFileName);
    const metadataPath = path.join(this.cachePath, this.metadataFileName);

    if (!fs.existsSync(schemaPath) || !fs.existsSync(metadataPath)) {
      throw new Error('No cached schema found');
    }

    const schema = fs.readJsonSync(schemaPath);
    const metadata: CachedSchema = fs.readJsonSync(metadataPath);

    return {
      schema,
      version: metadata.version,
      lastFetched: new Date(metadata.lastFetched),
      source: 'cache'
    };
  }

  /**
   * Gets the local schema (development/fallback)
   */
  getLocalSchema(): SchemaInfo {
    if (!this.localSchemaPath || !fs.existsSync(this.localSchemaPath)) {
      throw new Error('Local schema path not provided or file does not exist');
    }

    const schema = fs.readJsonSync(this.localSchemaPath);
    const version = this.extractSchemaVersion(schema);

    return {
      schema,
      version,
      lastFetched: new Date(0), // Unix epoch to indicate it's not freshly fetched
      source: 'local'
    };
  }

  /**
   * Checks if the cached schema is stale (older than maxAge milliseconds)
   */
  isCacheStale(maxAge: number = 24 * 60 * 60 * 1000): boolean { // Default: 24 hours
    try {
      const metadata = this.getCachedSchemaMetadata();
      const ageMs = Date.now() - new Date(metadata.lastFetched).getTime();
      return ageMs > maxAge;
    } catch {
      return true; // If we can't read metadata, consider cache stale
    }
  }

  /**
   * Forces a refresh of the cached schema
   */
  async refreshCache(): Promise<SchemaInfo> {
    return this.fetchLatestSchema();
  }

  /**
   * Gets information about the currently cached schema
   */
  getCachedSchemaInfo(): SchemaInfo | null {
    try {
      return this.getCachedSchema();
    } catch {
      return null;
    }
  }

  /**
   * Clears the schema cache
   */
  async clearCache(): Promise<void> {
    const schemaPath = path.join(this.cachePath, this.schemaFileName);
    const metadataPath = path.join(this.cachePath, this.metadataFileName);

    await Promise.all([
      fs.remove(schemaPath).catch(() => {}), // Ignore errors if files don't exist
      fs.remove(metadataPath).catch(() => {})
    ]);
  }

  /**
   * Caches the schema to disk
   */
  private async cacheSchema(schema: object, version: string, lastFetched: Date): Promise<void> {
    const schemaPath = path.join(this.cachePath, this.schemaFileName);
    const metadataPath = path.join(this.cachePath, this.metadataFileName);

    const metadata: CachedSchema = {
      schema: schema,
      version,
      lastFetched: lastFetched.toISOString(),
      url: this.remoteUrl
    };

    await Promise.all([
      fs.writeJson(schemaPath, schema, { spaces: 2 }),
      fs.writeJson(metadataPath, metadata, { spaces: 2 })
    ]);
  }

  /**
   * Gets cached schema metadata
   */
  private getCachedSchemaMetadata(): CachedSchema {
    const metadataPath = path.join(this.cachePath, this.metadataFileName);
    return fs.readJsonSync(metadataPath);
  }

  /**
   * Extracts version information from the schema
   */
  private extractSchemaVersion(schema: any): string {
    // Try to get version from $id URL
    if (schema.$id && typeof schema.$id === 'string') {
      const versionMatch = schema.$id.match(/\/v(\d+(?:\.\d+)*)/);
      if (versionMatch) {
        return versionMatch[1];
      }
    }

    // Try to get from title or description
    if (schema.title && typeof schema.title === 'string') {
      const versionMatch = schema.title.match(/v(\d+(?:\.\d+)*(?:-\w+)?)/i);
      if (versionMatch) {
        return versionMatch[1];
      }
    }

    // Fallback to current timestamp
    return new Date().toISOString();
  }
} 