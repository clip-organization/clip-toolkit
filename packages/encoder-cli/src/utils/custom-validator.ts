/**
 * Custom validation rules system for CLIP objects
 * Provides additional validation beyond JSON Schema
 */

export interface ValidationRule {
  id: string;
  description: string;
  severity: 'error' | 'warning' | 'info';
  validate: (clipObject: any) => ValidationIssue[];
}

export interface ValidationIssue {
  ruleId: string;
  message: string;
  path: string;
  severity: 'error' | 'warning' | 'info';
  suggestion?: string;
}

export class CustomValidator {
  private rules: ValidationRule[] = [];
  
  constructor(rules: ValidationRule[] = []) {
    this.rules = [...this.getBuiltInRules(), ...rules];
  }
  
  /**
   * Validate a CLIP object against all custom rules
   */
  validate(clipObject: any): ValidationIssue[] {
    const issues: ValidationIssue[] = [];
    
    for (const rule of this.rules) {
      try {
        const ruleIssues = rule.validate(clipObject);
        issues.push(...ruleIssues);
      } catch (error) {
        // If a rule throws an error, report it as an issue
        issues.push({
          ruleId: rule.id,
          message: `Rule execution failed: ${error instanceof Error ? error.message : String(error)}`,
          path: 'root',
          severity: 'error',
          suggestion: 'Check rule implementation'
        });
      }
    }
    
    return issues;
  }
  
  /**
   * Add a custom rule
   */
  addRule(rule: ValidationRule): void {
    this.rules.push(rule);
  }
  
  /**
   * Remove a rule by ID
   */
  removeRule(ruleId: string): boolean {
    const initialLength = this.rules.length;
    this.rules = this.rules.filter(rule => rule.id !== ruleId);
    return this.rules.length < initialLength;
  }
  
  /**
   * Get all rules
   */
  getRules(): ValidationRule[] {
    return [...this.rules];
  }
  
