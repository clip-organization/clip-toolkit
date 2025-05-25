export { SchemaManager, SchemaManagerOptions, SchemaInfo, CachedSchema } from './schema-manager';
export { 
  CLIPValidator, 
  CLIPValidatorOptions, 
  ValidationResult, 
  FormattedError, 
  CLIPStats 
} from './clip-validator';
export { 
  CLIPToolkit, 
  CLIPToolkitOptions, 
  validateCLIP, 
  validateCLIPBatch 
} from './clip-toolkit';

// Error classes for better error handling
export class CLIPValidationError extends Error {
  constructor(message: string, public details?: any) {
    super(message);
    this.name = 'CLIPValidationError';
  }
}

export class SchemaFetchError extends Error {
  constructor(message: string, public url?: string, public statusCode?: number) {
    super(message);
    this.name = 'SchemaFetchError';
  }
}

export class SchemaCacheError extends Error {
  constructor(message: string, public cachePath?: string) {
    super(message);
    this.name = 'SchemaCacheError';
  }
} 