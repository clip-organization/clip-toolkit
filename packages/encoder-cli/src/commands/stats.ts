import * as fs from 'fs/promises';
import * as path from 'path';
import chalk from 'chalk';
import ora from 'ora';
import axios from 'axios';
import { CLIPToolkit } from '@clip-toolkit/validator-core';
import { isURL, formatBytes, getCompletenessColor } from '../utils';

interface StatsOptions {
  output: 'text' | 'json';
  detailed?: boolean;
}

export async function statsCommand(source: string, options: StatsOptions) {
  const spinner = ora('Loading CLIP object...').start();
  
  try {
    // Initialize toolkit
    const toolkit = new CLIPToolkit();

    // Update spinner text based on source type
    spinner.text = isURL(source) ? 'Fetching CLIP object from URL...' : 'Loading CLIP object from file...';

    // Load CLIP object
    const clipObject = await loadClipObject(source);
    
    spinner.text = 'Analyzing CLIP object...';

    // Get validation result with stats
    const result = await toolkit.validate(clipObject);

    spinner.stop();

    // Generate detailed analysis
    const analysis = generateDetailedAnalysis(clipObject, result.stats);

    // Output results
    if (options.output === 'json') {
      console.log(JSON.stringify({
        ...result.stats,
        ...analysis,
        source: source,
        sourceType: isURL(source) ? 'url' : 'file'
      }, null, 2));
    } else {
      // Text output
      printStatsOutput(result.stats, analysis, options, source);
    }

  } catch (error) {
    spinner.stop();
    
    if (options.output === 'json') {
      console.log(JSON.stringify({
        error: error instanceof Error ? error.message : String(error),
        source: source,
        sourceType: isURL(source) ? 'url' : 'file'
      }, null, 2));
    } else {
      console.error(chalk.red('✗ Stats analysis failed:'), error instanceof Error ? error.message : String(error));
    }
    
    process.exit(1);
  }
}

async function loadClipObject(source: string): Promise<any> {
  if (isURL(source)) {
    try {
      const response = await axios.get(source, {
        headers: {
          'Accept': 'application/json',
          'User-Agent': 'CLIP-Toolkit/1.0'
        },
        timeout: 30000, // 30 second timeout
        maxRedirects: 5
      });
      
      // Validate that we received JSON
      if (response.headers['content-type'] && 
          !response.headers['content-type'].includes('application/json')) {
        console.warn(chalk.yellow('⚠️  Warning: Response content-type is not application/json'));
      }
      
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        if (error.response) {
          throw new Error(`HTTP error ${error.response.status}: ${error.response.statusText} when fetching ${source}`);
        } else if (error.request) {
          throw new Error(`Network error: No response received from ${source}`);
        } else if (error.code === 'ECONNABORTED') {
          throw new Error(`Request timeout when fetching ${source}`);
        }
      }
      throw new Error(`Failed to fetch CLIP object from ${source}: ${error instanceof Error ? error.message : String(error)}`);
    }
  } else {
    // Load from file
    try {
      const filePath = path.resolve(source);
      const content = await fs.readFile(filePath, 'utf-8');
      
      try {
        return JSON.parse(content);
      } catch (parseError) {
        throw new Error(`Invalid JSON in file: ${source} - ${parseError instanceof Error ? parseError.message : String(parseError)}`);
      }
    } catch (error: any) {
      if (error.code === 'ENOENT') {
        throw new Error(`File not found: ${source}`);
      } else if (error.code === 'EACCES') {
        throw new Error(`Permission denied reading file: ${source}`);
      } else if (error.code === 'EISDIR') {
        throw new Error(`Path is a directory, not a file: ${source}`);
      }
      throw new Error(`Failed to read file ${source}: ${error.message}`);
    }
  }
}