  /**
   * Get built-in validation rules
   */
  private getBuiltInRules(): ValidationRule[] {
    return [
      {
        id: 'unique-feature-ids',
        description: 'Feature IDs must be unique within the CLIP object',
        severity: 'error',
        validate: (clip) => {
          const issues: ValidationIssue[] = [];
          const features = clip.features || [];
          const featureIds = new Set<string>();
          const duplicateIds = new Set<string>();
          
          features.forEach((feature: any, index: number) => {
            const id = feature.id;
            if (id) {
              if (featureIds.has(id)) {
                duplicateIds.add(id);
              }
              featureIds.add(id);
            }
          });
          
          duplicateIds.forEach(id => {
            issues.push({
              ruleId: 'unique-feature-ids',
              message: `Duplicate feature ID: ${id}`,
              path: 'features',
              severity: 'error',
              suggestion: 'Ensure all feature IDs are unique across all features'
            });
          });
          
          return issues;
        }
      },
      
      {
        id: 'unique-service-ids',
        description: 'Service IDs must be unique within the CLIP object',
        severity: 'error',
        validate: (clip) => {
          const issues: ValidationIssue[] = [];
          const services = clip.services || [];
          const serviceIds = new Set<string>();
          const duplicateIds = new Set<string>();
          
          services.forEach((service: any, index: number) => {
            const id = service.id;
            if (id) {
              if (serviceIds.has(id)) {
                duplicateIds.add(id);
              }
              serviceIds.add(id);
            }
          });
          
          duplicateIds.forEach(id => {
            issues.push({
              ruleId: 'unique-service-ids',
              message: `Duplicate service ID: ${id}`,
              path: 'services',
              severity: 'error',
              suggestion: 'Ensure all service IDs are unique across all services'
            });
          });
          
          return issues;
        }
      },
      
      {
        id: 'unique-action-ids',
        description: 'Action IDs must be unique within the CLIP object',
        severity: 'error',
        validate: (clip) => {
          const issues: ValidationIssue[] = [];
          const actions = clip.actions || [];
          const actionIds = new Set<string>();
          const duplicateIds = new Set<string>();
          
          actions.forEach((action: any, index: number) => {
            const id = action.id;
            if (id) {
              if (actionIds.has(id)) {
                duplicateIds.add(id);
              }
              actionIds.add(id);
            }
          });
          
          duplicateIds.forEach(id => {
            issues.push({
              ruleId: 'unique-action-ids',
              message: `Duplicate action ID: ${id}`,
              path: 'actions',
              severity: 'error',
              suggestion: 'Ensure all action IDs are unique across all actions'
            });
          });
          
          return issues;
        }
      },
      
      {
        id: 'descriptive-names',
        description: 'Names should be descriptive (at least 3 words)',
        severity: 'warning',
        validate: (clip) => {
          const issues: ValidationIssue[] = [];
          
          if (clip.name && clip.name.split(/\s+/).filter(Boolean).length < 3) {
            issues.push({
              ruleId: 'descriptive-names',
              message: 'Name is not descriptive enough',
              path: 'name',
              severity: 'warning',
              suggestion: 'Use at least 3 words for a more descriptive name'
            });
          }
          
          return issues;
        }
      },
      
      {
        id: 'meaningful-descriptions',
        description: 'Descriptions should be meaningful and detailed',
        severity: 'warning',
        validate: (clip) => {
          const issues: ValidationIssue[] = [];
          
          if (clip.description) {
            if (clip.description.length < 20) {
              issues.push({
                ruleId: 'meaningful-descriptions',
                message: 'Description is too short to be meaningful',
                path: 'description',
                severity: 'warning',
                suggestion: 'Provide a more detailed description (at least 20 characters)'
              });
            } else if (clip.description.split(/\s+/).length < 5) {
              issues.push({
                ruleId: 'meaningful-descriptions',
                message: 'Description should contain more words',
                path: 'description',
                severity: 'warning',
                suggestion: 'Use at least 5 words for a meaningful description'
              });
            }
          }
          
          return issues;
        }
      },
      
      {
        id: 'location-data-quality',
        description: 'Location data should be complete and accurate',
        severity: 'warning',
        validate: (clip) => {
          const issues: ValidationIssue[] = [];
          
          if (clip.location) {
            const location = clip.location;
            
            // Check for coordinates
            if (!location.latitude || !location.longitude) {
              issues.push({
                ruleId: 'location-data-quality',
                message: 'Location is missing coordinates',
                path: 'location',
                severity: 'warning',
                suggestion: 'Include latitude and longitude for precise location data'
              });
            }
            
            // Check coordinate validity
            if (location.latitude && (location.latitude < -90 || location.latitude > 90)) {
              issues.push({
                ruleId: 'location-data-quality',
                message: 'Invalid latitude value',
                path: 'location.latitude',
                severity: 'error',
                suggestion: 'Latitude must be between -90 and 90 degrees'
              });
            }
            
            if (location.longitude && (location.longitude < -180 || location.longitude > 180)) {
              issues.push({
                ruleId: 'location-data-quality',
                message: 'Invalid longitude value',
                path: 'location.longitude',
                severity: 'error',
                suggestion: 'Longitude must be between -180 and 180 degrees'
              });
            }
            
            // Check for address completeness
            if (!location.address && !location.streetAddress) {
              issues.push({
                ruleId: 'location-data-quality',
                message: 'Location is missing address information',
                path: 'location',
                severity: 'info',
                suggestion: 'Consider adding address or streetAddress for better usability'
              });
            }
          }
          
          return issues;
        }
      },
      
      {
        id: 'feature-completeness',
        description: 'Features should have complete information',
        severity: 'info',
        validate: (clip) => {
          const issues: ValidationIssue[] = [];
          const features = clip.features || [];
          
          features.forEach((feature: any, index: number) => {
            if (!feature.description) {
              issues.push({
                ruleId: 'feature-completeness',
                message: `Feature ${index + 1} is missing description`,
                path: `features[${index}]`,
                severity: 'info',
                suggestion: 'Add descriptions to features for better usability'
              });
            }
            
            if (!feature.category) {
              issues.push({
                ruleId: 'feature-completeness',
                message: `Feature ${index + 1} is missing category`,
                path: `features[${index}]`,
                severity: 'info',
                suggestion: 'Categorize features for better organization'
              });
            }
          });
          
          return issues;
        }
      },
      
      {
        id: 'action-usability',
        description: 'Actions should be user-friendly and complete',
        severity: 'warning',
        validate: (clip) => {
          const issues: ValidationIssue[] = [];
          const actions = clip.actions || [];
          
          actions.forEach((action: any, index: number) => {
            if (!action.description) {
              issues.push({
                ruleId: 'action-usability',
                message: `Action ${index + 1} is missing description`,
                path: `actions[${index}]`,
                severity: 'warning',
                suggestion: 'Add descriptions to actions for better user experience'
              });
            }
            
            if (action.method && !['GET', 'POST', 'PUT', 'DELETE', 'PATCH'].includes(action.method.toUpperCase())) {
              issues.push({
                ruleId: 'action-usability',
                message: `Action ${index + 1} uses non-standard HTTP method: ${action.method}`,
                path: `actions[${index}].method`,
                severity: 'warning',
                suggestion: 'Use standard HTTP methods: GET, POST, PUT, DELETE, PATCH'
              });
            }
          });
          
          return issues;
        }
      },
      
      {
        id: 'clip-id-format',
        description: 'CLIP ID should follow the proper format',
        severity: 'error',
        validate: (clip) => {
          const issues: ValidationIssue[] = [];
          
          if (clip.id && !clip.id.startsWith('clip:')) {
            issues.push({
              ruleId: 'clip-id-format',
              message: 'CLIP ID should start with "clip:" prefix',
              path: 'id',
              severity: 'error',
              suggestion: 'Use the format: clip:namespace:type:identifier'
            });
          }
          
          if (clip.id && clip.id.startsWith('clip:')) {
            const parts = clip.id.split(':');
            if (parts.length < 4) {
              issues.push({
                ruleId: 'clip-id-format',
                message: 'CLIP ID should have at least 4 parts separated by colons',
                path: 'id',
                severity: 'warning',
                suggestion: 'Use the format: clip:namespace:type:identifier'
              });
            }
          }
          
          return issues;
        }
      },
      
      {
        id: 'context-validity',
        description: 'Context should reference valid CLIP Protocol URLs',
        severity: 'error',
        validate: (clip) => {
          const issues: ValidationIssue[] = [];
          
          if (clip['@context'] && typeof clip['@context'] === 'string') {
            if (!clip['@context'].includes('clipprotocol.org')) {
              issues.push({
                ruleId: 'context-validity',
                message: 'Context should reference clipprotocol.org',
                path: '@context',
                severity: 'error',
                suggestion: 'Use an official CLIP Protocol context URL'
              });
            }
          }
          
          return issues;
        }
      }
    ];
  }
}

