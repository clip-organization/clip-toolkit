"""
CLIP object models and manipulation.
"""

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, validator


class CLIPLocation(BaseModel):
    """Location information for CLIP objects."""
    address: Optional[str] = None
    coordinates: Optional[Dict[str, float]] = None
    timezone: Optional[str] = None
    
    @validator('coordinates')
    def validate_coordinates(cls, v):
        if v is not None:
            if not isinstance(v, dict):
                raise ValueError('coordinates must be a dictionary')
            if 'latitude' not in v or 'longitude' not in v:
                raise ValueError('coordinates must have latitude and longitude')
            if not (-90 <= v['latitude'] <= 90):
                raise ValueError('latitude must be between -90 and 90')
            if not (-180 <= v['longitude'] <= 180):
                raise ValueError('longitude must be between -180 and 180')
        return v


class CLIPFeature(BaseModel):
    """Feature information for CLIP objects."""
    name: str
    type: str
    value: Optional[Union[str, int, float, bool]] = None
    count: Optional[int] = None
    available: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


class CLIPAction(BaseModel):
    """Action information for CLIP objects."""
    label: str
    type: str
    endpoint: str
    description: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    authentication: Optional[str] = None


class CLIPService(BaseModel):
    """Service information for CLIP objects."""
    type: str
    endpoint: str
    updateFrequency: Optional[str] = None
    authentication: Optional[str] = None
    capabilities: Optional[List[str]] = None


class CLIPPersona(BaseModel):
    """Persona information for CLIP objects."""
    role: str
    personality: Optional[str] = None
    expertise: Optional[List[str]] = None
    prompt: Optional[str] = None


