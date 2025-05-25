import axios from 'axios';
import * as fs from 'fs-extra';
import * as path from 'path';
import * as os from 'os';
import { SchemaManager, SchemaInfo } from '../src/schema-manager';

// Mock axios
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

// Mock fs-extra
jest.mock('fs-extra');
const mockedFs = fs as jest.Mocked<typeof fs>;

describe('SchemaManager', () => {
  let schemaManager: SchemaManager;
  let tempCachePath: string;

  const mockSchema = {
    $schema: 'https://json-schema.org/draft/2020-12/schema',
    $id: 'https://clipprotocol.org/schemas/v1/clip.schema.json',
    title: 'CLIP Schema v1.0',
    type: 'object',
    required: ['@context', 'type', 'id', 'name', 'description', 'lastUpdated']
  };

  beforeEach(() => {
    tempCachePath = path.join(os.tmpdir(), 'clip-toolkit-test-cache');
    schemaManager = new SchemaManager({
      cachePath: tempCachePath,
      remoteUrl: 'https://example.com/test-schema.json'
    });

    // Reset all mocks
    jest.clearAllMocks();
    
    // Setup default fs-extra mocks
    mockedFs.ensureDirSync.mockImplementation(() => {});
    mockedFs.existsSync.mockReturnValue(false);
  });

  describe('fetchLatestSchema', () => {
    it('should successfully fetch schema from remote URL', async () => {
      // Arrange
      mockedAxios.get.mockResolvedValue({
        status: 200,
        data: mockSchema
      });
      mockedFs.writeJson.mockResolvedValue();

      // Act
      const result = await schemaManager.fetchLatestSchema();

      // Assert
      expect(result.schema).toEqual(mockSchema);
      expect(result.source).toBe('remote');
      expect(result.version).toBe('1');
      expect(mockedAxios.get).toHaveBeenCalledWith(
        'https://example.com/test-schema.json',
        expect.objectContaining({
          timeout: 10000,
          headers: expect.objectContaining({
            'Accept': 'application/json',
            'User-Agent': 'clip-toolkit-validator-core'
          })
        })
      );
    });

    it('should throw error for non-200 HTTP status', async () => {
      // Arrange
      mockedAxios.get.mockResolvedValue({
        status: 404,
        data: {}
      });

      // Act & Assert
      await expect(schemaManager.fetchLatestSchema())
        .rejects
        .toThrow('HTTP 404: Failed to fetch schema');
    });

    it('should throw error for invalid schema format', async () => {
      // Arrange
      mockedAxios.get.mockResolvedValue({
        status: 200,
        data: { invalid: 'schema' } // Missing $schema property
      });

      // Act & Assert
      await expect(schemaManager.fetchLatestSchema())
        .rejects
        .toThrow('Invalid schema format: missing $schema property');
    });

    it('should handle network errors', async () => {
      // Arrange
      mockedAxios.get.mockRejectedValue(new Error('Network error'));

      // Act & Assert
      await expect(schemaManager.fetchLatestSchema())
        .rejects
        .toThrow('Network error');
    });
  });

  describe('getCachedSchema', () => {
    it('should load cached schema when files exist', () => {
      // Arrange
      mockedFs.existsSync.mockReturnValue(true);
      mockedFs.readJsonSync
        .mockReturnValueOnce(mockSchema) // schema file
        .mockReturnValueOnce({ // metadata file
          schema: mockSchema,
          version: '1',
          lastFetched: '2023-01-01T00:00:00.000Z',
          url: 'https://example.com/test-schema.json'
        });

      // Act
      const result = schemaManager.getCachedSchema();

      // Assert
      expect(result.schema).toEqual(mockSchema);
      expect(result.source).toBe('cache');
      expect(result.version).toBe('1');
    });

    it('should throw error when cache files do not exist', () => {
      // Arrange
      mockedFs.existsSync.mockReturnValue(false);

      // Act & Assert
      expect(() => schemaManager.getCachedSchema())
        .toThrow('No cached schema found');
    });
  });

  describe('getSchema', () => {
    it('should try remote first, then fallback to cache', async () => {
      // Arrange
      mockedAxios.get.mockRejectedValue(new Error('Network error'));
      mockedFs.existsSync.mockReturnValue(true);
      mockedFs.readJsonSync
        .mockReturnValueOnce(mockSchema)
        .mockReturnValueOnce({
          schema: mockSchema,
          version: '1',
          lastFetched: '2023-01-01T00:00:00.000Z',
          url: 'https://example.com/test-schema.json'
        });

      // Act
      const result = await schemaManager.getSchema();

      // Assert
      expect(result.source).toBe('cache');
      expect(mockedAxios.get).toHaveBeenCalled();
    });

    it('should throw error when all sources fail', async () => {
      // Arrange
      mockedAxios.get.mockRejectedValue(new Error('Network error'));
      mockedFs.existsSync.mockReturnValue(false);

      // Act & Assert
      await expect(schemaManager.getSchema())
        .rejects
        .toThrow('Unable to load CLIP schema from any source');
    });
  });

  describe('isCacheStale', () => {
    it('should return true when cache is older than maxAge', () => {
      // Arrange
      const oldDate = new Date(Date.now() - 48 * 60 * 60 * 1000); // 48 hours ago
      mockedFs.readJsonSync.mockReturnValue({
        lastFetched: oldDate.toISOString()
      });
      mockedFs.existsSync.mockReturnValue(true);

      // Act
      const isStale = schemaManager.isCacheStale(24 * 60 * 60 * 1000); // 24 hours

      // Assert
      expect(isStale).toBe(true);
    });

    it('should return false when cache is newer than maxAge', () => {
      // Arrange
      const recentDate = new Date(Date.now() - 12 * 60 * 60 * 1000); // 12 hours ago
      mockedFs.readJsonSync.mockReturnValue({
        lastFetched: recentDate.toISOString()
      });
      mockedFs.existsSync.mockReturnValue(true);

      // Act
      const isStale = schemaManager.isCacheStale(24 * 60 * 60 * 1000); // 24 hours

      // Assert
      expect(isStale).toBe(false);
    });
  });
}); 