function generateDetailedAnalysis(clipObject: any, stats: any): any {
  const analysis: any = {
    structure: {
      topLevelFields: Object.keys(clipObject).length,
      requiredFields: countRequiredFields(clipObject),
      optionalFields: countOptionalFields(clipObject),
      nestedObjects: countNestedObjects(clipObject),
      arrays: countArrays(clipObject)
    },
    content: {
      hasContext: !!clipObject['@context'],
      hasTimestamp: !!clipObject.lastUpdated,
      timestampAge: clipObject.lastUpdated ? getTimestampAge(clipObject.lastUpdated) : null,
      descriptionLength: clipObject.description ? clipObject.description.length : 0,
      nameLength: clipObject.name ? clipObject.name.length : 0
    },
    compliance: {
      hasValidId: isValidId(clipObject.id),
      hasLocation: stats.hasLocation,
      hasPersona: stats.hasPersona,
      hasActions: stats.actionCount > 0,
      hasFeatures: stats.featureCount > 0,
      hasServices: stats.serviceCount > 0
    }
  };

  // Add feature analysis if available
  if (clipObject.features && Array.isArray(clipObject.features)) {
    analysis.features = analyzeFeatures(clipObject.features);
  }

  // Add action analysis if available
  if (clipObject.actions && Array.isArray(clipObject.actions)) {
    analysis.actions = analyzeActions(clipObject.actions);
  }

  // Add service analysis if available
  if (clipObject.services && Array.isArray(clipObject.services)) {
    analysis.services = analyzeServices(clipObject.services);
  }

  return analysis;
}

function printStatsOutput(stats: any, analysis: any, options: StatsOptions, source: string) {
  // Header
  console.log(chalk.blue('CLIP Object Statistics'));
  console.log(chalk.gray('═'.repeat(50)));
  console.log(`Source: ${chalk.cyan(source)}`);
  console.log(`Type: ${isURL(source) ? chalk.magenta('URL') : chalk.blue('File')}`);
  console.log(`CLIP Type: ${chalk.cyan(stats.type)}`);
  console.log();

  // Basic Stats
  console.log(chalk.blue('📊 Basic Statistics'));
  console.log(`  Size: ${chalk.cyan(formatBytes(stats.estimatedSize))}`);
  console.log(`  Completeness: ${getCompletenessColor(stats.completeness)(stats.completeness + '%')}`);
  console.log(`  Features: ${chalk.cyan(stats.featureCount)}`);
  console.log(`  Actions: ${chalk.cyan(stats.actionCount)}`);
  console.log(`  Services: ${chalk.cyan(stats.serviceCount)}`);
  console.log();

  // Structure Analysis
  console.log(chalk.blue('🏗️  Structure'));
  console.log(`  Top-level fields: ${chalk.cyan(analysis.structure.topLevelFields)}`);
  console.log(`  Required fields: ${chalk.cyan(analysis.structure.requiredFields)}`);
  console.log(`  Optional fields: ${chalk.cyan(analysis.structure.optionalFields)}`);
  console.log(`  Nested objects: ${chalk.cyan(analysis.structure.nestedObjects)}`);
  console.log(`  Arrays: ${chalk.cyan(analysis.structure.arrays)}`);
  console.log();

  // Content Analysis
  console.log(chalk.blue('📝 Content'));
  console.log(`  Has context: ${analysis.content.hasContext ? chalk.green('Yes') : chalk.red('No')}`);
  console.log(`  Has timestamp: ${analysis.content.hasTimestamp ? chalk.green('Yes') : chalk.red('No')}`);
  if (analysis.content.timestampAge) {
    const color = analysis.content.timestampAge.days > 30 ? chalk.yellow : chalk.green;
    console.log(`  Timestamp age: ${color(analysis.content.timestampAge.readable)}`);
  }
  console.log(`  Name length: ${chalk.cyan(analysis.content.nameLength)} characters`);
  console.log(`  Description length: ${chalk.cyan(analysis.content.descriptionLength)} characters`);
  console.log();

  // Compliance Check
  console.log(chalk.blue('✅ Compliance'));
  console.log(`  Valid ID format: ${analysis.compliance.hasValidId ? chalk.green('Yes') : chalk.red('No')}`);
  console.log(`  Has location: ${analysis.compliance.hasLocation ? chalk.green('Yes') : chalk.red('No')}`);
  console.log(`  Has persona: ${analysis.compliance.hasPersona ? chalk.green('Yes') : chalk.red('No')}`);
  console.log(`  Has actions: ${analysis.compliance.hasActions ? chalk.green('Yes') : chalk.red('No')}`);
  console.log(`  Has features: ${analysis.compliance.hasFeatures ? chalk.green('Yes') : chalk.red('No')}`);
  console.log(`  Has services: ${analysis.compliance.hasServices ? chalk.green('Yes') : chalk.red('No')}`);

  if (options.detailed) {
    // Detailed Feature Analysis
    if (analysis.features) {
      console.log();
      console.log(chalk.blue('🔧 Feature Details'));
      Object.entries(analysis.features.byType).forEach(([type, count]) => {
        console.log(`  ${type}: ${chalk.cyan(count)}`);
      });
    }

    // Detailed Action Analysis
    if (analysis.actions) {
      console.log();
      console.log(chalk.blue('⚡ Action Details'));
      Object.entries(analysis.actions.byType).forEach(([type, count]) => {
        console.log(`  ${type}: ${chalk.cyan(count)}`);
      });
    }

    // Detailed Service Analysis
    if (analysis.services) {
      console.log();
      console.log(chalk.blue('🔗 Service Details'));
      Object.entries(analysis.services.byType).forEach(([type, count]) => {
        console.log(`  ${type}: ${chalk.cyan(count)}`);
      });
    }
  }

  console.log();
  
  // Recommendations
  printRecommendations(stats, analysis);
}

