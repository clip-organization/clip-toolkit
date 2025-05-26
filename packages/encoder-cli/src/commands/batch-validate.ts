import * as fs from 'fs/promises';
import * as path from 'path';
import chalk from 'chalk';
import ora from 'ora';
import { glob } from 'glob';
import { CLIPToolkit } from '@clip-toolkit/validator-core';
import { isURL, CustomValidator, getValidationStats } from '../utils';

// Load custom rules from a file
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

// Import the loadClipObject function from validate.ts
async function loadClipObject(source: string): Promise<any> {
  if (isURL(source)) {
    const axios = await import('axios');
    try {
      const response = await axios.default.get(source, {
        headers: {
          'Accept': 'application/json',
          'User-Agent': 'CLIP-Toolkit/1.0'
        },
        timeout: 30000,
        maxRedirects: 5
      });
      
      if (response.headers['content-type'] && 
          !response.headers['content-type'].includes('application/json')) {
        console.warn(chalk.yellow(`⚠️  Warning: Response content-type is not application/json for ${source}`));
      }
      
      return response.data;
    } catch (error) {
      if (axios.isAxiosError && axios.isAxiosError(error)) {
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

interface BatchValidateOptions {
  schema?: string;
  output: 'text' | 'json';
  strict?: boolean;
  warnings?: boolean;
  quiet?: boolean;
  verbose?: boolean;
  exitCode?: boolean;
  continueOnError?: boolean;
  customRules?: boolean;
  rulesFile?: string;
}

interface ValidationResult {
  source: string;
  sourceType: 'file' | 'url';
  valid: boolean;
  errors: any[];
  warnings?: any[];
  stats?: any;
  customIssues?: any[];
  processingTime: number;
}

interface BatchSummary {
  total: number;
  valid: number;
  invalid: number;
  errors: number;
  skipped: number;
  totalTime: number;
  results: ValidationResult[];
}

export async function batchValidateCommand(sources: string[], options: BatchValidateOptions) {
  const startTime = Date.now();
  const spinner = ora('Preparing batch validation...').start();
  
  try {
    // Initialize toolkit
    const toolkit = new CLIPToolkit({
      schema: options.schema ? { localSchemaPath: options.schema } : undefined,
      validator: {
        strict: options.strict
      }
    });

    // Expand sources (directories, globs, etc.)
    spinner.text = 'Expanding file patterns...';
    const expandedSources = await expandSources(sources);
    
    if (expandedSources.length === 0) {
      spinner.stop();
      console.log(chalk.yellow('No files found to validate.'));
      return options.exitCode ? 0 : undefined;
    }

    spinner.text = `Processing ${expandedSources.length} sources...`;
    
    const results: ValidationResult[] = [];
    let validCount = 0;
    let invalidCount = 0;
    let skippedCount = 0;

    // Process each source
    for (let i = 0; i < expandedSources.length; i++) {
      const source = expandedSources[i];
      const sourceIndex = i + 1;
      
      if (!options.quiet) {
        spinner.text = `[${sourceIndex}/${expandedSources.length}] Processing: ${source}`;
      }

      const sourceStartTime = Date.now();
      
      try {
        // Load CLIP object
        const clipObject = await loadClipObject(source);
        
        // Schema validation
        const schemaResult = await toolkit.validate(clipObject);
        
        // Custom validation (enabled by default)
        let customIssues: any[] = [];
        if (options.customRules !== false) {
          const customValidator = new CustomValidator();
          
          // Load additional rules if specified
          if (options.rulesFile) {
            try {
              const customRules = await loadCustomRules(options.rulesFile);
              customRules.forEach((rule: any) => customValidator.addRule(rule));
            } catch (error) {
              if (!options.quiet) {
                console.warn(chalk.yellow(`⚠️  Warning: Failed to load custom rules from ${options.rulesFile}: ${error instanceof Error ? error.message : String(error)}`));
              }
            }
          }
          
          customIssues = customValidator.validate(clipObject);
        }
        
        const processingTime = Date.now() - sourceStartTime;
        const customStats = getValidationStats(customIssues);
        const overallValid = schemaResult.valid && !customStats.hasErrors;
        
        const validationResult: ValidationResult = {
          source,
          sourceType: isURL(source) ? 'url' : 'file',
          valid: overallValid,
          errors: schemaResult.errors || [],
          warnings: schemaResult.warnings || [],
          stats: schemaResult.stats,
          customIssues: customIssues,
          processingTime
        };
        
        results.push(validationResult);
        
        if (overallValid) {
          validCount++;
          if (!options.quiet) {
            console.log(`${chalk.green('✓')} ${source}: Valid (${processingTime}ms)`);
          }
        } else {
          invalidCount++;
          const errorCount = schemaResult.errors.length + customStats.errors;
          if (!options.quiet) {
            console.log(`${chalk.red('✗')} ${source}: Invalid (${errorCount} errors, ${processingTime}ms)`);
            
            // Show errors if verbose or not quiet
            if (options.verbose) {
              // Show schema errors
              if (schemaResult.errors.length > 0) {
                console.log(chalk.red(`  Schema errors:`));
                schemaResult.errors.slice(0, 2).forEach((error: any, index: number) => {
                  console.log(chalk.red(`    ${index + 1}. ${error.field}: ${error.message}`));
                });
                if (schemaResult.errors.length > 2) {
                  console.log(chalk.gray(`    ... and ${schemaResult.errors.length - 2} more schema errors`));
                }
              }
              
              // Show custom errors
              const customErrors = customIssues.filter(issue => issue.severity === 'error');
              if (customErrors.length > 0) {
                console.log(chalk.red(`  Custom rule errors:`));
                customErrors.slice(0, 2).forEach((error: any, index: number) => {
                  console.log(chalk.red(`    ${index + 1}. [${error.ruleId}] ${error.message}`));
                });
                if (customErrors.length > 2) {
                  console.log(chalk.gray(`    ... and ${customErrors.length - 2} more custom errors`));
                }
              }
            }
          }
        }
        
      } catch (error) {
        skippedCount++;
        const processingTime = Date.now() - sourceStartTime;
        
        const validationResult: ValidationResult = {
          source,
          sourceType: isURL(source) ? 'url' : 'file',
          valid: false,
          errors: [{ field: 'loading', message: error instanceof Error ? error.message : String(error) }],
          processingTime
        };
        
        results.push(validationResult);
        
        if (!options.quiet) {
          console.log(`${chalk.red('✗')} ${source}: Error (${processingTime}ms)`);
          if (options.verbose) {
            console.log(chalk.red(`  ${error instanceof Error ? error.message : String(error)}`));
          }
        }
        
        // Exit early if not continuing on error
        if (!options.continueOnError) {
          spinner.stop();
          console.error(chalk.red('Stopping batch validation due to error. Use --continue-on-error to process all files.'));
          return options.exitCode ? 1 : undefined;
        }
      }
    }

    spinner.stop();
    
    // Generate summary
    const totalTime = Date.now() - startTime;
    const summary: BatchSummary = {
      total: expandedSources.length,
      valid: validCount,
      invalid: invalidCount,
      errors: invalidCount + skippedCount,
      skipped: skippedCount,
      totalTime,
      results
    };

    // Output results
    if (options.output === 'json') {
      console.log(JSON.stringify(summary, null, 2));
    } else {
      printSummary(summary, options);
    }

    // Return appropriate exit code
    const hasErrors = invalidCount > 0 || skippedCount > 0;
    return options.exitCode ? (hasErrors ? 1 : 0) : undefined;

  } catch (error) {
    spinner.stop();
    console.error(chalk.red('Batch validation failed:'), error instanceof Error ? error.message : String(error));
    return options.exitCode ? 1 : undefined;
  }
}

async function expandSources(sources: string[]): Promise<string[]> {
  const expandedSources: string[] = [];
  
  for (const source of sources) {
    // If it's a URL, add it directly
    if (isURL(source)) {
      expandedSources.push(source);
      continue;
    }
    
    try {
      // Check if it's a directory
      const stats = await fs.stat(source);
      if (stats.isDirectory()) {
        // Find all JSON files in directory recursively
        const pattern = path.join(source, '**/*.json');
        const files = await glob(pattern, { ignore: ['**/node_modules/**'] });
        expandedSources.push(...files);
        continue;
      }
    } catch (error) {
      // File might not exist, try as glob pattern
    }
    
    // Try as glob pattern
    if (source.includes('*') || source.includes('?') || source.includes('[')) {
      try {
        const files = await glob(source, { ignore: ['**/node_modules/**'] });
        expandedSources.push(...files);
      } catch (error) {
        // If glob fails, treat as regular file
        expandedSources.push(source);
      }
    } else {
      // Regular file path
      expandedSources.push(source);
    }
  }
  
  // Remove duplicates and sort
  return [...new Set(expandedSources)].sort();
}

function printSummary(summary: BatchSummary, options: BatchValidateOptions) {
  console.log();
  console.log(chalk.blue('Batch Validation Summary'));
  console.log(chalk.gray('═'.repeat(50)));
  
  // Overall stats
  console.log(`Total sources: ${chalk.cyan(summary.total)}`);
  console.log(`Valid: ${chalk.green(summary.valid)}`);
  console.log(`Invalid: ${chalk.red(summary.invalid)}`);
  if (summary.skipped > 0) {
    console.log(`Skipped: ${chalk.yellow(summary.skipped)}`);
  }
  console.log(`Processing time: ${chalk.cyan(summary.totalTime)}ms`);
  
  // Success rate
  const successRate = summary.total > 0 ? ((summary.valid / summary.total) * 100).toFixed(1) : '0';
  console.log(`Success rate: ${summary.valid === summary.total ? chalk.green(successRate + '%') : chalk.yellow(successRate + '%')}`);
  
  console.log();

  // Failed files summary
  const failedResults = summary.results.filter(r => !r.valid);
  if (failedResults.length > 0 && !options.quiet) {
    console.log(chalk.red('Failed validations:'));
    failedResults.forEach((result, index) => {
      console.log(`${chalk.red((index + 1).toString().padStart(2))}. ${result.source}`);
      if (options.verbose && result.errors.length > 0) {
        result.errors.slice(0, 2).forEach(error => {
          console.log(`     ${chalk.gray('•')} ${error.field}: ${error.message}`);
        });
        if (result.errors.length > 2) {
          console.log(`     ${chalk.gray('...')} +${result.errors.length - 2} more errors`);
        }
      }
    });
    console.log();
  }

  // Performance stats
  if (options.verbose) {
    const avgTime = summary.results.length > 0 ? 
      (summary.results.reduce((sum, r) => sum + r.processingTime, 0) / summary.results.length).toFixed(1) : '0';
    const slowest = summary.results.reduce((prev, current) => 
      (prev.processingTime > current.processingTime) ? prev : current, summary.results[0]);
    
    console.log(chalk.blue('Performance Statistics:'));
    console.log(`Average processing time: ${chalk.cyan(avgTime)}ms`);
    if (slowest) {
      console.log(`Slowest file: ${chalk.cyan(slowest.source)} (${slowest.processingTime}ms)`);
    }
    console.log();
  }

  // Recommendations
  if (summary.invalid > 0) {
    console.log(chalk.blue('💡 Recommendations:'));
    console.log('• Use --verbose to see detailed error information');
    console.log('• Use --continue-on-error to process all files even when errors occur');
    if (summary.skipped > 0) {
      console.log('• Check file paths and network connectivity for skipped files');
    }
  } else {
    console.log(chalk.green('🎉 All CLIP objects are valid!'));
  }
} 