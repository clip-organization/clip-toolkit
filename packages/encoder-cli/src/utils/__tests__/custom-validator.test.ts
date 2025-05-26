/**
 * Tests for custom validation rules system
 */

import { CustomValidator, ValidationRule, ValidationIssue, formatValidationIssues, getValidationStats } from '../custom-validator';

describe('CustomValidator', () => {
  let validator: CustomValidator;

  beforeEach(() => {
    validator = new CustomValidator();
  });

  describe('Built-in rules', () => {
    test('validates unique feature IDs', () => {
      const clipObject = {
        features: [
          { id: 'feature1', name: 'Feature 1' },
          { id: 'feature2', name: 'Feature 2' },
          { id: 'feature1', name: 'Duplicate Feature' }
        ]
      };

      const issues = validator.validate(clipObject);
      const duplicateIssues = issues.filter(issue => issue.ruleId === 'unique-feature-ids');
      
      expect(duplicateIssues).toHaveLength(1);
      expect(duplicateIssues[0].severity).toBe('error');
      expect(duplicateIssues[0].message).toContain('feature1');
    });

    test('validates unique service IDs', () => {
      const clipObject = {
        services: [
          { id: 'service1', name: 'Service 1' },
          { id: 'service2', name: 'Service 2' },
          { id: 'service1', name: 'Duplicate Service' }
        ]
      };

      const issues = validator.validate(clipObject);
      const duplicateIssues = issues.filter(issue => issue.ruleId === 'unique-service-ids');
      
      expect(duplicateIssues).toHaveLength(1);
      expect(duplicateIssues[0].severity).toBe('error');
    });

    test('validates unique action IDs', () => {
      const clipObject = {
        actions: [
          { id: 'action1', name: 'Action 1' },
          { id: 'action2', name: 'Action 2' },
          { id: 'action1', name: 'Duplicate Action' }
        ]
      };

      const issues = validator.validate(clipObject);
      const duplicateIssues = issues.filter(issue => issue.ruleId === 'unique-action-ids');
      
      expect(duplicateIssues).toHaveLength(1);
      expect(duplicateIssues[0].severity).toBe('error');
    });

    test('validates descriptive names', () => {
      const clipObject = {
        name: 'Short'
      };

      const issues = validator.validate(clipObject);
      const nameIssues = issues.filter(issue => issue.ruleId === 'descriptive-names');
      
      expect(nameIssues).toHaveLength(1);
      expect(nameIssues[0].severity).toBe('warning');
      expect(nameIssues[0].path).toBe('name');
    });

    test('passes with descriptive names', () => {
      const clipObject = {
        name: 'This is a very descriptive name'
      };

      const issues = validator.validate(clipObject);
      const nameIssues = issues.filter(issue => issue.ruleId === 'descriptive-names');
      
      expect(nameIssues).toHaveLength(0);
    });

    test('validates meaningful descriptions', () => {
      const clipObject = {
        description: 'Short'
      };

      const issues = validator.validate(clipObject);
      const descIssues = issues.filter(issue => issue.ruleId === 'meaningful-descriptions');
      
      expect(descIssues).toHaveLength(1);
      expect(descIssues[0].severity).toBe('warning');
    });

    test('validates location data quality', () => {
      const clipObject = {
        location: {
          latitude: 95, // Invalid latitude
          longitude: -200 // Invalid longitude
        }
      };

      const issues = validator.validate(clipObject);
      const locationIssues = issues.filter(issue => issue.ruleId === 'location-data-quality');
      
      expect(locationIssues.length).toBeGreaterThanOrEqual(2);
      expect(locationIssues.some(issue => issue.message.includes('latitude'))).toBe(true);
      expect(locationIssues.some(issue => issue.message.includes('longitude'))).toBe(true);
    });

    test('validates CLIP ID format', () => {
      const clipObject = {
        id: 'invalid-id'
      };

      const issues = validator.validate(clipObject);
      const idIssues = issues.filter(issue => issue.ruleId === 'clip-id-format');
      
      expect(idIssues).toHaveLength(1);
      expect(idIssues[0].severity).toBe('error');
      expect(idIssues[0].message).toContain('clip:');
    });

    test('validates context validity', () => {
      const clipObject = {
        '@context': 'https://example.com/context'
      };

      const issues = validator.validate(clipObject);
      const contextIssues = issues.filter(issue => issue.ruleId === 'context-validity');
      
      expect(contextIssues).toHaveLength(1);
      expect(contextIssues[0].severity).toBe('error');
      expect(contextIssues[0].message).toContain('clipprotocol.org');
    });

    test('validates feature completeness', () => {
      const clipObject = {
        features: [
          { id: 'feature1' }, // Missing description and category
          { id: 'feature2', description: 'Has description' } // Missing category
        ]
      };

      const issues = validator.validate(clipObject);
      const featureIssues = issues.filter(issue => issue.ruleId === 'feature-completeness');
      
      expect(featureIssues.length).toBeGreaterThanOrEqual(3); // 2 missing descriptions + 2 missing categories
    });

    test('validates action usability', () => {
      const clipObject = {
        actions: [
          { id: 'action1' }, // Missing description
          { id: 'action2', method: 'INVALID' } // Invalid method
        ]
      };

      const issues = validator.validate(clipObject);
      const actionIssues = issues.filter(issue => issue.ruleId === 'action-usability');
      
      expect(actionIssues.length).toBeGreaterThanOrEqual(2);
    });
  });

  describe('Custom rules management', () => {
    test('adds custom rule', () => {
      const customRule: ValidationRule = {
        id: 'test-rule',
        description: 'Test rule',
        severity: 'warning',
        validate: (clip) => [{
          ruleId: 'test-rule',
          message: 'Test message',
          path: 'test',
          severity: 'warning'
        }]
      };

      validator.addRule(customRule);
      const rules = validator.getRules();
      
      expect(rules.some(rule => rule.id === 'test-rule')).toBe(true);
    });

    test('removes rule', () => {
      const customRule: ValidationRule = {
        id: 'removable-rule',
        description: 'Removable rule',
        severity: 'info',
        validate: () => []
      };

      validator.addRule(customRule);
      expect(validator.getRules().some(rule => rule.id === 'removable-rule')).toBe(true);
      
      const removed = validator.removeRule('removable-rule');
      expect(removed).toBe(true);
      expect(validator.getRules().some(rule => rule.id === 'removable-rule')).toBe(false);
    });

    test('handles rule execution errors', () => {
      const faultyRule: ValidationRule = {
        id: 'faulty-rule',
        description: 'Faulty rule',
        severity: 'error',
        validate: () => {
          throw new Error('Rule failed');
        }
      };

      validator.addRule(faultyRule);
      const issues = validator.validate({});
      
      const errorIssues = issues.filter(issue => 
        issue.ruleId === 'faulty-rule' && issue.message.includes('Rule execution failed')
      );
      
      expect(errorIssues).toHaveLength(1);
    });
  });

  describe('Complex validation scenarios', () => {
    test('validates complete CLIP object', () => {
      const clipObject = {
        '@context': 'https://clipprotocol.org/context/v1',
        id: 'clip:example:venue:test-venue',
        type: 'Venue',
        name: 'Example Test Venue Location',
        description: 'This is a comprehensive test venue with all the necessary details and information',
        location: {
          latitude: 40.7128,
          longitude: -74.0060,
          address: '123 Test Street, Test City, TC 12345'
        },
        features: [
          {
            id: 'wifi',
            name: 'WiFi',
            description: 'Free wireless internet access',
            category: 'connectivity'
          },
          {
            id: 'parking',
            name: 'Parking',
            description: 'On-site parking available',
            category: 'amenities'
          }
        ],
        actions: [
          {
            id: 'check-in',
            name: 'Check In',
            description: 'Check into the venue',
            method: 'POST'
          }
        ],
        services: [
          {
            id: 'booking',
            name: 'Booking Service',
            description: 'Book appointments and reservations'
          }
        ]
      };

      const issues = validator.validate(clipObject);
      const errors = issues.filter(issue => issue.severity === 'error');
      
      expect(errors).toHaveLength(0);
    });

    test('validates object with multiple issues', () => {
      const clipObject = {
        '@context': 'https://invalid.example.com/context',
        id: 'invalid-format',
        name: 'Short',
        description: 'Too short',
        location: {
          latitude: 95,
          longitude: -200
        },
        features: [
          { id: 'feat1' },
          { id: 'feat1' } // Duplicate
        ],
        actions: [
          { id: 'act1', method: 'INVALID' }
        ]
      };

      const issues = validator.validate(clipObject);
      const stats = getValidationStats(issues);
      
      expect(stats.errors).toBeGreaterThan(0);
      expect(stats.warnings).toBeGreaterThan(0);
      expect(stats.total).toBeGreaterThan(5);
    });
  });
});