/**
 * Format validation issues for display
 */
export function formatValidationIssues(issues: ValidationIssue[]): string {
  if (issues.length === 0) {
    return 'No custom validation issues found.';
  }
  
  const grouped = issues.reduce((acc, issue) => {
    if (!acc[issue.severity]) {
      acc[issue.severity] = [];
    }
    acc[issue.severity].push(issue);
    return acc;
  }, {} as Record<string, ValidationIssue[]>);
  
  let output = '';
  
  // Display in order: errors, warnings, info
  ['error', 'warning', 'info'].forEach(severity => {
    const severityIssues = grouped[severity];
    if (severityIssues && severityIssues.length > 0) {
      output += `\n${severity.toUpperCase()}S (${severityIssues.length}):\n`;
      severityIssues.forEach((issue, index) => {
        output += `  ${index + 1}. [${issue.ruleId}] ${issue.message}\n`;
        output += `     at ${issue.path}\n`;
        if (issue.suggestion) {
          output += `     💡 ${issue.suggestion}\n`;
        }
      });
    }
  });
  
  return output;
}

/**
 * Get statistics about validation issues
 */
export function getValidationStats(issues: ValidationIssue[]) {
  const errorCount = issues.filter(i => i.severity === 'error').length;
  const warningCount = issues.filter(i => i.severity === 'warning').length;
  const infoCount = issues.filter(i => i.severity === 'info').length;
  
  return {
    total: issues.length,
    errors: errorCount,
    warnings: warningCount,
    info: infoCount,
    hasErrors: errorCount > 0,
    hasWarnings: warningCount > 0,
    hasInfo: infoCount > 0
  };
} 