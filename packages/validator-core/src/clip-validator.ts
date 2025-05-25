import Ajv, { ErrorObject, ValidateFunction } from 'ajv';
import addFormats from 'ajv-formats';

export interface ValidationResult {
  valid: boolean;
  errors: FormattedError[];
  stats: CLIPStats;
  warnings?: string[];
}

export interface FormattedError {
  field: string;
  message: string;
  value?: any;
  suggestion?: string;
  severity: 'error' | 'warning';
}

export interface CLIPStats {
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

export interface CLIPValidatorOptions {
  strict?: boolean;
  allowUnknownFields?: boolean;
  validateFormats?: boolean;
}

export class CLIPValidator {
  private ajv: Ajv;
  private schema: object;
  private validateFunction: ValidateFunction;

  constructor(schema: object, options: CLIPValidatorOptions = {}) {
    this.schema = schema;
    
    // Configure Ajv with appropriate options
    this.ajv = new Ajv({
      allErrors: true, // Collect all errors, not just the first one
      verbose: true, // Include schema and data references in errors
      strict: options.strict !== false, // Enable strict mode by default
      validateFormats: options.validateFormats !== false, // Validate formats by default
      removeAdditional: false, // Don't remove additional properties
      allowUnionTypes: true
    });

    // Add format validators (date-time, uri, etc.)
    addFormats(this.ajv);

    // Compile the schema
    try {
      this.validateFunction = this.ajv.compile(this.schema);
    } catch (error) {
      throw new Error(`Invalid CLIP schema: ${error instanceof Error ? error.message : error}`);
    }
  }

  /**
   * Validates a CLIP object against the schema
   */
  validate(clipObject: any): ValidationResult {
    // Perform schema validation
    const valid = this.validateFunction(clipObject);
    const ajvErrors = this.validateFunction.errors || [];

    // Format errors for better user experience
    const errors = this.formatErrors(ajvErrors);
    
    // Generate warnings for common issues
    const warnings = this.generateWarnings(clipObject);

    // Generate statistics about the CLIP object
    const stats = this.generateStats(clipObject);

    return {
      valid,
      errors,
      stats,
      warnings
    };
  }

  /**
   * Validates multiple CLIP objects
   */
  validateBatch(clipObjects: any[]): ValidationResult[] {
    return clipObjects.map(obj => this.validate(obj));
  }

  /**
   * Formats Ajv errors into user-friendly messages
   */
  private formatErrors(errors: ErrorObject[]): FormattedError[] {
    return errors.map(error => {
      const field = error.instancePath || error.schemaPath || 'root';
      let message = error.message || 'Validation error';
      let suggestion: string | undefined;

      // Customize error messages based on error type
      switch (error.keyword) {
        case 'required':
          const missingField = error.params?.missingProperty;
          message = `Missing required field: ${missingField}`;
          suggestion = this.getRequiredFieldSuggestion(missingField);
          break;

        case 'type':
          const expectedType = error.params?.type;
          message = `Expected ${expectedType}, got ${typeof error.data}`;
          suggestion = this.getTypeSuggestion(expectedType, error.data);
          break;

        case 'enum':
          const allowedValues = error.params?.allowedValues;
          message = `Value must be one of: ${allowedValues?.join(', ')}`;
          suggestion = `Use one of the allowed values: ${allowedValues?.join(', ')}`;
          break;

        case 'format':
          const format = error.params?.format;
          message = `Invalid ${format} format`;
          suggestion = this.getFormatSuggestion(format);
          break;

        case 'const':
          const expectedValue = error.params?.allowedValue;
          message = `Must be exactly: ${expectedValue}`;
          suggestion = `Set the value to: ${expectedValue}`;
          break;

        case 'minLength':
          const minLength = error.params?.limit;
          message = `Must be at least ${minLength} characters long`;
          break;

        case 'maxLength':
          const maxLength = error.params?.limit;
          message = `Must be at most ${maxLength} characters long`;
          break;
      }

      return {
        field: this.cleanFieldPath(field),
        message,
        value: error.data,
        suggestion,
        severity: 'error'
      };
    });
  }

