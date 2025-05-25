"""
CLIP Python SDK

A Python SDK for working with CLIP (Context Link Interface Protocol) objects.
"""

__version__ = "0.1.0"

from .validator import CLIPValidator
from .fetcher import CLIPFetcher
from .clip_object import CLIPObject

__all__ = [
    "CLIPValidator",
    "CLIPFetcher", 
    "CLIPObject",
    "__version__"
] 