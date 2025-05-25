import { CLIPValidator, ValidationResult, CLIPStats } from '../src/clip-validator';

describe('CLIPValidator', () => {
  let validator: CLIPValidator;

  // Mock CLIP schema for testing
  const mockSchema = {
    type: 'object',
    required: ['@context', 'type', 'id', 'name', 'description', 'lastUpdated'],
    properties: {
      '@context': {
        type: 'string',
        const: 'https://clipprotocol.org/v1'
      },
      type: {
        type: 'string',
        enum: ['Venue', 'Device', 'SoftwareApp']
      },
      id: {
        type: 'string',
        format: 'uri'
      },
      name: {
        type: 'string',
        minLength: 1,
        maxLength: 100
      },
      description: {
        type: 'string',
        minLength: 1,
        maxLength: 500
      },
      lastUpdated: {
        type: 'string',
        format: 'date-time'
      },
      location: {
        type: 'object',
        properties: {
          address: { type: 'string' },
          coordinates: {
            type: 'object',
            required: ['latitude', 'longitude'],
            properties: {
              latitude: { type: 'number', minimum: -90, maximum: 90 },
              longitude: { type: 'number', minimum: -180, maximum: 180 }
            }
          }
        }
      },
      features: {
        type: 'array',
        items: {
          type: 'object',
          required: ['name'],
          properties: {
            name: { type: 'string' },
            type: { type: 'string' },
            count: { type: 'integer', minimum: 0 }
          }
        }
      },
      actions: {
        type: 'array',
        items: {
          type: 'object',
          required: ['label', 'type', 'endpoint'],
          properties: {
            label: { type: 'string' },
            type: { type: 'string', enum: ['link', 'chat', 'call', 'api', 'custom'] },
            endpoint: { type: 'string', format: 'uri' }
          }
        }
      },
      services: {
        type: 'array',
        items: {
          type: 'object',
          required: ['type', 'endpoint'],
          properties: {
            type: { type: 'string' },
            endpoint: { type: 'string', format: 'uri' }
          }
        }
      },
      persona: {
        type: 'object',
        properties: {
          role: { type: 'string' },
          personality: { type: 'string' }
        }
      }
    }
  };

  // Valid CLIP objects for testing
  const validVenue = {
    '@context': 'https://clipprotocol.org/v1',
    type: 'Venue',
    id: 'clip:us:ny:gym:test-gym',
    name: 'Test Gym',
    description: 'A test gym for validation testing',
    lastUpdated: '2023-01-01T00:00:00Z',
    location: {
      address: '123 Test St, Test City, NY 10001',
      coordinates: {
        latitude: 40.7589,
        longitude: -73.9851
      }
    },
    features: [
      {
        name: 'Treadmill',
        type: 'equipment',
        count: 5
      }
    ],
    actions: [
      {
        label: 'Book Equipment',
        type: 'link',
        endpoint: 'https://test-gym.com/book'
      }
    ]
  };

  const validDevice = {
    '@context': 'https://clipprotocol.org/v1',
    type: 'Device',
    id: 'clip:us:device:smart-fridge',
    name: 'Smart Fridge',
    description: 'IoT refrigerator with inventory tracking',
    lastUpdated: '2023-01-01T00:00:00Z'
  };

  beforeEach(() => {
    validator = new CLIPValidator(mockSchema);
  });

  describe('constructor', () => {
    it('should create validator with valid schema', () => {
      expect(() => new CLIPValidator(mockSchema)).not.toThrow();
    });

    it('should throw error with invalid schema', () => {
      const invalidSchema = { invalid: 'schema' };
      expect(() => new CLIPValidator(invalidSchema)).toThrow();
    });

    it('should accept validator options', () => {
      const options = { strict: false, validateFormats: false };
      expect(() => new CLIPValidator(mockSchema, options)).not.toThrow();
    });
  });

  describe('validate', () => {
    it('should validate a correct Venue CLIP object', () => {
      const result = validator.validate(validVenue);

      expect(result.valid).toBe(true);
      expect(result.errors).toHaveLength(0);
      expect(result.stats.type).toBe('Venue');
      expect(result.stats.hasLocation).toBe(true);
      expect(result.stats.featureCount).toBe(1);
      expect(result.stats.actionCount).toBe(1);
    });

    it('should validate a correct Device CLIP object', () => {
      const result = validator.validate(validDevice);

      expect(result.valid).toBe(true);
      expect(result.errors).toHaveLength(0);
      expect(result.stats.type).toBe('Device');
      expect(result.stats.hasLocation).toBe(false);
    });

    it('should detect missing required fields', () => {
      const invalidClip = {
        '@context': 'https://clipprotocol.org/v1',
        type: 'Venue'
        // Missing id, name, description, lastUpdated
      };

      const result = validator.validate(invalidClip);

      expect(result.valid).toBe(false);
      expect(result.errors.length).toBeGreaterThan(0);
      
      const missingFields = result.errors
        .filter(error => error.message.includes('Missing required field'))
        .map(error => error.message);
      
      expect(missingFields).toContain('Missing required field: id');
      expect(missingFields).toContain('Missing required field: name');
      expect(missingFields).toContain('Missing required field: description');
      expect(missingFields).toContain('Missing required field: lastUpdated');
    });

    it('should detect invalid field types', () => {
      const invalidClip = {
        '@context': 'https://clipprotocol.org/v1',
        type: 'Venue',
        id: 123, // Should be string
        name: ['Test'], // Should be string
        description: 'Valid description',
        lastUpdated: '2023-01-01T00:00:00Z'
      };

      const result = validator.validate(invalidClip);

      expect(result.valid).toBe(false);
      
      const typeErrors = result.errors.filter(error => 
        error.message.includes('Expected string')
      );
      
      expect(typeErrors.length).toBeGreaterThan(0);
    });

    it('should detect invalid enum values', () => {
      const invalidClip = {
        '@context': 'https://clipprotocol.org/v1',
        type: 'InvalidType', // Not in enum
        id: 'clip:test',
        name: 'Test',
        description: 'Test description',
        lastUpdated: '2023-01-01T00:00:00Z'
      };

      const result = validator.validate(invalidClip);

      expect(result.valid).toBe(false);
      
      const enumError = result.errors.find(error => 
        error.message.includes('Value must be one of')
      );
      
      expect(enumError).toBeDefined();
      expect(enumError?.suggestion).toContain('Venue, Device, SoftwareApp');
    });

    it('should detect invalid formats', () => {
      const invalidClip = {
        '@context': 'https://clipprotocol.org/v1',
        type: 'Venue',
        id: 'not-a-uri',
        name: 'Test',
        description: 'Test description',
        lastUpdated: 'not-a-date'
      };

      const result = validator.validate(invalidClip);

      expect(result.valid).toBe(false);
      
      const formatErrors = result.errors.filter(error => 
        error.message.includes('Invalid') && error.message.includes('format')
      );
      
      expect(formatErrors.length).toBeGreaterThan(0);
    });

    it('should detect string length violations', () => {
      const invalidClip = {
        '@context': 'https://clipprotocol.org/v1',
        type: 'Venue',
        id: 'clip:test',
        name: '', // Too short (minLength: 1)
        description: 'A'.repeat(501), // Too long (maxLength: 500)
        lastUpdated: '2023-01-01T00:00:00Z'
      };

      const result = validator.validate(invalidClip);

      expect(result.valid).toBe(false);
      
      const lengthErrors = result.errors.filter(error => 
        error.message.includes('characters long')
      );
      
      expect(lengthErrors.length).toBe(2);
    });
  });

  describe('generateStats', () => {
    it('should calculate correct statistics for complete CLIP object', () => {
      const result = validator.validate(validVenue);
      const stats = result.stats;

      expect(stats.type).toBe('Venue');
      expect(stats.hasLocation).toBe(true);
      expect(stats.featureCount).toBe(1);
      expect(stats.actionCount).toBe(1);
      expect(stats.serviceCount).toBe(0);
      expect(stats.hasPersona).toBe(false);
      expect(stats.estimatedSize).toBeGreaterThan(0);
      expect(stats.completeness).toBeGreaterThan(0);
    });

    it('should calculate completeness score correctly', () => {
      const minimalClip = {
        '@context': 'https://clipprotocol.org/v1',
        type: 'Device',
        id: 'clip:test',
        name: 'Test',
        description: 'Test description',
        lastUpdated: '2023-01-01T00:00:00Z'
      };

      const result = validator.validate(minimalClip);
      
      // Should have 40% for required fields only
      expect(result.stats.completeness).toBe(40);
    });

    it('should handle invalid objects gracefully', () => {
      const result = validator.validate(null);
      
      expect(result.stats.type).toBe('unknown');
      expect(result.stats.completeness).toBe(0);
      expect(result.stats.estimatedSize).toBe(0);
    });
  });

  describe('generateWarnings', () => {
    it('should warn about stale lastUpdated', () => {
      const staleClip = {
        ...validVenue,
        lastUpdated: '2022-01-01T00:00:00Z' // More than 30 days ago
      };

      const result = validator.validate(staleClip);
      
      const staleWarning = result.warnings?.find(warning => 
        warning.includes("hasn't been updated")
      );
      
      expect(staleWarning).toBeDefined();
    });

    it('should warn about short descriptions', () => {
      const shortDescClip = {
        ...validVenue,
        description: 'Short'
      };

      const result = validator.validate(shortDescClip);
      
      const descWarning = result.warnings?.find(warning => 
        warning.includes('Description is very short')
      );
      
      expect(descWarning).toBeDefined();
    });

    it('should warn about missing location for Venues', () => {
      const noLocationVenue = {
        ...validVenue,
        location: undefined
      };
      delete noLocationVenue.location;

      const result = validator.validate(noLocationVenue);
      
      const locationWarning = result.warnings?.find(warning => 
        warning.includes('location information')
      );
      
      expect(locationWarning).toBeDefined();
    });

    it('should warn about missing features and actions', () => {
      const emptyClip = {
        '@context': 'https://clipprotocol.org/v1',
        type: 'Venue',
        id: 'clip:test',
        name: 'Test',
        description: 'Test description',
        lastUpdated: '2023-01-01T00:00:00Z'
      };

      const result = validator.validate(emptyClip);
      
      const featureWarning = result.warnings?.find(warning => 
        warning.includes('adding features')
      );
      const actionWarning = result.warnings?.find(warning => 
        warning.includes('adding actions')
      );
      
      expect(featureWarning).toBeDefined();
      expect(actionWarning).toBeDefined();
    });
  });

  describe('validateBatch', () => {
    it('should validate multiple CLIP objects', () => {
      const clips = [validVenue, validDevice];
      const results = validator.validateBatch(clips);

      expect(results).toHaveLength(2);
      expect(results[0].valid).toBe(true);
      expect(results[1].valid).toBe(true);
      expect(results[0].stats.type).toBe('Venue');
      expect(results[1].stats.type).toBe('Device');
    });

    it('should handle mixed valid and invalid objects', () => {
      const invalidClip = { invalid: 'object' };
      const clips = [validVenue, invalidClip];
      const results = validator.validateBatch(clips);

      expect(results).toHaveLength(2);
      expect(results[0].valid).toBe(true);
      expect(results[1].valid).toBe(false);
    });
  });

  describe('error suggestions', () => {
    it('should provide helpful suggestions for required field errors', () => {
      const invalidClip = {
        '@context': 'https://clipprotocol.org/v1'
        // Missing all other required fields
      };

      const result = validator.validate(invalidClip);
      
      const typeError = result.errors.find(error => 
        error.message.includes('Missing required field: type')
      );
      
      expect(typeError?.suggestion).toContain('Venue", "Device", or "SoftwareApp');
    });

    it('should provide format suggestions', () => {
      const invalidClip = {
        '@context': 'https://clipprotocol.org/v1',
        type: 'Venue',
        id: 'clip:test',
        name: 'Test',
        description: 'Test',
        lastUpdated: 'invalid-date'
      };

      const result = validator.validate(invalidClip);
      
      const dateError = result.errors.find(error => 
        error.message.includes('Invalid date-time format')
      );
      
      expect(dateError?.suggestion).toContain('ISO 8601 format');
    });
  });
}); 