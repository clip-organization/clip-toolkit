import { SchemaManager, SchemaManagerOptions, SchemaInfo } from './schema-manager';
import { CLIPValidator, CLIPValidatorOptions, ValidationResult } from './clip-validator';

export interface CLIPToolkitOptions {
  schema?: SchemaManagerOptions;
  validator?: CLIPValidatorOptions;
  autoRefreshSchema?: boolean;
  maxSchemaAge?: number; // in milliseconds
}

/**
 * High-level convenience class that combines schema management and validation
 */
export class CLIPToolkit {
  private schemaManager: SchemaManager;
  private validator?: CLIPValidator;
  private lastSchemaFetch: Date | null = null;
  private autoRefreshSchema: boolean;
  private maxSchemaAge: number;

  constructor(options: CLIPToolkitOptions = {}) {
    this.schemaManager = new SchemaManager(options.schema);
    this.autoRefreshSchema = options.autoRefreshSchema !== false; // Default: true
    this.maxSchemaAge = options.maxSchemaAge || 24 * 60 * 60 * 1000; // Default: 24 hours
  }

  /**
   * Validates a CLIP object, automatically fetching/refreshing schema as needed
   */
  async validate(clipObject: any): Promise<ValidationResult> {
    await this.ensureValidator();
    return this.validator!.validate(clipObject);
  }

  /**
   * Validates multiple CLIP objects
   */
  async validateBatch(clipObjects: any[]): Promise<ValidationResult[]> {
    await this.ensureValidator();
    return this.validator!.validateBatch(clipObjects);
  }

  /**
   * Gets the current schema information
   */
  async getSchemaInfo(): Promise<SchemaInfo> {
    return this.schemaManager.getSchema();
  }

  /**
   * Forces a refresh of the schema and validator
   */
  async refreshSchema(): Promise<SchemaInfo> {
    const schemaInfo = await this.schemaManager.refreshCache();
    this.validator = new CLIPValidator(schemaInfo.schema);
    this.lastSchemaFetch = new Date();
    return schemaInfo;
  }

  /**
   * Clears the schema cache
   */
  async clearCache(): Promise<void> {
    await this.schemaManager.clearCache();
    this.validator = undefined;
    this.lastSchemaFetch = null;
  }

  /**
   * Checks if the current validator is using a stale schema
   */
  isSchemaStale(): boolean {
    if (!this.lastSchemaFetch) return true;
    
    const ageMs = Date.now() - this.lastSchemaFetch.getTime();
    return ageMs > this.maxSchemaAge;
  }

  /**
   * Ensures the validator is initialized and schema is fresh
   */
  private async ensureValidator(): Promise<void> {
    const needsUpdate = !this.validator || 
                       (this.autoRefreshSchema && this.isSchemaStale());

    if (needsUpdate) {
      const schemaInfo = await this.schemaManager.getSchema();
      this.validator = new CLIPValidator(schemaInfo.schema);
      this.lastSchemaFetch = new Date();
    }
  }
}

/**
 * Quick validation function for one-off validations
 */
export async function validateCLIP(
  clipObject: any, 
  options?: CLIPToolkitOptions
): Promise<ValidationResult> {
  const toolkit = new CLIPToolkit(options);
  return toolkit.validate(clipObject);
}

/**
 * Quick batch validation function
 */
export async function validateCLIPBatch(
  clipObjects: any[], 
  options?: CLIPToolkitOptions
): Promise<ValidationResult[]> {
  const toolkit = new CLIPToolkit(options);
  return toolkit.validateBatch(clipObjects);
} 