  /**
   * Generates warnings for common issues that aren't schema violations
   */
  private generateWarnings(clipObject: any): string[] {
    const warnings: string[] = [];

    if (!clipObject || typeof clipObject !== 'object') {
      return warnings;
    }

    // Check for potentially stale lastUpdated
    if (clipObject.lastUpdated) {
      const lastUpdated = new Date(clipObject.lastUpdated);
      const daysSinceUpdate = (Date.now() - lastUpdated.getTime()) / (1000 * 60 * 60 * 24);
      
      if (daysSinceUpdate > 30) {
        warnings.push(`CLIP object hasn't been updated in ${Math.floor(daysSinceUpdate)} days`);
      }
    }

    // Check for empty or minimal descriptions
    if (clipObject.description && clipObject.description.length < 10) {
      warnings.push('Description is very short - consider adding more detail');
    }

    // Check for missing location on Venue types
    if (clipObject.type === 'Venue' && !clipObject.location) {
      warnings.push('Venue objects typically include location information');
    }

    // Check for missing features
    if (!clipObject.features || clipObject.features.length === 0) {
      warnings.push('Consider adding features to describe capabilities or inventory');
    }

    // Check for missing actions
    if (!clipObject.actions || clipObject.actions.length === 0) {
      warnings.push('Consider adding actions to enable user interactions');
    }

    return warnings;
  }

  /**
   * Generates statistics about the CLIP object
   */
  private generateStats(clipObject: any): CLIPStats {
    if (!clipObject || typeof clipObject !== 'object') {
      return {
        type: 'unknown',
        hasLocation: false,
        featureCount: 0,
        actionCount: 0,
        serviceCount: 0,
        hasPersona: false,
        estimatedSize: 0,
        completeness: 0
      };
    }

    const jsonString = JSON.stringify(clipObject);
    const estimatedSize = new Blob([jsonString]).size;

    // Calculate completeness score (0-100)
    let completeness = 0;
    const weights = {
      requiredFields: 40, // @context, type, id, name, description, lastUpdated
      location: 15,
      features: 15,
      actions: 10,
      persona: 10,
      services: 10
    };

    // Check required fields (assume they exist if we got this far)
    completeness += weights.requiredFields;

    if (clipObject.location) completeness += weights.location;
    if (clipObject.features && clipObject.features.length > 0) completeness += weights.features;
    if (clipObject.actions && clipObject.actions.length > 0) completeness += weights.actions;
    if (clipObject.persona) completeness += weights.persona;
    if (clipObject.services && clipObject.services.length > 0) completeness += weights.services;

    return {
      type: clipObject.type || 'unknown',
      hasLocation: Boolean(clipObject.location),
      featureCount: Array.isArray(clipObject.features) ? clipObject.features.length : 0,
      actionCount: Array.isArray(clipObject.actions) ? clipObject.actions.length : 0,
      serviceCount: Array.isArray(clipObject.services) ? clipObject.services.length : 0,
      hasPersona: Boolean(clipObject.persona),
      estimatedSize,
      lastUpdated: clipObject.lastUpdated,
      completeness: Math.round(completeness)
    };
  }

  /**
   * Provides suggestions for required field errors
   */
  private getRequiredFieldSuggestion(field: string): string {
    const suggestions: Record<string, string> = {
      '@context': 'Add "@context": "https://clipprotocol.org/v1"',
      'type': 'Add "type": "Venue", "Device", or "SoftwareApp"',
      'id': 'Add a unique identifier like "clip:us:ny:business:my-business"',
      'name': 'Add a human-readable name for this entity',
      'description': 'Add a brief description (max 500 characters)',
      'lastUpdated': 'Add the current timestamp in ISO 8601 format'
    };

    return suggestions[field] || `Add the missing ${field} field`;
  }

  /**
   * Provides suggestions for type errors
   */
  private getTypeSuggestion(expectedType: string, actualValue: any): string {
    switch (expectedType) {
      case 'string':
        return `Convert ${typeof actualValue} to string by wrapping in quotes`;
      case 'number':
        return `Convert to number (remove quotes if it's a string number)`;
      case 'array':
        return `Convert to array format: [${actualValue}]`;
      case 'object':
        return 'Convert to object format: {}';
      default:
        return `Convert to ${expectedType}`;
    }
  }

  /**
   * Provides suggestions for format errors
   */
  private getFormatSuggestion(format: string): string {
    const suggestions: Record<string, string> = {
      'date-time': 'Use ISO 8601 format: "2023-12-01T10:30:00Z"',
      'uri': 'Use a valid URI format: "https://example.com"',
      'email': 'Use valid email format: "user@example.com"'
    };

    return suggestions[format] || `Use valid ${format} format`;
  }

  /**
   * Cleans field paths for better readability
   */
  private cleanFieldPath(path: string): string {
    return path
      .replace(/^\//, '') // Remove leading slash
      .replace(/\//g, '.') // Replace slashes with dots
      .replace(/\[(\d+)\]/g, '[$1]') // Keep array indices readable
      || 'root';
  }
} 