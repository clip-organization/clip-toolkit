#!/usr/bin/env node

import { Command } from 'commander';
import chalk from 'chalk';
import { validateCommand } from './commands/validate';
import { generateCommand } from './commands/generate';
import { statsCommand } from './commands/stats';
import { batchValidateCommand } from './commands/batch-validate';

// Import version from package.json
const packageJson = require('../package.json');

const program = new Command();

program
  .name('clip')
  .description('CLIP Toolkit CLI for validating and generating CLIP objects')
  .version(packageJson.version)
  .configureHelp({
    sortSubcommands: true,
    showGlobalOptions: true
  });

// Add global options
program
  .option('-v, --verbose', 'enable verbose logging')
  .option('--no-color', 'disable colored output');

// Validate command
program
  .command('validate')
  .description('Validate a CLIP JSON file against the schema and custom rules')
  .argument('<file>', 'Path to CLIP JSON file or URL')
  .option('-s, --schema <file>', 'Custom schema file path')
  .option('-o, --output <format>', 'Output format (text, json)', 'text')
  .option('--strict', 'Enable strict validation mode')
  .option('--no-warnings', 'Suppress warnings')
  .option('--exit-code', 'Return non-zero exit code on validation failure')
  .option('--no-custom-rules', 'Disable custom validation rules')
  .option('-r, --rules-file <file>', 'Load additional custom rules from JSON file')
  .action(validateCommand);

// Generate command
program
  .command('generate')
  .description('Generate a CLIP template')
  .requiredOption('-t, --type <type>', 'Type of CLIP object (venue, device, app)')
  .option('-o, --output <file>', 'Output file (default: stdout)')
  .option('--template <n>', 'Use a specific template')
  .option('--interactive', 'Interactive mode for filling template')
  .option('--minimal', 'Generate minimal template with required fields only')
  .action(generateCommand);

// Stats command
program
  .command('stats')
  .description('Show statistics about a CLIP object')
  .argument('<file>', 'Path to CLIP JSON file or URL')
  .option('-o, --output <format>', 'Output format (text, json)', 'text')
  .option('--detailed', 'Show detailed statistics')
  .action(statsCommand);

// Batch validate command
program
  .command('batch-validate')
  .description('Validate multiple CLIP files, directories, or URL patterns')
  .argument('<sources...>', 'Paths to CLIP files, directories, URLs, or glob patterns')
  .option('-s, --schema <file>', 'Custom schema file path')
  .option('-o, --output <format>', 'Output format (text, json)', 'text')
  .option('--strict', 'Enable strict validation mode')
  .option('--no-warnings', 'Suppress warnings')
  .option('--exit-code', 'Return non-zero exit code on validation failure')
  .option('-q, --quiet', 'Suppress detailed progress output')
  .option('--verbose', 'Show detailed error information')
  .option('--continue-on-error', 'Continue processing even when errors occur')
  .option('--no-custom-rules', 'Disable custom validation rules')
  .option('-r, --rules-file <file>', 'Load additional custom rules from JSON file')
  .action(async (sources: string[], options: any) => {
    const exitCode = await batchValidateCommand(sources, options);
    if (typeof exitCode === 'number' && exitCode !== 0) {
      process.exit(exitCode);
    }
  });

// Global error handler
program.exitOverride((err) => {
  if (err.code === 'commander.version') {
    console.log(packageJson.version);
    process.exit(0);
  }
  if (err.code === 'commander.helpDisplayed') {
    // Help was displayed, exit cleanly
    process.exit(0);
  }
  console.error(chalk.red('Error:'), err.message);
  process.exit(1);
});

// Handle unhandled promise rejections
process.on('unhandledRejection', (reason, promise) => {
  console.error(chalk.red('Unhandled Rejection at:'), promise, chalk.red('reason:'), reason);
  process.exit(1);
});

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
  console.error(chalk.red('Uncaught Exception:'), error);
  process.exit(1);
});

// Parse command line arguments
program.parse();

// If no arguments provided, show help
if (!process.argv.slice(2).length) {
  program.outputHelp();
  process.exit(0);
} 