describe('Utility functions', () => {
  test('formatValidationIssues', () => {
    const issues: ValidationIssue[] = [
      {
        ruleId: 'test-error',
        message: 'Error message',
        path: 'test.path',
        severity: 'error',
        suggestion: 'Fix this error'
      },
      {
        ruleId: 'test-warning',
        message: 'Warning message',
        path: 'test.warning',
        severity: 'warning'
      }
    ];

    const formatted = formatValidationIssues(issues);
    
    expect(formatted).toContain('ERRORS (1)');
    expect(formatted).toContain('WARNINGS (1)');
    expect(formatted).toContain('Error message');
    expect(formatted).toContain('Warning message');
    expect(formatted).toContain('Fix this error');
  });

  test('getValidationStats', () => {
    const issues: ValidationIssue[] = [
      { ruleId: 'r1', message: 'Error 1', path: 'p1', severity: 'error' },
      { ruleId: 'r2', message: 'Error 2', path: 'p2', severity: 'error' },
      { ruleId: 'r3', message: 'Warning 1', path: 'p3', severity: 'warning' },
      { ruleId: 'r4', message: 'Info 1', path: 'p4', severity: 'info' }
    ];

    const stats = getValidationStats(issues);
    
    expect(stats.total).toBe(4);
    expect(stats.errors).toBe(2);
    expect(stats.warnings).toBe(1);
    expect(stats.info).toBe(1);
    expect(stats.hasErrors).toBe(true);
    expect(stats.hasWarnings).toBe(true);
    expect(stats.hasInfo).toBe(true);
  });

  test('getValidationStats with no issues', () => {
    const stats = getValidationStats([]);
    
    expect(stats.total).toBe(0);
    expect(stats.errors).toBe(0);
    expect(stats.warnings).toBe(0);
    expect(stats.info).toBe(0);
    expect(stats.hasErrors).toBe(false);
    expect(stats.hasWarnings).toBe(false);
    expect(stats.hasInfo).toBe(false);
  });

  test('formatValidationIssues with no issues', () => {
    const formatted = formatValidationIssues([]);
    expect(formatted).toBe('No custom validation issues found.');
  });
}); 