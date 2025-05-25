"""
Tests for the CLIPObject class and related models.
"""

import json
import pytest
from datetime import datetime, timezone

from clip_sdk.clip_object import (
    CLIPObject, CLIPLocation, CLIPFeature, CLIPAction, 
    CLIPService, CLIPPersona
)


class TestCLIPLocation:
    
    def test_valid_location(self):
        """Test creating a valid location."""
        location = CLIPLocation(
            address="123 Main St",
            coordinates={"latitude": 40.7128, "longitude": -74.0060},
            timezone="America/New_York"
        )
        assert location.address == "123 Main St"
        assert location.coordinates["latitude"] == 40.7128
        assert location.timezone == "America/New_York"
    
    def test_invalid_coordinates(self):
        """Test validation of invalid coordinates."""
        with pytest.raises(ValueError, match="coordinates must have latitude and longitude"):
            CLIPLocation(coordinates={"latitude": 40.7128})
        
        with pytest.raises(ValueError, match="latitude must be between -90 and 90"):
            CLIPLocation(coordinates={"latitude": 100, "longitude": -74.0060})
        
        with pytest.raises(ValueError, match="longitude must be between -180 and 180"):
            CLIPLocation(coordinates={"latitude": 40.7128, "longitude": 200})


class TestCLIPObject:
    
    def test_create_minimal_clip_object(self):
        """Test creating a minimal CLIP object."""
        clip_obj = CLIPObject(
            **{
                "@context": "https://clipprotocol.org/v1",
                "type": "Venue",
                "id": "clip:test:venue:123",
                "name": "Test Venue",
                "description": "A test venue"
            }
        )
        
        assert clip_obj.context == "https://clipprotocol.org/v1"
        assert clip_obj.type == "Venue"
        assert clip_obj.id == "clip:test:venue:123"
        assert clip_obj.name == "Test Venue"
        assert clip_obj.description == "A test venue"
    
    def test_invalid_context(self):
        """Test validation of invalid @context."""
        with pytest.raises(ValueError, match="Invalid CLIP @context"):
            CLIPObject(
                **{
                    "@context": "https://invalid.com/context",
                    "type": "Venue",
                    "id": "clip:test:venue:123",
                    "name": "Test Venue",
                    "description": "A test venue"
                }
            )
    
    def test_invalid_type(self):
        """Test validation of invalid type."""
        with pytest.raises(ValueError, match="Type must be one of"):
            CLIPObject(
                **{
                    "@context": "https://clipprotocol.org/v1",
                    "type": "InvalidType",
                    "id": "clip:test:venue:123",
                    "name": "Test Venue",
                    "description": "A test venue"
                }
            )
    
    def test_invalid_id(self):
        """Test validation of invalid ID."""
        with pytest.raises(ValueError, match='ID must start with "clip:"'):
            CLIPObject(
                **{
                    "@context": "https://clipprotocol.org/v1",
                    "type": "Venue",
                    "id": "invalid:id",
                    "name": "Test Venue",
                    "description": "A test venue"
                }
            )
    
    def test_invalid_last_updated(self):
        """Test validation of invalid lastUpdated."""
        with pytest.raises(ValueError, match="lastUpdated must be a valid ISO 8601 datetime"):
            CLIPObject(
                **{
                    "@context": "https://clipprotocol.org/v1",
                    "type": "Venue",
                    "id": "clip:test:venue:123",
                    "name": "Test Venue",
                    "description": "A test venue",
                    "lastUpdated": "invalid-date"
                }
            )
    
    def test_from_dict(self):
        """Test creating CLIPObject from dictionary."""
        data = {
            "@context": "https://clipprotocol.org/v1",
            "type": "Device",
            "id": "clip:test:device:456",
            "name": "Test Device",
            "description": "A test device"
        }
        
        clip_obj = CLIPObject.from_dict(data)
        assert clip_obj.type == "Device"
        assert clip_obj.name == "Test Device"
    
    def test_from_json(self):
        """Test creating CLIPObject from JSON string."""
        json_str = json.dumps({
            "@context": "https://clipprotocol.org/v1",
            "type": "SoftwareApp",
            "id": "clip:test:app:789",
            "name": "Test App",
            "description": "A test application"
        })
        
        clip_obj = CLIPObject.from_json(json_str)
        assert clip_obj.type == "SoftwareApp"
        assert clip_obj.name == "Test App"
    
    def test_to_dict(self):
        """Test converting CLIPObject to dictionary."""
        clip_obj = CLIPObject(
            **{
                "@context": "https://clipprotocol.org/v1",
                "type": "Venue",
                "id": "clip:test:venue:123",
                "name": "Test Venue",
                "description": "A test venue"
            }
        )
        
        data = clip_obj.to_dict()
        assert data["@context"] == "https://clipprotocol.org/v1"
        assert data["type"] == "Venue"
        assert "lastUpdated" not in data  # Should be excluded as None
    
    def test_to_json(self):
        """Test converting CLIPObject to JSON string."""
        clip_obj = CLIPObject(
            **{
                "@context": "https://clipprotocol.org/v1",
                "type": "Device",
                "id": "clip:test:device:456",
                "name": "Test Device",
                "description": "A test device"
            }
        )
        
        json_str = clip_obj.to_json()
        data = json.loads(json_str)
        assert data["type"] == "Device"
        assert data["name"] == "Test Device"
    
    def test_update_timestamp(self):
        """Test updating the timestamp."""
        clip_obj = CLIPObject(
            **{
                "@context": "https://clipprotocol.org/v1",
                "type": "Venue",
                "id": "clip:test:venue:123",
                "name": "Test Venue",
                "description": "A test venue"
            }
        )
        
        assert clip_obj.lastUpdated is None
        
        clip_obj.update_timestamp()
        assert clip_obj.lastUpdated is not None
        
        # Parse the timestamp to ensure it's valid
        parsed_time = datetime.fromisoformat(clip_obj.lastUpdated.replace('Z', '+00:00'))
        assert isinstance(parsed_time, datetime)
    
    def test_add_feature(self):
        """Test adding a feature."""
        clip_obj = CLIPObject(
            **{
                "@context": "https://clipprotocol.org/v1",
                "type": "Venue",
                "id": "clip:test:venue:123",
                "name": "Test Venue",
                "description": "A test venue"
            }
        )
        
        clip_obj.add_feature("WiFi", "facility", available=True)
        
        assert len(clip_obj.features) == 1
        assert clip_obj.features[0].name == "WiFi"
        assert clip_obj.features[0].type == "facility"
    
    def test_add_action(self):
        """Test adding an action."""
        clip_obj = CLIPObject(
            **{
                "@context": "https://clipprotocol.org/v1",
                "type": "Device",
                "id": "clip:test:device:456",
                "name": "Test Device",
                "description": "A test device"
            }
        )
        
        clip_obj.add_action("Power On", "api", "https://device.com/power", description="Turn on the device")
        
        assert len(clip_obj.actions) == 1
        assert clip_obj.actions[0].label == "Power On"
        assert clip_obj.actions[0].type == "api"
        assert clip_obj.actions[0].endpoint == "https://device.com/power"
    
    def test_add_service(self):
        """Test adding a service."""
        clip_obj = CLIPObject(
            **{
                "@context": "https://clipprotocol.org/v1",
                "type": "SoftwareApp",
                "id": "clip:test:app:789",
                "name": "Test App",
                "description": "A test application"
            }
        )
        
        clip_obj.add_service("http", "https://api.app.com", capabilities=["query", "action"])
        
        assert len(clip_obj.services) == 1
        assert clip_obj.services[0].type == "http"
        assert clip_obj.services[0].endpoint == "https://api.app.com"
    
    def test_set_location(self):
        """Test setting location."""
        clip_obj = CLIPObject(
            **{
                "@context": "https://clipprotocol.org/v1",
                "type": "Venue",
                "id": "clip:test:venue:123",
                "name": "Test Venue",
                "description": "A test venue"
            }
        )
        
        clip_obj.set_location(
            address="123 Main St",
            coordinates={"latitude": 40.7128, "longitude": -74.0060},
            timezone="America/New_York"
        )
        
        assert clip_obj.location.address == "123 Main St"
        assert clip_obj.location.coordinates["latitude"] == 40.7128
    
    def test_set_persona(self):
        """Test setting persona."""
        clip_obj = CLIPObject(
            **{
                "@context": "https://clipprotocol.org/v1",
                "type": "Venue",
                "id": "clip:test:venue:123",
                "name": "Test Venue",
                "description": "A test venue"
            }
        )
        
        clip_obj.set_persona(
            role="Assistant",
            personality="helpful and friendly",
            expertise=["customer service", "information"],
            prompt="You are a helpful venue assistant."
        )
        
        assert clip_obj.persona.role == "Assistant"
        assert clip_obj.persona.personality == "helpful and friendly"
        assert "customer service" in clip_obj.persona.expertise
    
    def test_get_statistics(self):
        """Test getting statistics."""
        clip_obj = CLIPObject(
            **{
                "@context": "https://clipprotocol.org/v1",
                "type": "Venue",
                "id": "clip:test:venue:123",
                "name": "Test Venue",
                "description": "A test venue"
            }
        )
        
        clip_obj.add_feature("WiFi", "facility")
        clip_obj.add_action("Visit", "link", "https://venue.com")
        clip_obj.set_location(address="123 Main St")
        
        stats = clip_obj.get_statistics()
        
        assert stats['type'] == 'Venue'
        assert stats['featureCount'] == 1
        assert stats['actionCount'] == 1
        assert stats['serviceCount'] == 0
        assert stats['hasLocation'] is True
        assert stats['hasPersona'] is False
    
    def test_validate_completeness(self):
        """Test completeness validation."""
        clip_obj = CLIPObject(
            **{
                "@context": "https://clipprotocol.org/v1",
                "type": "Venue",
                "id": "clip:test:venue:123",
                "name": "Test Venue",
                "description": "A test venue",
                "lastUpdated": "2024-01-01T00:00:00Z"
            }
        )
        
        completeness = clip_obj.validate_completeness()
        
        assert 'completeness' in completeness
        assert 'missingFields' in completeness
        assert 'presentFields' in completeness
        assert completeness['completeness'] < 100  # Not all optional fields present
    
    def test_clone(self):
        """Test cloning a CLIP object."""
        original = CLIPObject(
            **{
                "@context": "https://clipprotocol.org/v1",
                "type": "Device",
                "id": "clip:test:device:456",
                "name": "Original Device",
                "description": "Original description"
            }
        )
        
        cloned = original.clone()
        
        assert cloned.name == "Original Device"
        assert cloned.id == original.id
        assert cloned is not original  # Different instances
    
    def test_string_representations(self):
        """Test string representations."""
        clip_obj = CLIPObject(
            **{
                "@context": "https://clipprotocol.org/v1",
                "type": "Venue",
                "id": "clip:test:venue:123",
                "name": "Test Venue",
                "description": "A test venue"
            }
        )
        
        str_repr = str(clip_obj)
        assert "Venue" in str_repr
        assert "Test Venue" in str_repr
        
        repr_str = repr(clip_obj)
        assert "CLIPObject" in repr_str
        assert "Venue" in repr_str 