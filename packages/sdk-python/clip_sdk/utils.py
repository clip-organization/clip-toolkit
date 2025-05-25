"""
Utility functions for the CLIP SDK.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


def load_json_from_path(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Load JSON data from a file path.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Loaded JSON data as a dictionary
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        json.JSONDecodeError: If the file contains invalid JSON
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json_to_path(data: Dict[str, Any], file_path: Union[str, Path], 
                      indent: int = 2) -> None:
    """
    Save JSON data to a file path.
    
    Args:
        data: Data to save as JSON
        file_path: Path to save the file to
        indent: JSON indentation
    """
    path = Path(file_path)
    
    # Create parent directories if they don't exist
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)


def is_valid_clip_id(clip_id: str) -> bool:
    """
    Check if a string is a valid CLIP ID format.
    
    Args:
        clip_id: The ID to validate
        
    Returns:
        True if the ID follows CLIP format conventions
    """
    if not isinstance(clip_id, str):
        return False
    
    if not clip_id.startswith('clip:'):
        return False
    
    # Basic format check: clip:domain:type:identifier
    parts = clip_id.split(':')
    if len(parts) < 3:
        return False
    
    return True


def is_valid_clip_type(clip_type: str) -> bool:
    """
    Check if a string is a valid CLIP type.
    
    Args:
        clip_type: The type to validate
        
    Returns:
        True if the type is a valid CLIP type
    """
    valid_types = ['Venue', 'Device', 'SoftwareApp']
    return clip_type in valid_types


def is_valid_clip_context(context: str) -> bool:
    """
    Check if a string is a valid CLIP @context.
    
    Args:
        context: The @context to validate
        
    Returns:
        True if the context is valid for CLIP
    """
    if not isinstance(context, str):
        return False
    
    return 'clipprotocol.org' in context


def generate_clip_id(clip_type: str, domain: str = "local", 
                    identifier: Optional[str] = None) -> str:
    """
    Generate a CLIP ID following the standard format.
    
    Args:
        clip_type: Type of CLIP object (venue, device, app)
        domain: Domain identifier (default: "local")
        identifier: Unique identifier (auto-generated if not provided)
        
    Returns:
        Generated CLIP ID string
    """
    import uuid
    
    # Normalize type
    type_map = {
        'venue': 'venue',
        'device': 'device',
        'app': 'app',
        'software': 'app',
        'softwareapp': 'app'
    }
    
    normalized_type = type_map.get(clip_type.lower(), clip_type.lower())
    
    # Generate identifier if not provided
    if identifier is None:
        identifier = str(uuid.uuid4())[:8]
    
    return f"clip:{domain}:{normalized_type}:{identifier}"


def get_clip_object_hash(clip_object: Dict[str, Any]) -> str:
    """
    Generate a hash for a CLIP object for caching/comparison purposes.
    
    Args:
        clip_object: CLIP object dictionary
        
    Returns:
        Hash string
    """
    import hashlib
    
    # Create a stable string representation
    stable_str = json.dumps(clip_object, sort_keys=True, separators=(',', ':'))
    
    # Generate hash
    return hashlib.sha256(stable_str.encode('utf-8')).hexdigest()[:16]


def filter_clip_objects(clip_objects: List[Dict[str, Any]], 
                       filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Filter a list of CLIP objects based on criteria.
    
    Args:
        clip_objects: List of CLIP objects to filter
        filters: Dictionary of filter criteria
        
    Returns:
        Filtered list of CLIP objects
    """
    filtered = []
    
    for obj in clip_objects:
        matches = True
        
        for key, value in filters.items():
            if key not in obj:
                matches = False
                break
            
            if isinstance(value, str):
                # String matching (case-insensitive)
                if value.lower() not in str(obj[key]).lower():
                    matches = False
                    break
            elif isinstance(value, list):
                # List contains matching
                if obj[key] not in value:
                    matches = False
                    break
            else:
                # Exact matching
                if obj[key] != value:
                    matches = False
                    break
        
        if matches:
            filtered.append(obj)
    
    return filtered


