import { batchValidateCommand } from '../batch-validate';

// Mock ora (spinner)
jest.mock('ora', () => ({
  __esModule: true,
  default: jest.fn(() => ({
    start: jest.fn().mockReturnThis(),
    stop: jest.fn().mockReturnThis(),
    text: ''
  }))
}));

// Mock CLIPToolkit
jest.mock('@clip-toolkit/validator-core', () => ({
  CLIPToolkit: jest.fn().mockImplementation(() => ({
    validate: jest.fn()
  }))
}));

// Mock glob
jest.mock('glob', () => ({
  glob: jest.fn()
}));

// Mock fs
jest.mock('fs/promises', () => ({
  stat: jest.fn(),
  readFile: jest.fn()
}));

// Mock console methods
const consoleSpy = {
  log: jest.spyOn(console, 'log').mockImplementation(),
  error: jest.spyOn(console, 'error').mockImplementation(),
  warn: jest.spyOn(console, 'warn').mockImplementation()
};

describe('Batch Validation', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    consoleSpy.log.mockClear();
    consoleSpy.error.mockClear();
    consoleSpy.warn.mockClear();
  });

  afterAll(() => {
    consoleSpy.log.mockRestore();
    consoleSpy.error.mockRestore();
    consoleSpy.warn.mockRestore();
  });

  describe('Multiple file validation', () => {
    it('should process multiple files and return summary', async () => {
      const { glob } = require('glob');
      const fs = require('fs/promises');
      const { CLIPToolkit } = require('@clip-toolkit/validator-core');

      // Mock glob to return test files
      glob.mockResolvedValue(['test1.json', 'test2.json']);

      // Mock file reading
      fs.readFile.mockResolvedValue('{"@context":"test","type":"Venue","id":"test","name":"test","description":"test"}');

      // Mock validation results
      const mockValidate = jest.fn()
        .mockResolvedValueOnce({ valid: true, errors: [], warnings: [], stats: {} })
        .mockResolvedValueOnce({ valid: false, errors: [{ field: 'test', message: 'test error' }], warnings: [] });
      
      CLIPToolkit.mockImplementation(() => ({ validate: mockValidate }));

      const result = await batchValidateCommand(['*.json'], {
        output: 'json',
        continueOnError: true,
        exitCode: true
      });

      expect(result).toBe(1); // Should return 1 due to invalid file
      expect(mockValidate).toHaveBeenCalledTimes(2);
      expect(consoleSpy.log).toHaveBeenCalledWith(
        expect.stringContaining('"total": 2')
      );
    });

    it('should handle empty file list', async () => {
      const { glob } = require('glob');
      glob.mockResolvedValue([]);

      const result = await batchValidateCommand(['*.json'], {
        output: 'text',
        exitCode: true
      });

      expect(result).toBe(0);
      expect(consoleSpy.log).toHaveBeenCalledWith(
        expect.stringContaining('No files found to validate')
      );
    });

    it('should stop on first error when continueOnError is false', async () => {
      const { glob } = require('glob');
      const fs = require('fs/promises');
      
      glob.mockResolvedValue(['test1.json']);
      fs.readFile.mockRejectedValue(new Error('File read error'));

      const result = await batchValidateCommand(['*.json'], {
        output: 'text',
        continueOnError: false,
        exitCode: true
      });

      expect(result).toBe(1);
      expect(consoleSpy.error).toHaveBeenCalledWith(
        expect.stringContaining('Stopping batch validation due to error')
      );
    });
  });

  describe('Output formats', () => {
    it('should support JSON output format', async () => {
      const { glob } = require('glob');
      const fs = require('fs/promises');
      const { CLIPToolkit } = require('@clip-toolkit/validator-core');

      glob.mockResolvedValue(['test.json']);
      fs.readFile.mockResolvedValue('{"@context":"test","type":"Venue","id":"test","name":"test","description":"test"}');
      
      const mockValidate = jest.fn().mockResolvedValue({
        valid: true,
        errors: [],
        warnings: [],
        stats: { type: 'Venue', completeness: 85 }
      });
      CLIPToolkit.mockImplementation(() => ({ validate: mockValidate }));

      await batchValidateCommand(['test.json'], {
        output: 'json',
        continueOnError: true,
        customRules: false  // Disable custom validation for this test
      });

      const lastCall = consoleSpy.log.mock.calls[consoleSpy.log.mock.calls.length - 1];
      expect(lastCall[0]).toContain('"total": 1');
      expect(lastCall[0]).toContain('"valid": 1');
    });

    it('should support text output format with summary', async () => {
      const { glob } = require('glob');
      const fs = require('fs/promises');
      const { CLIPToolkit } = require('@clip-toolkit/validator-core');

      glob.mockResolvedValue(['test.json']);
      fs.readFile.mockResolvedValue('{"@context":"test","type":"Venue","id":"test","name":"test","description":"test"}');
      
      const mockValidate = jest.fn().mockResolvedValue({
        valid: true,
        errors: [],
        warnings: [],
        stats: { type: 'Venue', completeness: 85 }
      });
      CLIPToolkit.mockImplementation(() => ({ validate: mockValidate }));

      await batchValidateCommand(['test.json'], {
        output: 'text',
        continueOnError: true
      });

      expect(consoleSpy.log).toHaveBeenCalledWith(
        expect.stringContaining('Batch Validation Summary')
      );
    });
  });

  describe('URL validation', () => {
    it('should handle URLs in batch validation', async () => {
      const { glob } = require('glob');
      const { CLIPToolkit } = require('@clip-toolkit/validator-core');

      // URLs should be passed through directly without glob expansion
      glob.mockResolvedValue([]);

      const mockValidate = jest.fn().mockResolvedValue({
        valid: true,
        errors: [],
        warnings: [],
        stats: {}
      });
      CLIPToolkit.mockImplementation(() => ({ validate: mockValidate }));

      // Mock axios for URL loading
      const mockAxios = {
        get: jest.fn().mockResolvedValue({
          data: { '@context': 'test', type: 'Venue', id: 'test', name: 'test', description: 'test' },
          headers: { 'content-type': 'application/json' }
        }),
        isAxiosError: jest.fn().mockReturnValue(false)
      };
      
      // Mock dynamic import of axios
      jest.doMock('axios', () => ({
        __esModule: true,
        default: mockAxios,
        isAxiosError: mockAxios.isAxiosError
      }));

      await batchValidateCommand(['https://example.com/clip.json'], {
        output: 'json',
        continueOnError: true
      });

      expect(mockValidate).toHaveBeenCalledWith({
        '@context': 'test',
        type: 'Venue',
        id: 'test',
        name: 'test',
        description: 'test'
      });
    });
  });
}); 