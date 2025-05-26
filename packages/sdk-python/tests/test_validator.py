"""
Tests for the CLIPValidator class.
"""

import json
from unittest.mock import Mock, patch

import pytest

from clip_sdk.validator import CLIPValidationError, CLIPValidator


class TestCLIPValidator:
    def test_init_default(self):
        """Test validator initialization with defaults."""
        validator = CLIPValidator()
        assert validator.schema_url == CLIPValidator.DEFAULT_SCHEMA_URL
        assert validator.cache_schema is True
        assert validator.strict_mode is False

    def test_init_custom(self):
        """Test validator initialization with custom parameters."""
        validator = CLIPValidator(
            schema_url="https://custom.com/schema.json",
            schema_path="/path/to/schema.json",
            cache_schema=False,
            strict_mode=True,
        )
        assert validator.schema_url == "https://custom.com/schema.json"
        assert validator.schema_path == "/path/to/schema.json"
        assert validator.cache_schema is False
        assert validator.strict_mode is True

    @patch("clip_sdk.validator.requests.get")
    def test_load_schema_from_url(self, mock_get):
        """Test loading schema from URL."""
        mock_response = Mock()
        mock_response.json.return_value = {"$schema": "test"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        validator = CLIPValidator()
        schema = validator.load_schema()

        assert schema == {"$schema": "test"}
        mock_get.assert_called_once_with(validator.schema_url, timeout=30)

    def test_load_schema_from_file(self, tmp_path):
        """Test loading schema from local file."""
        schema_data = {"$schema": "test", "type": "object"}
        schema_file = tmp_path / "schema.json"
        schema_file.write_text(json.dumps(schema_data))

        validator = CLIPValidator(schema_path=str(schema_file))
        schema = validator.load_schema()

        assert schema == schema_data

    @patch("clip_sdk.validator.requests.get")
    def test_load_schema_network_error(self, mock_get):
        """Test handling of network errors when loading schema."""
        mock_get.side_effect = Exception("Network error")

        validator = CLIPValidator()

        with pytest.raises(CLIPValidationError, match="Failed to load CLIP schema"):
            validator.load_schema()

    def test_validate_valid_json_string(self):
        """Test validation with valid JSON string."""
        validator = CLIPValidator()

        # Mock the schema loading and validation
        with patch.object(validator, "get_validator") as mock_get_validator:
            mock_validator = Mock()
            mock_validator.validate.return_value = None
            mock_validator.iter_errors.return_value = []
            mock_get_validator.return_value = mock_validator

            json_str = '{"@context": "https://clipprotocol.org/v1", "type": "Venue"}'
            result = validator.validate(json_str)

            assert result["valid"] is True
            assert result["errors"] == []

    def test_validate_invalid_json(self):
        """Test validation with invalid JSON."""
        validator = CLIPValidator()

        invalid_json = '{"invalid": json}'
        result = validator.validate(invalid_json)

        assert result["valid"] is False
        assert len(result["errors"]) == 1
        assert "Invalid JSON" in result["errors"][0]["message"]

    def test_validate_dict_object(self):
        """Test validation with dictionary object."""
        validator = CLIPValidator()

        # Mock the schema loading and validation
        with patch.object(validator, "get_validator") as mock_get_validator:
            mock_validator = Mock()
            mock_validator.validate.return_value = None
            mock_validator.iter_errors.return_value = []
            mock_get_validator.return_value = mock_validator

            clip_object = {
                "@context": "https://clipprotocol.org/v1",
                "type": "Venue",
                "id": "clip:test:venue:123",
                "name": "Test Venue",
                "description": "A test venue",
            }
            result = validator.validate(clip_object)

            assert result["valid"] is True

    def test_generate_warnings_stale_timestamp(self):
        """Test warning generation for stale timestamps."""
        validator = CLIPValidator()

        clip_object = {"type": "Venue", "lastUpdated": "2020-01-01T00:00:00Z"}

        warnings = validator._generate_warnings(clip_object)
        assert any("days old" in warning for warning in warnings)

    def test_generate_warnings_venue_without_location(self):
        """Test warning generation for venue without location."""
        validator = CLIPValidator()

        clip_object = {"type": "Venue"}
        warnings = validator._generate_warnings(clip_object)

        assert any("location" in warning for warning in warnings)

    def test_calculate_statistics(self):
        """Test statistics calculation."""
        validator = CLIPValidator()

        clip_object = {
            "type": "Venue",
            "features": [{"name": "test"}],
            "actions": [{"label": "test"}, {"label": "test2"}],
            "services": [],
            "location": {"address": "test"},
            "persona": {"role": "test"},
        }

        stats = validator._calculate_statistics(clip_object)

        assert stats["type"] == "Venue"
        assert stats["featureCount"] == 1
        assert stats["actionCount"] == 2
        assert stats["serviceCount"] == 0
        assert stats["hasLocation"] is True
        assert stats["hasPersona"] is True
