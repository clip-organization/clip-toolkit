/**
 * Utility functions for the CLIP Encoder CLI
 */

/**
 * Checks if a string is a valid HTTP/HTTPS URL
 * @param str - The string to check
 * @returns True if the string is a valid HTTP/HTTPS URL, false otherwise
 */
export function isURL(str: string): boolean {
  if (!str || typeof str !== 'string') {
    return false;
  }

  // Check for malformed protocol patterns (like http:/// instead of http://)
  if (str.includes('://') && (str.includes(':///') || str.endsWith('://'))) {
    return false;
  }

  try {
    const url = new URL(str);
    // Only accept HTTP and HTTPS protocols
    if (url.protocol !== 'http:' && url.protocol !== 'https:') {
      return false;
    }
    
    // Check for valid hostname
    if (!url.hostname || url.hostname.length === 0) {
      return false;
    }
    
    return true;
  } catch (error) {
    return false;
  }
}

/**
 * Formats bytes into a human-readable string
 * @param bytes - Number of bytes
 * @returns Formatted string (e.g., "1.2 KB")
 */
export function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

/**
 * Gets the appropriate color function for completeness percentage
 * @param completeness - Completeness percentage (0-100)
 * @returns Chalk color function
 */
export function getCompletenessColor(completeness: number) {
  const chalk = require('chalk');
  if (completeness >= 90) return chalk.green;
  if (completeness >= 70) return chalk.yellow;
  return chalk.red;
}

// Export custom validation functionality
export {
  ValidationRule,
  ValidationIssue,
  CustomValidator,
  formatValidationIssues,
  getValidationStats
} from './custom-validator'; 