function printRecommendations(stats: any, analysis: any) {
  console.log(chalk.blue('💡 Recommendations'));
  
  const recommendations = [];
  
  if (stats.completeness < 70) {
    recommendations.push('Consider adding more optional fields to improve completeness');
  }
  
  if (!analysis.compliance.hasLocation && stats.type === 'Venue') {
    recommendations.push('Venues should include location information');
  }
  
  if (!analysis.compliance.hasPersona) {
    recommendations.push('Adding a persona can enhance AI interactions');
  }
  
  if (analysis.content.timestampAge && analysis.content.timestampAge.days > 30) {
    recommendations.push('Consider updating the lastUpdated timestamp');
  }
  
  if (analysis.content.descriptionLength < 50) {
    recommendations.push('A more detailed description would be helpful');
  }
  
  if (stats.actionCount === 0) {
    recommendations.push('Adding actions makes your CLIP object more interactive');
  }

  if (recommendations.length === 0) {
    console.log(chalk.green('  ✨ Your CLIP object looks great!'));
  } else {
    recommendations.forEach((rec, index) => {
      console.log(`  ${index + 1}. ${chalk.yellow(rec)}`);
    });
  }
}

// Helper functions
function countRequiredFields(obj: any): number {
  const required = ['@context', 'type', 'id', 'name', 'description'];
  return required.filter(field => obj.hasOwnProperty(field)).length;
}

function countOptionalFields(obj: any): number {
  const required = ['@context', 'type', 'id', 'name', 'description'];
  return Object.keys(obj).filter(key => !required.includes(key)).length;
}

function countNestedObjects(obj: any): number {
  let count = 0;
  Object.values(obj).forEach(value => {
    if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
      count++;
    }
  });
  return count;
}

function countArrays(obj: any): number {
  let count = 0;
  Object.values(obj).forEach(value => {
    if (Array.isArray(value)) {
      count++;
    }
  });
  return count;
}

function isValidId(id: string): boolean {
  if (!id) return false;
  return id.startsWith('clip:') && id.split(':').length >= 3;
}

function getTimestampAge(timestamp: string): { days: number; readable: string } {
  const now = new Date();
  const ts = new Date(timestamp);
  const diffMs = now.getTime() - ts.getTime();
  const days = Math.floor(diffMs / (1000 * 60 * 60 * 24));
  
  let readable = '';
  if (days === 0) {
    const hours = Math.floor(diffMs / (1000 * 60 * 60));
    readable = `${hours} hours ago`;
  } else if (days === 1) {
    readable = '1 day ago';
  } else if (days < 30) {
    readable = `${days} days ago`;
  } else {
    const months = Math.floor(days / 30);
    readable = months === 1 ? '1 month ago' : `${months} months ago`;
  }
  
  return { days, readable };
}

function analyzeFeatures(features: any[]): any {
  const byType: { [key: string]: number } = {};
  features.forEach(feature => {
    const type = feature.type || 'unknown';
    byType[type] = (byType[type] || 0) + 1;
  });
  return { byType, total: features.length };
}

function analyzeActions(actions: any[]): any {
  const byType: { [key: string]: number } = {};
  actions.forEach(action => {
    const type = action.type || 'unknown';
    byType[type] = (byType[type] || 0) + 1;
  });
  return { byType, total: actions.length };
}

function analyzeServices(services: any[]): any {
  const byType: { [key: string]: number } = {};
  services.forEach(service => {
    const type = service.type || 'unknown';
    byType[type] = (byType[type] || 0) + 1;
  });
  return { byType, total: services.length };
} 