class CLIPObject(BaseModel):
    """
    A Pydantic model representing a CLIP object.
    
    This class provides validation, serialization, and manipulation
    capabilities for CLIP objects.
    """
    
    context: str = Field(alias='@context')
    type: str
    id: str
    name: str
    description: str
    lastUpdated: Optional[str] = None
    location: Optional[CLIPLocation] = None
    features: Optional[List[CLIPFeature]] = None
    actions: Optional[List[CLIPAction]] = None
    services: Optional[List[CLIPService]] = None
    persona: Optional[CLIPPersona] = None
    
    class Config:
        allow_population_by_field_name = True
        
    @validator('context')
    def validate_context(cls, v):
        if 'clipprotocol.org' not in v:
            raise ValueError('Invalid CLIP @context')
        return v
    
    @validator('type')
    def validate_type(cls, v):
        valid_types = ['Venue', 'Device', 'SoftwareApp']
        if v not in valid_types:
            raise ValueError(f'Type must be one of: {valid_types}')
        return v
    
    @validator('id')
    def validate_id(cls, v):
        if not v.startswith('clip:'):
            raise ValueError('ID must start with "clip:"')
        return v
    
    @validator('lastUpdated')
    def validate_last_updated(cls, v):
        if v is not None:
            try:
                datetime.fromisoformat(v.replace('Z', '+00:00'))
            except ValueError:
                raise ValueError('lastUpdated must be a valid ISO 8601 datetime')
        return v
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CLIPObject':
        """
        Create a CLIPObject from a dictionary.
        
        Args:
            data: Dictionary containing CLIP object data
            
        Returns:
            CLIPObject instance
        """
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'CLIPObject':
        """
        Create a CLIPObject from a JSON string.
        
        Args:
            json_str: JSON string containing CLIP object data
            
        Returns:
            CLIPObject instance
        """
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def to_dict(self, by_alias: bool = True, exclude_none: bool = True) -> Dict[str, Any]:
        """
        Convert the CLIPObject to a dictionary.
        
        Args:
            by_alias: Use field aliases (@context instead of context)
            exclude_none: Exclude None values from output
            
        Returns:
            Dictionary representation of the CLIP object
        """
        return self.dict(by_alias=by_alias, exclude_none=exclude_none)
    
    def to_json(self, by_alias: bool = True, exclude_none: bool = True, indent: int = 2) -> str:
        """
        Convert the CLIPObject to a JSON string.
        
        Args:
            by_alias: Use field aliases (@context instead of context)
            exclude_none: Exclude None values from output
            indent: JSON indentation
            
        Returns:
            JSON string representation of the CLIP object
        """
        data = self.to_dict(by_alias=by_alias, exclude_none=exclude_none)
        return json.dumps(data, indent=indent, ensure_ascii=False)
    
    def update_timestamp(self) -> None:
        """Update the lastUpdated timestamp to current time."""
        self.lastUpdated = datetime.now(timezone.utc).isoformat()
    
    def add_feature(self, name: str, type: str, **kwargs) -> None:
        """
        Add a feature to the CLIP object.
        
        Args:
            name: Feature name
            type: Feature type
            **kwargs: Additional feature properties
        """
        if self.features is None:
            self.features = []
        
        feature = CLIPFeature(name=name, type=type, **kwargs)
        self.features.append(feature)
    
    def add_action(self, label: str, type: str, endpoint: str, **kwargs) -> None:
        """
        Add an action to the CLIP object.
        
        Args:
            label: Action label
            type: Action type
            endpoint: Action endpoint
            **kwargs: Additional action properties
        """
        if self.actions is None:
            self.actions = []
        
        action = CLIPAction(label=label, type=type, endpoint=endpoint, **kwargs)
        self.actions.append(action)
    
    def add_service(self, type: str, endpoint: str, **kwargs) -> None:
        """
        Add a service to the CLIP object.
        
        Args:
            type: Service type
            endpoint: Service endpoint
            **kwargs: Additional service properties
        """
        if self.services is None:
            self.services = []
        
        service = CLIPService(type=type, endpoint=endpoint, **kwargs)
        self.services.append(service)
    
    def set_location(self, address: Optional[str] = None, 
                    coordinates: Optional[Dict[str, float]] = None,
                    timezone: Optional[str] = None) -> None:
        """
        Set location information for the CLIP object.
        
        Args:
            address: Physical address
            coordinates: Latitude/longitude coordinates
            timezone: Timezone identifier
        """
        self.location = CLIPLocation(
            address=address,
            coordinates=coordinates,
            timezone=timezone
        )
    
    def set_persona(self, role: str, personality: Optional[str] = None,
                   expertise: Optional[List[str]] = None,
                   prompt: Optional[str] = None) -> None:
        """
        Set persona information for the CLIP object.
        
        Args:
            role: Persona role
            personality: Personality description
            expertise: List of expertise areas
            prompt: AI prompt for the persona
        """
        self.persona = CLIPPersona(
            role=role,
            personality=personality,
            expertise=expertise,
            prompt=prompt
        )
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the CLIP object.
        
        Returns:
            Dictionary with statistics
        """
        return {
            'type': self.type,
            'featureCount': len(self.features) if self.features else 0,
            'actionCount': len(self.actions) if self.actions else 0,
            'serviceCount': len(self.services) if self.services else 0,
            'hasLocation': self.location is not None,
            'hasPersona': self.persona is not None,
            'estimatedSize': len(self.to_json(exclude_none=True, indent=None))
        }
    
    def validate_completeness(self) -> Dict[str, Any]:
        """
        Validate the completeness of the CLIP object.
        
        Returns:
            Dictionary with completeness information
        """
        total_fields = ['@context', 'type', 'id', 'name', 'description', 'lastUpdated',
                       'location', 'features', 'actions', 'services', 'persona']
        
        present_fields = 0
        missing_fields = []
        
        data = self.to_dict(by_alias=True, exclude_none=True)
        
        for field in total_fields:
            if field in data and data[field] is not None:
                present_fields += 1
            else:
                missing_fields.append(field)
        
        completeness = round((present_fields / len(total_fields)) * 100)
        
        return {
            'completeness': completeness,
            'presentFields': present_fields,
            'totalFields': len(total_fields),
            'missingFields': missing_fields
        }
    
    def merge_with(self, other: 'CLIPObject', prefer_other: bool = True) -> 'CLIPObject':
        """
        Merge this CLIP object with another, creating a new object.
        
        Args:
            other: Other CLIPObject to merge with
            prefer_other: Whether to prefer values from the other object
            
        Returns:
            New merged CLIPObject
        """
        if prefer_other:
            base_data = self.to_dict(exclude_none=True)
            other_data = other.to_dict(exclude_none=True)
            merged_data = {**base_data, **other_data}
        else:
            base_data = other.to_dict(exclude_none=True)
            other_data = self.to_dict(exclude_none=True)
            merged_data = {**base_data, **other_data}
        
        return CLIPObject.from_dict(merged_data)
    
    def clone(self) -> 'CLIPObject':
        """
        Create a deep copy of the CLIP object.
        
        Returns:
            New CLIPObject instance
        """
        return CLIPObject.from_dict(self.to_dict())
    
    def __str__(self) -> str:
        """String representation of the CLIP object."""
        return f"CLIPObject(type={self.type}, id={self.id}, name={self.name})"
    
    def __repr__(self) -> str:
        """Developer representation of the CLIP object."""
        return f"CLIPObject(type='{self.type}', id='{self.id}', name='{self.name}')" 