def merge_clip_objects(base: Dict[str, Any], update: Dict[str, Any], 
                      prefer_update: bool = True) -> Dict[str, Any]:
    """
    Merge two CLIP objects.
    
    Args:
        base: Base CLIP object
        update: Update CLIP object
        prefer_update: Whether to prefer values from the update object
        
    Returns:
        Merged CLIP object
    """
    if prefer_update:
        merged = {**base, **update}
    else:
        merged = {**update, **base}
    
    # Handle array fields specially (merge rather than replace)
    array_fields = ['features', 'actions', 'services']
    
    for field in array_fields:
        if field in base and field in update:
            base_items = base[field] if isinstance(base[field], list) else []
            update_items = update[field] if isinstance(update[field], list) else []
            merged[field] = base_items + update_items
    
    return merged


def validate_clip_basic_structure(clip_object: Dict[str, Any]) -> List[str]:
    """
    Validate basic CLIP object structure and return any errors.
    
    Args:
        clip_object: CLIP object to validate
        
    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []
    
    if not isinstance(clip_object, dict):
        errors.append("CLIP object must be a dictionary")
        return errors
    
    # Check required fields
    required_fields = ['@context', 'type', 'id', 'name', 'description']
    for field in required_fields:
        if field not in clip_object:
            errors.append(f"Missing required field: {field}")
        elif not clip_object[field]:
            errors.append(f"Required field '{field}' is empty")
    
    # Validate @context
    context = clip_object.get('@context')
    if context and not is_valid_clip_context(context):
        errors.append(f"Invalid @context: {context}")
    
    # Validate type
    clip_type = clip_object.get('type')
    if clip_type and not is_valid_clip_type(clip_type):
        errors.append(f"Invalid type: {clip_type}")
    
    # Validate ID format
    clip_id = clip_object.get('id')
    if clip_id and not is_valid_clip_id(clip_id):
        errors.append(f"Invalid ID format: {clip_id}")
    
    return errors


def get_default_clip_context() -> str:
    """
    Get the default CLIP @context URL.
    
    Returns:
        Default CLIP @context string
    """
    return "https://clipprotocol.org/v1"


def create_minimal_clip_object(clip_type: str, name: str, description: str,
                              clip_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a minimal valid CLIP object.
    
    Args:
        clip_type: Type of CLIP object
        name: Name of the object
        description: Description of the object
        clip_id: Optional custom ID (auto-generated if not provided)
        
    Returns:
        Minimal CLIP object dictionary
    """
    from datetime import datetime, timezone
    
    # Validate type
    if not is_valid_clip_type(clip_type):
        raise ValueError(f"Invalid CLIP type: {clip_type}")
    
    # Generate ID if not provided
    if clip_id is None:
        clip_id = generate_clip_id(clip_type.lower())
    
    return {
        "@context": get_default_clip_context(),
        "type": clip_type,
        "id": clip_id,
        "name": name,
        "description": description,
        "lastUpdated": datetime.now(timezone.utc).isoformat()
    }


def discover_clip_files(directory: Union[str, Path], recursive: bool = True) -> List[str]:
    """
    Discover CLIP JSON files in a directory.
    
    Args:
        directory: Directory to search
        recursive: Whether to search recursively
        
    Returns:
        List of discovered CLIP file paths
    """
    directory_path = Path(directory)
    if not directory_path.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")
    
    pattern = "**/*.json" if recursive else "*.json"
    json_files = list(directory_path.glob(pattern))
    
    clip_files = []
    for file_path in json_files:
        try:
            data = load_json_from_path(file_path)
            errors = validate_clip_basic_structure(data)
            if not errors:  # If no validation errors, it's likely a CLIP file
                clip_files.append(str(file_path))
        except (json.JSONDecodeError, FileNotFoundError):
            continue
    
    return clip_files


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string
    """
    if size_bytes == 0:
        return "0 B"
    
    units = ["B", "KB", "MB", "GB"]
    unit_index = 0
    size = float(size_bytes)
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    return f"{size:.1f} {units[unit_index]}" 