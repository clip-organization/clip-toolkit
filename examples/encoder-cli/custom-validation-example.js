#!/usr/bin/env node

/**
 * Custom Validation Example
 * 
 * This example demonstrates how to use the CLIP Encoder CLI's custom validation
 * system to validate CLIP objects beyond the basic JSON Schema validation.
 */

const fs = require('fs');
const path = require('path');

// Example CLIP objects for testing
const validClipObject = {
  "@context": "https://clipprotocol.org/context/v1",
  "id": "clip:example:venue:coffee-shop",
  "type": "Venue",
  "name": "Downtown Coffee Shop Location",
  "description": "A cozy coffee shop in the heart of downtown with excellent WiFi and comfortable seating for remote work",
  "location": {
    "latitude": 40.7128,
    "longitude": -74.0060,
    "address": "123 Main Street, New York, NY 10001"
  },
  "features": [
    {
      "id": "wifi",
      "name": "Free WiFi",
      "description": "High-speed wireless internet access",
      "category": "connectivity"
    },
    {
      "id": "seating",
      "name": "Comfortable Seating",
      "description": "Various seating options including tables and couches",
      "category": "amenities"
    }
  ],
  "actions": [
    {
      "id": "order",
      "name": "Place Order",
      "description": "Order coffee and food items",
      "method": "POST"
    }
  ],
  "services": [
    {
      "id": "loyalty",
      "name": "Loyalty Program",
      "description": "Earn points with every purchase"
    }
  ]
};

const invalidClipObject = {
  "@context": "https://invalid-context.example.com/context",
  "id": "invalid-format-id",
  "type": "Venue",
  "name": "Short",
  "description": "Too short",
  "location": {
    "latitude": 95, // Invalid latitude
    "longitude": -200 // Invalid longitude
  },
  "features": [
    {
      "id": "wifi",
      "name": "WiFi"
      // Missing description and category
    },
    {
      "id": "wifi", // Duplicate ID
      "name": "Another WiFi"
    }
  ],
  "actions": [
    {
      "id": "action1",
      "method": "INVALID_METHOD"
      // Missing description
    }
  ],
  "services": [
    {
      "id": "service1"
      // Missing name and description
    },
    {
      "id": "service1" // Duplicate ID
    }
  ]
};

// Custom validation rules example
const customRules = [
  {
    "id": "venue-specific-features",
    "description": "Venues should have specific required features",
    "severity": "warning",
    "validate": function(clip) {
      const issues = [];
      if (clip.type === 'Venue') {
        const features = clip.features || [];
        const featureIds = features.map(f => f.id);
        
        if (!featureIds.includes('wifi')) {
          issues.push({
            "ruleId": "venue-specific-features",
            "message": "Venues should typically include WiFi as a feature",
            "path": "features",
            "severity": "warning",
            "suggestion": "Consider adding a WiFi feature for better user experience"
          });
        }
      }
      return issues;
    }
  },
  {
    "id": "business-hours",
    "description": "Business venues should include operating hours",
    "severity": "info",
    "validate": function(clip) {
      const issues = [];
      if (clip.type === 'Venue' && !clip.hours && !clip.operatingHours) {
        issues.push({
          "ruleId": "business-hours",
          "message": "Consider adding business hours information",
          "path": "root",
          "severity": "info",
          "suggestion": "Add 'hours' or 'operatingHours' field with business operating times"
        });
      }
      return issues;
    }
  }
];

