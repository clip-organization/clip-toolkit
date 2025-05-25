"""
Tests for the CLIPFetcher class.
"""

import json
import pytest
import requests
from unittest.mock import Mock, patch, mock_open
from pathlib import Path

from clip_sdk.fetcher import CLIPFetcher, CLIPFetchError


class TestCLIPFetcher:
    
    def test_init_default(self):
        """Test fetcher initialization with defaults."""
        fetcher = CLIPFetcher()
        assert fetcher.timeout == 30.0
        assert fetcher.max_retries == 3
        assert fetcher.cache_enabled is False
    
    def test_init_custom(self):
        """Test fetcher initialization with custom parameters."""
        fetcher = CLIPFetcher(
            timeout=60.0,
            max_retries=5,
            cache_enabled=True,
            cache_dir="/tmp/cache"
        )
        assert fetcher.timeout == 60.0
        assert fetcher.max_retries == 5
        assert fetcher.cache_enabled is True
        assert fetcher.cache_dir == Path("/tmp/cache")
    
    def test_is_url(self):
        """Test URL detection."""
        fetcher = CLIPFetcher()
        
        assert fetcher._is_url("https://example.com/clip.json") is True
        assert fetcher._is_url("http://example.com/clip.json") is True
        assert fetcher._is_url("/path/to/file.json") is False
        assert fetcher._is_url("file.json") is False
        assert fetcher._is_url("") is False
    
    @patch('clip_sdk.fetcher.requests.get')
    def test_fetch_from_url_success(self, mock_get):
        """Test successful URL fetching."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "@context": "https://clipprotocol.org/v1",
            "type": "Venue",
            "id": "clip:test:venue:123",
            "name": "Test Venue",
            "description": "A test venue"
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        fetcher = CLIPFetcher()
        result = fetcher.fetch_from_url("https://example.com/clip.json")
        
        assert result["type"] == "Venue"
        assert result["name"] == "Test Venue"
        mock_get.assert_called_once_with("https://example.com/clip.json", timeout=30.0)
    
    @patch('clip_sdk.fetcher.requests.get')
    def test_fetch_from_url_retry(self, mock_get):
        """Test URL fetching with retries."""
        # First two calls fail, third succeeds
        mock_response_success = Mock()
        mock_response_success.json.return_value = {"@context": "https://clipprotocol.org/v1", "type": "Venue", "id": "clip:test:venue:123"}
        mock_response_success.raise_for_status.return_value = None
        
        mock_get.side_effect = [
            requests.RequestException("Network error"),
            requests.RequestException("Timeout"),
            mock_response_success
        ]
        
        fetcher = CLIPFetcher(max_retries=3)
        result = fetcher.fetch_from_url("https://example.com/clip.json")
        
        assert result["type"] == "Venue"
        assert mock_get.call_count == 3
    
    @patch('clip_sdk.fetcher.requests.get')
    def test_fetch_from_url_all_retries_fail(self, mock_get):
        """Test URL fetching when all retries fail."""
        mock_get.side_effect = requests.RequestException("Network error")
        
        fetcher = CLIPFetcher(max_retries=2)
        
        with pytest.raises(CLIPFetchError, match="Failed to fetch CLIP object"):
            fetcher.fetch_from_url("https://example.com/clip.json")
        
        assert mock_get.call_count == 2
    
    def test_fetch_from_file_success(self, tmp_path):
        """Test successful file fetching."""
        clip_data = {
            "@context": "https://clipprotocol.org/v1",
            "type": "Device",
            "id": "clip:test:device:456",
            "name": "Test Device",
            "description": "A test device"
        }
        
        clip_file = tmp_path / "test_clip.json"
        clip_file.write_text(json.dumps(clip_data))
        
        fetcher = CLIPFetcher()
        result = fetcher.fetch_from_file(str(clip_file))
        
        assert result == clip_data
        assert result["type"] == "Device"
    
    def test_fetch_from_file_not_found(self):
        """Test file fetching with non-existent file."""
        fetcher = CLIPFetcher()
        
        with pytest.raises(CLIPFetchError, match="Failed to load CLIP object"):
            fetcher.fetch_from_file("/non/existent/file.json")
    
    def test_fetch_from_file_invalid_json(self, tmp_path):
        """Test file fetching with invalid JSON."""
        invalid_file = tmp_path / "invalid.json"
        invalid_file.write_text("{invalid json}")
        
        fetcher = CLIPFetcher()
        
        with pytest.raises(CLIPFetchError, match="Failed to load CLIP object"):
            fetcher.fetch_from_file(str(invalid_file))
    
    def test_fetch_multiple_success(self, tmp_path):
        """Test fetching multiple sources successfully."""
        # Create test files
        clip1_data = {"@context": "https://clipprotocol.org/v1", "type": "Venue", "id": "clip:test:venue:1"}
        clip2_data = {"@context": "https://clipprotocol.org/v1", "type": "Device", "id": "clip:test:device:2"}
        
        file1 = tmp_path / "clip1.json"
        file2 = tmp_path / "clip2.json"
        file1.write_text(json.dumps(clip1_data))
        file2.write_text(json.dumps(clip2_data))
        
        fetcher = CLIPFetcher()
        results = fetcher.fetch_multiple([str(file1), str(file2)])
        
        assert len(results) == 2
        assert results[0]["type"] == "Venue"
        assert results[1]["type"] == "Device"
    
    def test_fetch_multiple_with_failures(self, tmp_path):
        """Test fetching multiple sources with some failures."""
        # Create one valid file
        clip_data = {"@context": "https://clipprotocol.org/v1", "type": "Venue", "id": "clip:test:venue:1"}
        valid_file = tmp_path / "valid.json"
        valid_file.write_text(json.dumps(clip_data))
        
        fetcher = CLIPFetcher()
        results = fetcher.fetch_multiple([str(valid_file), "/non/existent/file.json"])
        
        assert len(results) == 1
        assert results[0]["type"] == "Venue"
        
        failed_sources = fetcher.get_failed_sources()
        assert len(failed_sources) == 1
        assert "/non/existent/file.json" in failed_sources[0]["source"]
    
    def test_validate_basic_structure_valid(self):
        """Test basic structure validation with valid CLIP object."""
        fetcher = CLIPFetcher()
        clip_object = {
            "@context": "https://clipprotocol.org/v1",
            "type": "Venue",
            "id": "clip:test:venue:123"
        }
        
        # Should not raise an exception
        fetcher._validate_basic_structure(clip_object, "test")
    
    def test_validate_basic_structure_invalid_context(self):
        """Test basic structure validation with invalid context."""
        fetcher = CLIPFetcher()
        clip_object = {
            "@context": "https://invalid.com/context",
            "type": "Venue",
            "id": "clip:test:venue:123"
        }
        
        with pytest.raises(ValueError, match="Invalid or missing CLIP @context"):
            fetcher._validate_basic_structure(clip_object, "test")
    
    def test_validate_basic_structure_missing_fields(self):
        """Test basic structure validation with missing required fields."""
        fetcher = CLIPFetcher()
        clip_object = {
            "@context": "https://clipprotocol.org/v1"
            # Missing type and id
        }
        
        with pytest.raises(ValueError, match="Missing required CLIP fields"):
            fetcher._validate_basic_structure(clip_object, "test")
    
    def test_is_likely_clip_object(self):
        """Test CLIP object detection."""
        fetcher = CLIPFetcher()
        
        # Valid CLIP objects
        assert fetcher._is_likely_clip_object({
            "@context": "https://clipprotocol.org/v1",
            "type": "Venue"
        }) is True
        
        assert fetcher._is_likely_clip_object({
            "type": "Device",
            "id": "clip:test:device:123"
        }) is True
        
        # Invalid objects
        assert fetcher._is_likely_clip_object({
            "name": "Not a CLIP object"
        }) is False
        
        assert fetcher._is_likely_clip_object("not a dict") is False 