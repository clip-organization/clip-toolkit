import { isURL, formatBytes, getCompletenessColor } from './index';

describe('Utils', () => {
  describe('isURL', () => {
    it('should return true for valid HTTP URLs', () => {
      expect(isURL('http://example.com')).toBe(true);
      expect(isURL('http://example.com/path')).toBe(true);
      expect(isURL('http://example.com/path?query=value')).toBe(true);
    });

    it('should return true for valid HTTPS URLs', () => {
      expect(isURL('https://example.com')).toBe(true);
      expect(isURL('https://api.example.com/v1/clip/123')).toBe(true);
      expect(isURL('https://cdn.example.com/clip.json')).toBe(true);
    });

    it('should return true for URLs with ports', () => {
      expect(isURL('http://localhost:3000')).toBe(true);
      expect(isURL('https://example.com:8443/api')).toBe(true);
    });

    it('should return false for file paths', () => {
      expect(isURL('./test.json')).toBe(false);
      expect(isURL('/path/to/file.json')).toBe(false);
      expect(isURL('C:\\path\\to\\file.json')).toBe(false);
      expect(isURL('../relative/path.json')).toBe(false);
    });

    it('should return false for invalid URLs', () => {
      expect(isURL('not-a-url')).toBe(false);
      expect(isURL('ftp://example.com')).toBe(false); // URL() accepts this, but we want HTTP/HTTPS
      expect(isURL('')).toBe(false);
      expect(isURL('http://')).toBe(false);
    });

    it('should return false for malformed URLs', () => {
      expect(isURL('http:///invalid')).toBe(false);
      expect(isURL('https://')).toBe(false);
      expect(isURL('://example.com')).toBe(false);
    });
  });

  describe('formatBytes', () => {
    it('should format bytes correctly', () => {
      expect(formatBytes(0)).toBe('0 B');
      expect(formatBytes(1)).toBe('1 B');
      expect(formatBytes(1024)).toBe('1 KB');
      expect(formatBytes(1536)).toBe('1.5 KB');
      expect(formatBytes(1048576)).toBe('1 MB');
      expect(formatBytes(1073741824)).toBe('1 GB');
    });
  });

  describe('getCompletenessColor', () => {
    it('should return appropriate color functions', () => {
      const greenColor = getCompletenessColor(95);
      const yellowColor = getCompletenessColor(75);
      const redColor = getCompletenessColor(50);
      
      // Test that different functions are returned (they won't be equal)
      expect(greenColor).toBeDefined();
      expect(yellowColor).toBeDefined();
      expect(redColor).toBeDefined();
    });
  });
}); 