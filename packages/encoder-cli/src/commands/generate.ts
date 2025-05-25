import * as fs from 'fs';
import * as path from 'path';
import chalk from 'chalk';
import ora from 'ora';

interface GenerateOptions {
  type: 'venue' | 'device' | 'app';
  output?: string;
  template?: string;
  interactive?: boolean;
  minimal?: boolean;
}

export async function generateCommand(options: GenerateOptions) {
  const spinner = ora('Generating CLIP template...').start();
  
  try {
    // Generate the appropriate template
    const template = generateTemplate(options.type, options.minimal);
    
    spinner.stop();
    
    // Interactive mode (basic implementation)
    if (options.interactive) {
      console.log(chalk.blue('🛠️  Interactive mode not yet implemented. Generating basic template...'));
    }
    
    // Output the template
    const output = JSON.stringify(template, null, 2);
    
    if (options.output) {
      // Write to file
      const outputPath = path.resolve(options.output);
      fs.writeFileSync(outputPath, output, 'utf8');
      console.log(chalk.green('✓ Template generated:'), chalk.cyan(outputPath));
    } else {
      // Output to stdout
      console.log(output);
    }
    
    // Show helpful information
    if (!options.output) {
      console.error(chalk.gray('\n💡 To save to file, use: --output <filename>'));
      console.error(chalk.gray('💡 For minimal template, use: --minimal'));
    }
    
  } catch (error) {
    spinner.stop();
    console.error(chalk.red('✗ Generation failed:'), error instanceof Error ? error.message : String(error));
    process.exit(1);
  }
}

function generateTemplate(type: string, minimal: boolean = false): any {
  const baseTemplate = {
    "@context": "https://clipprotocol.org/v1",
    "type": getTypeFromString(type),
    "id": generateSampleId(type),
    "name": generateSampleName(type),
    "description": generateSampleDescription(type),
    "lastUpdated": new Date().toISOString()
  };

  if (minimal) {
    return baseTemplate;
  }

  // Add optional fields based on type
  switch (type) {
    case 'venue':
      return {
        ...baseTemplate,
        "location": {
          "address": "123 Example St, Example City, ST 12345",
          "coordinates": {
            "latitude": 40.7589,
            "longitude": -73.9851
          },
          "timezone": "America/New_York"
        },
        "features": [
          {
            "name": "Example Feature",
            "type": "facility",
            "count": 1,
            "available": 1,
            "metadata": {
              "description": "Description of this feature"
            }
          }
        ],
        "actions": [
          {
            "label": "Visit Website",
            "type": "link",
            "endpoint": "https://example.com",
            "description": "Visit our website for more information"
          }
        ],
        "persona": {
          "role": "Assistant",
          "personality": "helpful, friendly",
          "expertise": ["customer service", "information"],
          "prompt": "You are a helpful assistant for this venue. Provide information and help visitors."
        }
      };

    case 'device':
      return {
        ...baseTemplate,
        "features": [
          {
            "name": "Status",
            "type": "sensor",
            "value": "operational",
            "metadata": {
              "unit": "status",
              "lastReading": new Date().toISOString()
            }
          }
        ],
        "actions": [
          {
            "label": "Check Status",
            "type": "api",
            "endpoint": "https://api.example.com/device/status",
            "description": "Get current device status"
          }
        ],
        "services": [
          {
            "type": "http",
            "endpoint": "https://api.example.com/device/data",
            "updateFrequency": "PT5M",
            "authentication": "none"
          }
        ]
      };

    case 'app':
      return {
        ...baseTemplate,
        "features": [
          {
            "name": "Core Functionality",
            "type": "capability",
            "metadata": {
              "version": "1.0.0",
              "description": "Main application features"
            }
          }
        ],
        "actions": [
          {
            "label": "Launch App",
            "type": "link",
            "endpoint": "https://app.example.com",
            "description": "Open the application"
          },
          {
            "label": "API Access",
            "type": "api",
            "endpoint": "https://api.example.com",
            "description": "Access the application API"
          }
        ],
        "services": [
          {
            "type": "mcp",
            "endpoint": "mcp://app.example.com/service",
            "capabilities": ["query", "action", "notification"]
          }
        ],
        "persona": {
          "role": "Application Assistant",
          "personality": "efficient, knowledgeable",
          "expertise": ["software", "automation", "integration"],
          "prompt": "You are an assistant for this application. Help users understand features and capabilities."
        }
      };

    default:
      return baseTemplate;
  }
}

function getTypeFromString(type: string): string {
  switch (type.toLowerCase()) {
    case 'venue': return 'Venue';
    case 'device': return 'Device';
    case 'app': 
    case 'software':
    case 'application': return 'SoftwareApp';
    default: 
      throw new Error(`Unknown type: ${type}. Use: venue, device, or app`);
  }
}

function generateSampleId(type: string): string {
  const timestamp = Date.now().toString(36);
  switch (type) {
    case 'venue':
      return `clip:us:state:${type}:example-${timestamp}`;
    case 'device':
      return `clip:device:example-${timestamp}`;
    case 'app':
      return `clip:app:example-${timestamp}`;
    default:
      return `clip:example:${timestamp}`;
  }
}

function generateSampleName(type: string): string {
  switch (type) {
    case 'venue':
      return 'Example Venue';
    case 'device':
      return 'Example Device';
    case 'app':
      return 'Example Application';
    default:
      return 'Example CLIP Object';
  }
}

function generateSampleDescription(type: string): string {
  switch (type) {
    case 'venue':
      return 'An example venue template for CLIP. Replace with your venue description.';
    case 'device':
      return 'An example IoT device template for CLIP. Replace with your device description.';
    case 'app':
      return 'An example software application template for CLIP. Replace with your app description.';
    default:
      return 'An example CLIP object template. Replace with your description.';
  }
} 