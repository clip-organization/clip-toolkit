"""
CLIP object fetching from various sources.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlparse

import requests

from .utils import load_json_from_path


logger = logging.getLogger(__name__)


class CLIPFetchError(Exception):
    """Custom exception for CLIP fetching errors."""
    pass


class CLIPFetcher:
    """
    A fetcher for CLIP objects from various sources.
    
    Features:
    - Fetch from URLs (HTTP/HTTPS)
    - Load from local files
    - Support for multiple CLIP objects
    - Caching capabilities
    - Timeout and retry handling
    """
    
    def __init__(
        self,
        timeout: float = 30.0,
        max_retries: int = 3,
        cache_enabled: bool = False,
        cache_dir: Optional[str] = None
    ):
        """
        Initialize the CLIP fetcher.
        
        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            cache_enabled: Whether to enable local caching
            cache_dir: Directory for cache files
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.cache_enabled = cache_enabled
        self.cache_dir = Path(cache_dir) if cache_dir else Path.home() / '.clip_sdk' / 'cache'
        
        if self.cache_enabled:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def fetch(self, source: str) -> Dict[str, Any]:
        """
        Fetch a CLIP object from a source (URL or file path).
        
        Args:
            source: URL or file path to fetch from
            
        Returns:
            The fetched CLIP object
            
        Raises:
            CLIPFetchError: If fetching fails
        """
        if self._is_url(source):
            return self.fetch_from_url(source)
        else:
            return self.fetch_from_file(source)
    
    def fetch_from_url(self, url: str) -> Dict[str, Any]:
        """
        Fetch a CLIP object from a URL.
        
        Args:
            url: URL to fetch from
            
        Returns:
            The fetched CLIP object
            
        Raises:
            CLIPFetchError: If fetching fails
        """
        # Check cache first
        if self.cache_enabled:
            cached_object = self._get_from_cache(url)
            if cached_object is not None:
                logger.info(f"Loaded CLIP object from cache for URL: {url}")
                return cached_object
        
        # Fetch from URL with retries
        last_exception = None
        for attempt in range(self.max_retries):
            try:
                response = requests.get(url, timeout=self.timeout)
                response.raise_for_status()
                
                # Parse JSON
                clip_object = response.json()
                
                # Validate basic CLIP structure
                self._validate_basic_structure(clip_object, url)
                
                # Cache if enabled
                if self.cache_enabled:
                    self._save_to_cache(url, clip_object)
                
                logger.info(f"Successfully fetched CLIP object from: {url}")
                return clip_object
                
            except (requests.RequestException, json.JSONDecodeError, ValueError) as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    logger.warning(f"Attempt {attempt + 1} failed for {url}: {str(e)}. Retrying...")
                else:
                    logger.error(f"All {self.max_retries} attempts failed for {url}")
        
        raise CLIPFetchError(f"Failed to fetch CLIP object from {url}: {str(last_exception)}")
    
    def fetch_from_file(self, file_path: str) -> Dict[str, Any]:
        """
        Fetch a CLIP object from a local file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            The fetched CLIP object
            
        Raises:
            CLIPFetchError: If fetching fails
        """
        try:
            clip_object = load_json_from_path(file_path)
            self._validate_basic_structure(clip_object, file_path)
            logger.info(f"Successfully loaded CLIP object from: {file_path}")
            return clip_object
            
        except Exception as e:
            raise CLIPFetchError(f"Failed to load CLIP object from {file_path}: {str(e)}")
    
    def fetch_multiple(self, sources: List[str]) -> List[Dict[str, Any]]:
        """
        Fetch multiple CLIP objects from a list of sources.
        
        Args:
            sources: List of URLs or file paths
            
        Returns:
            List of fetched CLIP objects
            
        Note:
            Failed fetches are logged but don't stop the process.
            Use get_failed_sources() to check for failures.
        """
        results = []
        self._failed_sources: List[Dict[str, str]] = []
        
        for source in sources:
            try:
                clip_object = self.fetch(source)
                results.append(clip_object)
            except CLIPFetchError as e:
                logger.error(f"Failed to fetch from {source}: {str(e)}")
                self._failed_sources.append({
                    'source': source,
                    'error': str(e)
                })
        
        return results
    
    def get_failed_sources(self) -> List[Dict[str, str]]:
        """
        Get list of sources that failed during the last fetch_multiple call.
        
        Returns:
            List of failed sources with error messages
        """
        return getattr(self, '_failed_sources', [])
    
    def discover_from_directory(self, directory: str, recursive: bool = True) -> List[str]:
        """
        Discover CLIP JSON files in a directory.
        
        Args:
            directory: Directory to search
            recursive: Whether to search recursively
            
        Returns:
            List of discovered file paths
        """
        directory_path = Path(directory)
        if not directory_path.exists():
            raise CLIPFetchError(f"Directory does not exist: {directory}")
        
        pattern = "**/*.json" if recursive else "*.json"
        json_files = list(directory_path.glob(pattern))
        
        # Filter to only include likely CLIP files
        clip_files = []
        for file_path in json_files:
            try:
                # Quick check for CLIP structure
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if self._is_likely_clip_object(data):
                        clip_files.append(str(file_path))
            except (json.JSONDecodeError, IOError):
                # Skip files that can't be read as JSON
                continue
        
        logger.info(f"Discovered {len(clip_files)} potential CLIP files in {directory}")
        return clip_files
    
    def clear_cache(self) -> None:
        """Clear all cached CLIP objects."""
        if self.cache_enabled and self.cache_dir.exists():
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()
            logger.info("Cleared CLIP object cache")
    
    def _is_url(self, source: str) -> bool:
        """Check if a source is a URL."""
        try:
            result = urlparse(source)
            return bool(result.scheme and result.netloc)
        except Exception:
            return False
    
    def _validate_basic_structure(self, clip_object: Dict[str, Any], source: str) -> None:
        """Validate basic CLIP object structure."""
        if not isinstance(clip_object, dict):
            raise ValueError(f"CLIP object must be a JSON object, got {type(clip_object)}")
        
        # Check for required fields
        required_fields = ['@context', 'type', 'id']
        missing_fields = [field for field in required_fields if field not in clip_object]
        if missing_fields:
            raise ValueError(f"Missing required CLIP fields: {missing_fields}")
        
        # Check for valid CLIP context
        context = clip_object.get('@context')
        if not isinstance(context, str) or 'clipprotocol.org' not in context:
            raise ValueError(f"Invalid or missing CLIP @context: {context}")
    
    def _is_likely_clip_object(self, data: Dict[str, Any]) -> bool:
        """Quick check to see if a JSON object is likely a CLIP object."""
        if not isinstance(data, dict):
            return False
            
        # Check for CLIP indicators
        context = data.get('@context', '')
        has_clip_context = isinstance(context, str) and 'clipprotocol.org' in context
        has_clip_type = data.get('type') in ['Venue', 'Device', 'SoftwareApp']
        has_clip_id = isinstance(data.get('id'), str) and data.get('id', '').startswith('clip:')
        
        return has_clip_context or has_clip_type or has_clip_id
    
    def _get_cache_path(self, url: str) -> Path:
        """Get the cache file path for a URL."""
        # Create a safe filename from URL
        safe_filename = url.replace('/', '_').replace(':', '_').replace('?', '_')
        if len(safe_filename) > 200:  # Limit filename length
            safe_filename = safe_filename[:200]
        return self.cache_dir / f"{safe_filename}.json"
    
    def _get_from_cache(self, url: str) -> Optional[Dict[str, Any]]:
        """Get a CLIP object from cache."""
        cache_path = self._get_cache_path(url)
        
        if cache_path.exists():
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Failed to load from cache {cache_path}: {str(e)}")
                # Remove corrupted cache file
                cache_path.unlink(missing_ok=True)
        
        return None
    
    def _save_to_cache(self, url: str, clip_object: Dict[str, Any]) -> None:
        """Save a CLIP object to cache."""
        cache_path = self._get_cache_path(url)
        
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(clip_object, f, indent=2)
        except IOError as e:
            logger.warning(f"Failed to save to cache {cache_path}: {str(e)}") 