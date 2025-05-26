import * as fs from 'fs/promises';
import * as path from 'path';
import chalk from 'chalk';
import ora from 'ora';
import axios from 'axios';
import { CLIPToolkit } from '@clip-toolkit/validator-core';
import { isURL, formatBytes, getCompletenessColor, CustomValidator, formatValidationIssues, getValidationStats } from '../utils';

interface ValidateOptions {
  schema?: string;
  output: 'text' | 'json';
  strict?: boolean;
  warnings?: boolean;
  exitCode?: boolean;
  verbose?: boolean;
  customRules?: boolean;
  rulesFile?: string;
}

export async function validateCommand(source: string, options: ValidateOptions) {
  const spinner = ora('Initializing CLIP validator...').start();
  
  try {
    // Initialize toolkit
    const toolkit = new CLIPToolkit({
      schema: options.schema ? { localSchemaPath: options.schema } : undefined,
      validator: {
        strict: options.strict
      }
    });

    spinner.text = isURL(source) ? 'Fetching CLIP object from URL...' : 'Loading CLIP object from file...';

    // Load CLIP object
    const clipObject = await loadClipObject(source);
    
    spinner.text = 'Validating CLIP object against schema...';

    // Schema validation
    const schemaResult = await toolkit.validate(clipObject);
    
    // Custom validation (enabled by default)
    let customIssues: any[] = [];
    if (options.customRules !== false) {
      spinner.text = 'Running custom validation rules...';
      
      const customValidator = new CustomValidator();
      
      // Load additional rules if specified
      if (options.rulesFile) {
        try {
          const customRules = await loadCustomRules(options.rulesFile);
          customRules.forEach(rule => customValidator.addRule(rule));
        } catch (error) {
          console.warn(chalk.yellow(`⚠️  Warning: Failed to load custom rules from ${options.rulesFile}: ${error instanceof Error ? error.message : String(error)}`));
        }
      }
      
      customIssues = customValidator.validate(clipObject);
    }

    spinner.stop();

    // Output results
    if (options.output === 'json') {
      const customStats = getValidationStats(customIssues);
      console.log(JSON.stringify({
        valid: schemaResult.valid && !customStats.hasErrors,
        schema: {
          valid: schemaResult.valid,
          errors: schemaResult.errors,
          warnings: options.warnings !== false ? schemaResult.warnings : undefined
        },
        custom: {
          total: customStats.total,
          errors: customStats.errors,
          warnings: customStats.warnings,
          info: customStats.info,
          issues: customIssues
        },
        stats: schemaResult.stats,
        source: source
      }, null, 2));
    } else {
      // Text output
      printTextOutput(schemaResult, customIssues, options, source);
    }

    // Exit with appropriate code
    const customStats = getValidationStats(customIssues);
    const overallValid = schemaResult.valid && !customStats.hasErrors;
    
    if (options.exitCode && !overallValid) {
      process.exit(1);
    }

  } catch (error) {
    spinner.stop();
    
    if (options.output === 'json') {
      console.log(JSON.stringify({
        valid: false,
        error: error instanceof Error ? error.message : String(error),
        source: source
      }, null, 2));
    } else {
      console.error(chalk.red('✗ Validation failed:'), error instanceof Error ? error.message : String(error));
    }
    
    if (options.exitCode) {
      process.exit(1);
    }
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

async function loadCustomRules(rulesFile: string) {
  try {
    const filePath = path.resolve(rulesFile);
    const content = await fs.readFile(filePath, 'utf-8');
    const rules = JSON.parse(content);
    
    if (!Array.isArray(rules)) {
      throw new Error('Custom rules file must contain an array of rules');
    }
    
    return rules;
  } catch (error) {
    throw new Error(`Failed to load custom rules: ${error instanceof Error ? error.message : String(error)}`);
  }
}

function printTextOutput(schemaResult: any, customIssues: any[], options: ValidateOptions, source: string) {
  const { valid: schemaValid, errors, warnings, stats } = schemaResult;
  const customStats = getValidationStats(customIssues);
  const overallValid = schemaValid && !customStats.hasErrors;
  
  // Header
  console.log(chalk.blue('CLIP Validation Report'));
  console.log(chalk.gray('─'.repeat(50)));
  console.log(`Source: ${chalk.cyan(source)}`);
  console.log(`Type: ${isURL(source) ? chalk.magenta('URL') : chalk.blue('File')}`);
  console.log(`Overall Status: ${overallValid ? chalk.green('✓ Valid') : chalk.red('✗ Invalid')}`);
  console.log();

  // Schema validation results
  console.log(chalk.blue('Schema Validation:'));
  console.log(`  Status: ${schemaValid ? chalk.green('✓ Valid') : chalk.red('✗ Invalid')}`);
  
  if (errors && errors.length > 0) {
    console.log(chalk.red(`  Errors (${errors.length}):`));
    errors.forEach((error: any, index: number) => {
      console.log(chalk.red(`    ${index + 1}. ${error.field}: ${error.message}`));
      if (error.suggestion && options.verbose) {
        console.log(chalk.yellow(`       💡 ${error.suggestion}`));
      }
    });
  }

  // Schema warnings
  if (warnings && warnings.length > 0 && options.warnings !== false) {
    console.log(chalk.yellow(`  Schema Warnings (${warnings.length}):`));
    warnings.forEach((warning: string, index: number) => {
      console.log(chalk.yellow(`    ${index + 1}. ${warning}`));
    });
  }

  console.log();

  // Custom validation results
  if (options.customRules !== false) {
    console.log(chalk.blue('Custom Validation:'));
    console.log(`  Status: ${!customStats.hasErrors ? chalk.green('✓ Passed') : chalk.red('✗ Failed')}`);
    
    if (customStats.total > 0) {
      console.log(`  Issues: ${customStats.errors} errors, ${customStats.warnings} warnings, ${customStats.info} info`);
      
      // Display custom issues
      customIssues.forEach((issue, index) => {
        const color = issue.severity === 'error' ? chalk.red :
                     issue.severity === 'warning' ? chalk.yellow :
                     chalk.blue;
        
        console.log(color(`    ${index + 1}. [${issue.severity.toUpperCase()}] [${issue.ruleId}] ${issue.message}`));
        console.log(chalk.gray(`       at ${issue.path}`));
        if (issue.suggestion && options.verbose) {
          console.log(chalk.cyan(`       💡 ${issue.suggestion}`));
        }
      });
    } else {
      console.log(chalk.green('    ✓ All custom validation rules passed'));
    }
    
    console.log();
  }

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

  // Summary
  if (overallValid) {
    console.log(chalk.green('✓ CLIP object is valid!'));
    if (stats?.completeness === 100) {
      console.log(chalk.green('🎉 CLIP object is complete with all optional fields!'));
    } else if (stats?.completeness && stats.completeness >= 70) {
      console.log(chalk.cyan('ℹ️  Consider adding more optional fields for better completeness.'));
    }
  } else {
    if (!schemaValid) {
      console.log(chalk.red('✗ CLIP object failed schema validation. Please fix the errors above.'));
    }
    if (customStats.hasErrors) {
      console.log(chalk.red('✗ CLIP object failed custom validation rules. Please address the errors above.'));
    }
  }
} 