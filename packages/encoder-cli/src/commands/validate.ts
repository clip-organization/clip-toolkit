import * as fs from 'fs';
import * as path from 'path';
import chalk from 'chalk';
import ora from 'ora';
import { CLIPToolkit } from '@clip-toolkit/validator-core';

interface ValidateOptions {
  schema?: string;
  output: 'text' | 'json';
  strict?: boolean;
  warnings?: boolean;
  exitCode?: boolean;
  verbose?: boolean;
}

export async function validateCommand(file: string, options: ValidateOptions) {
  const spinner = ora('Initializing CLIP validator...').start();
  
  try {
    // Initialize toolkit
    const toolkit = new CLIPToolkit({
      schema: options.schema ? { localSchemaPath: options.schema } : undefined,
      validator: {
        strict: options.strict
      }
    });

    spinner.text = 'Loading CLIP object...';

    // Load CLIP object
    const clipObject = await loadClipObject(file);
    
    spinner.text = 'Validating CLIP object...';

    // Validate
    const result = await toolkit.validate(clipObject);

    spinner.stop();

    // Output results
    if (options.output === 'json') {
      console.log(JSON.stringify({
        valid: result.valid,
        errors: result.errors,
        warnings: options.warnings !== false ? result.warnings : undefined,
        stats: result.stats
      }, null, 2));
    } else {
      // Text output
      printTextOutput(result, options, file);
    }

    // Exit with appropriate code
    if (options.exitCode && !result.valid) {
      process.exit(1);
    }

  } catch (error) {
    spinner.stop();
    
    if (options.output === 'json') {
      console.log(JSON.stringify({
        valid: false,
        error: error instanceof Error ? error.message : String(error)
      }, null, 2));
    } else {
      console.error(chalk.red('✗ Validation failed:'), error instanceof Error ? error.message : String(error));
    }
    
    if (options.exitCode) {
      process.exit(1);
    }
  }
}

async function loadClipObject(file: string): Promise<any> {
  // Check if it's a URL
  if (file.startsWith('http://') || file.startsWith('https://')) {
    const axios = await import('axios');
    const response = await axios.default.get(file);
    return response.data;
  }
  
  // Load from file
  const filePath = path.resolve(file);
  
  if (!fs.existsSync(filePath)) {
    throw new Error(`File not found: ${filePath}`);
  }
  
  const content = fs.readFileSync(filePath, 'utf8');
  
  try {
    return JSON.parse(content);
  } catch (_error) {
    throw new Error(`Invalid JSON in file: ${file}`);
  }
}

function printTextOutput(result: any, options: ValidateOptions, file: string) {
  const { valid, errors, warnings, stats } = result;
  
  // Header
  console.log(chalk.blue('CLIP Validation Report'));
  console.log(chalk.gray('─'.repeat(50)));
  console.log(`File: ${chalk.cyan(file)}`);
  console.log(`Status: ${valid ? chalk.green('✓ Valid') : chalk.red('✗ Invalid')}`);
  console.log();

  // Stats
  if (stats) {
    console.log(chalk.blue('Statistics:'));
    console.log(`  Type: ${chalk.cyan(stats.type)}`);
    console.log(`  Completeness: ${getCompletenessColor(stats.completeness)(stats.completeness + '%')}`);
    console.log(`  Size: ${chalk.cyan(formatBytes(stats.estimatedSize))}`);
    console.log(`  Features: ${chalk.cyan(stats.featureCount)}`);
    console.log(`  Actions: ${chalk.cyan(stats.actionCount)}`);
    console.log(`  Services: ${chalk.cyan(stats.serviceCount)}`);
    console.log(`  Has Location: ${stats.hasLocation ? chalk.green('Yes') : chalk.red('No')}`);
    console.log(`  Has Persona: ${stats.hasPersona ? chalk.green('Yes') : chalk.red('No')}`);
    console.log();
  }

  // Errors
  if (errors && errors.length > 0) {
    console.log(chalk.red(`Errors (${errors.length}):`));
    errors.forEach((error: any, index: number) => {
      console.log(chalk.red(`  ${index + 1}. ${error.field}: ${error.message}`));
      if (error.suggestion && options.verbose) {
        console.log(chalk.yellow(`     💡 ${error.suggestion}`));
      }
    });
    console.log();
  }

  // Warnings
  if (warnings && warnings.length > 0 && options.warnings !== false) {
    console.log(chalk.yellow(`Warnings (${warnings.length}):`));
    warnings.forEach((warning: string, index: number) => {
      console.log(chalk.yellow(`  ${index + 1}. ${warning}`));
    });
    console.log();
  }

  // Summary
  if (valid) {
    console.log(chalk.green('✓ CLIP object is valid!'));
    if (stats?.completeness === 100) {
      console.log(chalk.green('🎉 CLIP object is complete with all optional fields!'));
    } else if (stats?.completeness && stats.completeness >= 70) {
      console.log(chalk.cyan('ℹ️  Consider adding more optional fields for better completeness.'));
    }
  } else {
    console.log(chalk.red('✗ CLIP object is invalid. Please fix the errors above.'));
  }
}

function getCompletenessColor(completeness: number): typeof chalk.green {
  if (completeness >= 90) return chalk.green;
  if (completeness >= 70) return chalk.yellow;
  return chalk.red;
}

function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
} 