async function runExample() {
  console.log('🔍 CLIP Custom Validation Example\n');
  
  // Create temporary files for testing
  const validFile = path.join(__dirname, 'temp-valid-clip.json');
  const invalidFile = path.join(__dirname, 'temp-invalid-clip.json');
  const rulesFile = path.join(__dirname, 'temp-custom-rules.json');
  
  try {
    // Write test files
    fs.writeFileSync(validFile, JSON.stringify(validClipObject, null, 2));
    fs.writeFileSync(invalidFile, JSON.stringify(invalidClipObject, null, 2));
    fs.writeFileSync(rulesFile, JSON.stringify(customRules, null, 2));
    
    console.log('📝 Created test files:');
    console.log(`   Valid CLIP: ${validFile}`);
    console.log(`   Invalid CLIP: ${invalidFile}`);
    console.log(`   Custom Rules: ${rulesFile}\n`);
    
    console.log('🧪 Test Cases:\n');
    
    console.log('1. Basic validation (valid CLIP object):');
    console.log('   Command: clip validate temp-valid-clip.json');
    console.log('   Expected: ✓ Valid with no custom validation errors\n');
    
    console.log('2. Basic validation (invalid CLIP object):');
    console.log('   Command: clip validate temp-invalid-clip.json');
    console.log('   Expected: ✗ Invalid with multiple custom validation errors\n');
    
    console.log('3. Validation with custom rules:');
    console.log('   Command: clip validate temp-valid-clip.json --rules-file temp-custom-rules.json');
    console.log('   Expected: ✓ Valid but may show custom warnings/info\n');
    
    console.log('4. Disable custom validation:');
    console.log('   Command: clip validate temp-invalid-clip.json --no-custom-rules');
    console.log('   Expected: Only schema validation, no custom rule checks\n');
    
    console.log('5. JSON output format:');
    console.log('   Command: clip validate temp-invalid-clip.json --output json');
    console.log('   Expected: Structured JSON with schema and custom validation results\n');
    
    console.log('6. Verbose output:');
    console.log('   Command: clip validate temp-invalid-clip.json --verbose');
    console.log('   Expected: Detailed error messages with suggestions\n');
    
    console.log('7. Batch validation:');
    console.log('   Command: clip batch-validate temp-*.json --rules-file temp-custom-rules.json');
    console.log('   Expected: Validation results for multiple files\n');
    
    console.log('📋 Built-in Custom Validation Rules:\n');
    console.log('   • unique-feature-ids: Ensures feature IDs are unique');
    console.log('   • unique-service-ids: Ensures service IDs are unique');
    console.log('   • unique-action-ids: Ensures action IDs are unique');
    console.log('   • descriptive-names: Names should be descriptive (3+ words)');
    console.log('   • meaningful-descriptions: Descriptions should be detailed');
    console.log('   • location-data-quality: Location coordinates should be valid');
    console.log('   • feature-completeness: Features should have descriptions/categories');
    console.log('   • action-usability: Actions should have descriptions and valid methods');
    console.log('   • clip-id-format: CLIP IDs should follow proper format');
    console.log('   • context-validity: Context should reference clipprotocol.org\n');
    
    console.log('🎯 Custom Rules File Format:\n');
    console.log('   Custom rules should be a JSON array of rule objects:');
    console.log('   [');
    console.log('     {');
    console.log('       "id": "rule-id",');
    console.log('       "description": "Rule description",');
    console.log('       "severity": "error|warning|info",');
    console.log('       "validate": "function(clip) { return []; }"');
    console.log('     }');
    console.log('   ]\n');
    
    console.log('💡 Tips:');
    console.log('   • Use --verbose for detailed error information');
    console.log('   • Use --no-custom-rules to disable custom validation');
    console.log('   • Use --output json for programmatic processing');
    console.log('   • Custom rules can be loaded from external JSON files');
    console.log('   • Built-in rules cover common CLIP object quality issues\n');
    
    console.log('🚀 Try running the commands above to see custom validation in action!');
    
  } catch (error) {
    console.error('Error creating example files:', error.message);
  } finally {
    // Clean up temporary files
    try {
      if (fs.existsSync(validFile)) fs.unlinkSync(validFile);
      if (fs.existsSync(invalidFile)) fs.unlinkSync(invalidFile);
      if (fs.existsSync(rulesFile)) fs.unlinkSync(rulesFile);
    } catch (cleanupError) {
      console.warn('Warning: Could not clean up temporary files:', cleanupError.message);
    }
  }
}

// Run the example if this file is executed directly
if (require.main === module) {
  runExample().catch(console.error);
}

module.exports = { runExample, validClipObject, invalidClipObject, customRules }; 