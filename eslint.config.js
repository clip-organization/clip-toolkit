import js from '@eslint/js';
import typescript from '@typescript-eslint/eslint-plugin';
import typescriptParser from '@typescript-eslint/parser';
import globals from 'globals';

export default [
  // Base configuration for all files
  {
    files: ['**/*.js', '**/*.ts'],
    languageOptions: {
      ecmaVersion: 2020,
      sourceType: 'module',
      globals: {
        ...globals.node,
        ...globals.es2020
      }
    },
    rules: {
      ...js.configs.recommended.rules,
      'no-unused-vars': 'warn',
      'prefer-const': 'error',
      'no-console': 'off'
    }
  },

  // TypeScript-specific configuration
  {
    files: ['**/*.ts'],
    languageOptions: {
      parser: typescriptParser,
      parserOptions: {
        ecmaVersion: 2020,
        sourceType: 'module'
      },
      globals: {
        ...globals.node,
        ...globals.es2020
      }
    },
    plugins: {
      '@typescript-eslint': typescript
    },
    rules: {
      ...js.configs.recommended.rules,
      'no-unused-vars': 'off',
      '@typescript-eslint/no-unused-vars': 'warn',
      '@typescript-eslint/no-explicit-any': 'off',
      'no-case-declarations': 'off',
      'no-prototype-builtins': 'off',
      'prefer-const': 'error',
      'no-console': 'off'
    }
  },

  // Jest test files
  {
    files: ['**/*.test.ts', '**/*.test.js', '**/*.spec.ts', '**/*.spec.js'],
    languageOptions: {
      globals: {
        ...globals.node,
        ...globals.jest,
        ...globals.es2020
      }
    }
  }
]; 