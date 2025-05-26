"""
CLIP object validation using JSON Schema.
"""

import json
import logging
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlparse

import jsonschema
import requests
from jsonschema import Draft202012Validator, ValidationError, validate
from jsonschema.validators import RefResolver

from .utils import load_json_from_path

logger = logging.getLogger(__name__)


class CLIPValidationError(Exception):
    """Custom exception for CLIP validation errors."""

    def __init__(self, message: str, errors: Optional[List[Dict[str, Any]]] = None):
        super().__init__(message)
        self.errors = errors or []


class CLIPValidator:
    """
    A validator for CLIP JSON objects against the official CLIP schema.

    Features:
    - Remote schema fetching from official CLIP repository
    - Local schema caching
    - Detailed validation error reporting
    - Statistics and completeness analysis
    """

    DEFAULT_SCHEMA_URL = (
        "https://raw.githubusercontent.com/clip-organization/spec/main/clip.schema.json"
    )

    def __init__(
        self,
        schema_url: Optional[str] = None,
        schema_path: Optional[str] = None,
        cache_schema: bool = True,
        strict_mode: bool = False,
    ):
        """
        Initialize the CLIP validator.

        Args:
            schema_url: URL to fetch the CLIP schema from
            schema_path: Local path to a CLIP schema file
            cache_schema: Whether to cache the schema locally
            strict_mode: Enable strict validation mode
        """
        self.schema_url = schema_url or self.DEFAULT_SCHEMA_URL
        self.schema_path = schema_path
        self.cache_schema = cache_schema
        self.strict_mode = strict_mode
        self._schema: Optional[Dict[str, Any]] = None
        self._validator: Optional[Draft202012Validator] = None

    def load_schema(self) -> Dict[str, Any]:
        """
        Load the CLIP schema from URL or local file.

        Returns:
            The loaded JSON schema

        Raises:
            CLIPValidationError: If schema cannot be loaded
        """
        if self._schema is not None:
            return self._schema

        try:
            if self.schema_path:
                # Load from local file
                with open(self.schema_path, "r", encoding="utf-8") as f:
                    self._schema = json.load(f)
                logger.info(f"Loaded schema from local file: {self.schema_path}")
            else:
                # Fetch from URL
                response = requests.get(self.schema_url, timeout=30)
                response.raise_for_status()
                self._schema = response.json()
                logger.info(f"Fetched schema from URL: {self.schema_url}")

            return self._schema

        except (
            requests.RequestException,
            json.JSONDecodeError,
            FileNotFoundError,
        ) as e:
            raise CLIPValidationError(f"Failed to load CLIP schema: {str(e)}")

    def get_validator(self) -> Draft202012Validator:
        """
        Get a configured JSON schema validator.

        Returns:
            Configured validator instance
        """
        if self._validator is not None:
            return self._validator

        schema = self.load_schema()

        # Create validator with proper resolver for $ref resolution
        resolver = RefResolver.from_schema(schema)
        self._validator = Draft202012Validator(schema, resolver=resolver)

        return self._validator

    def validate(self, clip_object: Union[Dict[str, Any], str]) -> Dict[str, Any]:
        """
        Validate a CLIP object against the schema.

        Args:
            clip_object: CLIP object as dict or JSON string

        Returns:
            Validation result with errors, warnings, and statistics
        """
        # Parse if string
        if isinstance(clip_object, str):
            try:
                clip_object = json.loads(clip_object)
            except json.JSONDecodeError as e:
                return {
                    "valid": False,
                    "errors": [{"field": "root", "message": f"Invalid JSON: {str(e)}"}],
                    "warnings": [],
                    "stats": {},
                }

        validator = self.get_validator()
        errors = []
        warnings = []

        # Perform validation
        try:
            validator.validate(clip_object)
            is_valid = True
        except ValidationError:
            is_valid = False
            # Collect all validation errors
            for error in validator.iter_errors(clip_object):
                errors.append(self._format_validation_error(error))

        # Generate warnings for common issues
        warnings.extend(self._generate_warnings(clip_object))

        # Calculate statistics
        stats = self._calculate_statistics(clip_object)

        return {
            "valid": is_valid,
            "errors": errors,
            "warnings": warnings,
            "stats": stats,
        }

    def validate_file(self, file_path: str) -> Dict[str, Any]:
        """
        Validate a CLIP object from a file.

        Args:
            file_path: Path to JSON file containing CLIP object

        Returns:
            Validation result
        """
        try:
            clip_object = load_json_from_path(file_path)
            return self.validate(clip_object)
        except Exception as e:
            return {
                "valid": False,
                "errors": [{"field": "file", "message": str(e)}],
                "warnings": [],
                "stats": {},
            }

    def validate_url(self, url: str) -> Dict[str, Any]:
        """
        Validate a CLIP object from a URL.

        Args:
            url: URL to fetch CLIP object from

        Returns:
            Validation result
        """
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            clip_object = response.json()
            return self.validate(clip_object)
        except Exception as e:
            return {
                "valid": False,
                "errors": [{"field": "url", "message": str(e)}],
                "warnings": [],
                "stats": {},
            }

    def _format_validation_error(self, error: ValidationError) -> Dict[str, Any]:
        """Format a JSON schema validation error into a user-friendly format."""
        field_path = (
            ".".join(str(p) for p in error.absolute_path)
            if error.absolute_path
            else "root"
        )

        # Generate helpful suggestions based on error type
        suggestion = self._get_error_suggestion(error)

        return {
            "field": field_path,
            "message": error.message,
            "value": error.instance if hasattr(error, "instance") else None,
            "suggestion": suggestion,
        }

    def _get_error_suggestion(self, error: ValidationError) -> Optional[str]:
        """Generate helpful suggestions based on validation error."""
        if "required" in error.message:
            return (
                "This field is required. Make sure to include it in your CLIP object."
            )
        elif "format" in error.message:
            return "Check the format of this field. It may need to be a valid URL, email, or date."
        elif "type" in error.message:
            return "Check the data type. This field may need to be a string, number, object, or array."
        elif "enum" in error.message:
            return (
                "This field must be one of the allowed values specified in the schema."
            )
        return None

    def _generate_warnings(self, clip_object: Dict[str, Any]) -> List[str]:
        """Generate warnings for common issues that don't fail validation."""
        warnings = []

        # Check for stale lastUpdated
        if "lastUpdated" in clip_object:
            try:
                from datetime import datetime, timezone

                last_updated = datetime.fromisoformat(
                    clip_object["lastUpdated"].replace("Z", "+00:00")
                )
                days_old = (datetime.now(timezone.utc) - last_updated).days
                if days_old > 30:
                    warnings.append(
                        f"lastUpdated is {days_old} days old - consider updating"
                    )
            except (ValueError, TypeError):
                warnings.append("lastUpdated field has invalid date format")

        # Check for missing location in venues
        if clip_object.get("type") == "Venue" and "location" not in clip_object:
            warnings.append("Venues typically should include location information")

        # Check for short descriptions
        description = clip_object.get("description", "")
        if isinstance(description, str) and len(description) < 50:
            warnings.append("Consider providing a more detailed description")

        return warnings

    def _calculate_statistics(self, clip_object: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate statistics about the CLIP object."""
        stats = {
            "type": clip_object.get("type", "Unknown"),
            "featureCount": len(clip_object.get("features", [])),
            "actionCount": len(clip_object.get("actions", [])),
            "serviceCount": len(clip_object.get("services", [])),
            "hasLocation": "location" in clip_object,
            "hasPersona": "persona" in clip_object,
            "estimatedSize": len(json.dumps(clip_object, separators=(",", ":"))),
        }

        # Calculate completeness percentage
        total_fields = [
            "@context",
            "type",
            "id",
            "name",
            "description",
            "lastUpdated",
            "location",
            "features",
            "actions",
            "services",
            "persona",
        ]
        present_fields = sum(1 for field in total_fields if field in clip_object)
        stats["completeness"] = round((present_fields / len(total_fields)) * 100)

        return stats
