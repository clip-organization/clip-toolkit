import axios, { AxiosError } from 'axios';
import { validateCommand } from '../validate';

// Mock axios for testing
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

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

// Mock console methods
const consoleSpy = {
  log: jest.spyOn(console, 'log').mockImplementation(),
  error: jest.spyOn(console, 'error').mockImplementation(),
  warn: jest.spyOn(console, 'warn').mockImplementation()
};

// Mock process.exit
const mockExit = jest.spyOn(process, 'exit').mockImplementation();

describe('Remote CLIP Validation', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    consoleSpy.log.mockClear();
    consoleSpy.error.mockClear();
    consoleSpy.warn.mockClear();
    mockExit.mockClear();
  });

  afterAll(() => {
    consoleSpy.log.mockRestore();
    consoleSpy.error.mockRestore();
    consoleSpy.warn.mockRestore();
    mockExit.mockRestore();
  });

  describe('Valid URLs returning valid CLIP objects', () => {
    it('should successfully validate a valid CLIP object from URL', async () => {
      const validClipObject = {
        '@context': 'https://clipprotocol.org/v1',
        'type': 'Venue',
        'id': 'clip:test:venue:123',
        'name': 'Test Venue',
        'description': 'A test venue'
      };

      mockedAxios.get.mockResolvedValueOnce({
        data: validClipObject,
        headers: { 'content-type': 'application/json' },
        status: 200,
        statusText: 'OK'
      });

      const { CLIPToolkit } = require('@clip-toolkit/validator-core');
      const mockValidate = jest.fn().mockResolvedValue({
        valid: true,
        errors: [],
        warnings: [],
        stats: { type: 'Venue', completeness: 85 }
      });
      CLIPToolkit.mockImplementation(() => ({ validate: mockValidate }));

      await validateCommand('https://api.example.com/clip/123', {
        output: 'json',
        exitCode: false
      });

      expect(mockedAxios.get).toHaveBeenCalledWith('https://api.example.com/clip/123', {
        headers: {
          'Accept': 'application/json',
          'User-Agent': 'CLIP-Toolkit/1.0'
        },
        timeout: 30000,
        maxRedirects: 5
      });

      expect(mockValidate).toHaveBeenCalledWith(validClipObject);
      expect(consoleSpy.log).toHaveBeenCalledWith(
        expect.stringContaining('"valid": true')
      );
    });

    it('should warn about non-JSON content type but proceed', async () => {
      const validClipObject = {
        '@context': 'https://clipprotocol.org/v1',
        'type': 'Venue',
        'id': 'clip:test:venue:123',
        'name': 'Test Venue',
        'description': 'A test venue'
      };

      mockedAxios.get.mockResolvedValueOnce({
        data: validClipObject,
        headers: { 'content-type': 'text/plain' },
        status: 200,
        statusText: 'OK'
      });

      const { CLIPToolkit } = require('@clip-toolkit/validator-core');
      const mockValidate = jest.fn().mockResolvedValue({
        valid: true,
        errors: [],
        warnings: [],
        stats: { type: 'Venue', completeness: 85 }
      });
      CLIPToolkit.mockImplementation(() => ({ validate: mockValidate }));

      await validateCommand('https://api.example.com/clip/123', {
        output: 'text',
        exitCode: false
      });

      expect(consoleSpy.warn).toHaveBeenCalledWith(
        expect.stringContaining('Response content-type is not application/json')
      );
    });
  });

  describe('Valid URLs returning invalid CLIP objects', () => {
    it('should handle validation errors for invalid CLIP objects from URL', async () => {
      const invalidClipObject = {
        'type': 'InvalidType',
        'name': 'Test'
        // Missing required fields
      };

      mockedAxios.get.mockResolvedValueOnce({
        data: invalidClipObject,
        headers: { 'content-type': 'application/json' },
        status: 200,
        statusText: 'OK'
      });

      const { CLIPToolkit } = require('@clip-toolkit/validator-core');
      const mockValidate = jest.fn().mockResolvedValue({
        valid: false,
        errors: [
          { field: '@context', message: 'Required field missing' },
          { field: 'id', message: 'Required field missing' }
        ],
        warnings: [],
        stats: { type: 'Unknown', completeness: 30 }
      });
      CLIPToolkit.mockImplementation(() => ({ validate: mockValidate }));

      await validateCommand('https://api.example.com/clip/invalid', {
        output: 'json',
        exitCode: false
      });

      expect(consoleSpy.log).toHaveBeenCalledWith(
        expect.stringContaining('"valid": false')
      );
    });
  });

  describe('URLs returning non-JSON responses', () => {
    it('should handle URLs returning HTML content', async () => {
      mockedAxios.get.mockResolvedValueOnce({
        data: '<html><body>Not JSON</body></html>',
        headers: { 'content-type': 'text/html' },
        status: 200,
        statusText: 'OK'
      });

      await validateCommand('https://example.com/not-json', {
        output: 'json',
        exitCode: false
      });

      expect(consoleSpy.warn).toHaveBeenCalledWith(
        expect.stringContaining('Response content-type is not application/json')
      );
    });
  });

  describe('URLs returning error status codes', () => {
    it('should handle 404 Not Found errors', async () => {
      const mockError: Partial<AxiosError> = {
        isAxiosError: true,
        response: {
          status: 404,
          statusText: 'Not Found',
          data: {},
          headers: {} as any,
          config: {
            headers: {} as any
          }
        } as any
      };

      mockedAxios.get.mockRejectedValueOnce(mockError);
      mockedAxios.isAxiosError.mockReturnValue(true);

      await validateCommand('https://api.example.com/clip/notfound', {
        output: 'json',
        exitCode: false
      });

      expect(consoleSpy.log).toHaveBeenCalledWith(
        expect.stringContaining('HTTP error 404: Not Found')
      );
    });

    it('should handle 500 Internal Server Error', async () => {
      const mockError: Partial<AxiosError> = {
        isAxiosError: true,
        response: {
          status: 500,
          statusText: 'Internal Server Error',
          data: {},
          headers: {} as any,
          config: {
            headers: {} as any
          }
        } as any
      };

      mockedAxios.get.mockRejectedValueOnce(mockError);
      mockedAxios.isAxiosError.mockReturnValue(true);

      await validateCommand('https://api.example.com/clip/error', {
        output: 'text',
        exitCode: false
      });

      expect(consoleSpy.error).toHaveBeenCalledWith(
        expect.anything(),
        expect.stringContaining('HTTP error 500: Internal Server Error')
      );
    });

    it('should handle 403 Forbidden errors', async () => {
      const mockError: Partial<AxiosError> = {
        isAxiosError: true,
        response: {
          status: 403,
          statusText: 'Forbidden',
          data: {},
          headers: {} as any,
          config: {
            headers: {} as any
          }
        } as any
      };

      mockedAxios.get.mockRejectedValueOnce(mockError);
      mockedAxios.isAxiosError.mockReturnValue(true);

      await validateCommand('https://api.example.com/clip/forbidden', {
        output: 'json',
        exitCode: false
      });

      expect(consoleSpy.log).toHaveBeenCalledWith(
        expect.stringContaining('HTTP error 403: Forbidden')
      );
    });
  });

  describe('Network failures', () => {
    it('should handle network timeout errors', async () => {
      const mockError: Partial<AxiosError> = {
        isAxiosError: true,
        code: 'ECONNABORTED',
        request: {}
      };

      mockedAxios.get.mockRejectedValueOnce(mockError);
      mockedAxios.isAxiosError.mockReturnValue(true);

      await validateCommand('https://timeout.example.com/clip/123', {
        output: 'json',
        exitCode: false
      });

      expect(consoleSpy.log).toHaveBeenCalledWith(
        expect.stringContaining('Network error: No response received')
      );
    });

    it('should handle no response network errors', async () => {
      const mockError: Partial<AxiosError> = {
        isAxiosError: true,
        request: {},
        code: 'ENOTFOUND'
      };

      mockedAxios.get.mockRejectedValueOnce(mockError);
      mockedAxios.isAxiosError.mockReturnValue(true);

      await validateCommand('https://nonexistent.example.com/clip/123', {
        output: 'text',
        exitCode: false
      });

      expect(consoleSpy.error).toHaveBeenCalledWith(
        expect.anything(),
        expect.stringContaining('Network error: No response received')
      );
    });

    it('should handle DNS resolution failures', async () => {
      const mockError = new Error('getaddrinfo ENOTFOUND nonexistent.example.com');

      mockedAxios.get.mockRejectedValueOnce(mockError);
      mockedAxios.isAxiosError.mockReturnValue(false);

      await validateCommand('https://nonexistent.example.com/clip/123', {
        output: 'json',
        exitCode: false
      });

      expect(consoleSpy.log).toHaveBeenCalledWith(
        expect.stringContaining('Failed to fetch CLIP object')
      );
    });

    it('should handle connection refused errors', async () => {
      const mockError: Partial<AxiosError> = {
        isAxiosError: true,
        code: 'ECONNREFUSED',
        request: {}
      };

      mockedAxios.get.mockRejectedValueOnce(mockError);
      mockedAxios.isAxiosError.mockReturnValue(true);

      await validateCommand('https://localhost:9999/clip/123', {
        output: 'text',
        exitCode: false
      });

      expect(consoleSpy.error).toHaveBeenCalledWith(
        expect.anything(),
        expect.stringContaining('Network error: No response received')
      );
    });
  });

  describe('Edge cases', () => {
    it('should handle redirects properly', async () => {
      const validClipObject = {
        '@context': 'https://clipprotocol.org/v1',
        'type': 'Venue',
        'id': 'clip:test:venue:123',
        'name': 'Test Venue',
        'description': 'A test venue'
      };

      mockedAxios.get.mockResolvedValueOnce({
        data: validClipObject,
        headers: { 'content-type': 'application/json' },
        status: 200,
        statusText: 'OK'
      });

      const { CLIPToolkit } = require('@clip-toolkit/validator-core');
      const mockValidate = jest.fn().mockResolvedValue({
        valid: true,
        errors: [],
        warnings: [],
        stats: { type: 'Venue', completeness: 85 }
      });
      CLIPToolkit.mockImplementation(() => ({ validate: mockValidate }));

      await validateCommand('https://short.ly/clip123', {
        output: 'json',
        exitCode: false
      });

      expect(mockedAxios.get).toHaveBeenCalledWith('https://short.ly/clip123', {
        headers: {
          'Accept': 'application/json',
          'User-Agent': 'CLIP-Toolkit/1.0'
        },
        timeout: 30000,
        maxRedirects: 5
      });
    });

    it('should handle URLs with query parameters and fragments', async () => {
      const validClipObject = {
        '@context': 'https://clipprotocol.org/v1',
        'type': 'Venue',
        'id': 'clip:test:venue:123',
        'name': 'Test Venue',
        'description': 'A test venue'
      };

      mockedAxios.get.mockResolvedValueOnce({
        data: validClipObject,
        headers: { 'content-type': 'application/json' },
        status: 200,
        statusText: 'OK'
      });

      const { CLIPToolkit } = require('@clip-toolkit/validator-core');
      const mockValidate = jest.fn().mockResolvedValue({
        valid: true,
        errors: [],
        warnings: [],
        stats: { type: 'Venue', completeness: 85 }
      });
      CLIPToolkit.mockImplementation(() => ({ validate: mockValidate }));

      await validateCommand('https://api.example.com/clip/123?format=json&version=v1#metadata', {
        output: 'json',
        exitCode: false
      });

      expect(mockedAxios.get).toHaveBeenCalledWith(
        'https://api.example.com/clip/123?format=json&version=v1#metadata',
        expect.any(Object)
      );
    });
  });
}); 