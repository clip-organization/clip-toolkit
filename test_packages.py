#!/usr/bin/env python3
"""
Test script to verify that both Python packages work correctly.
"""

import sys
import os

# Add package paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'packages', 'sdk-python'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'packages', 'decoder-python'))

def test_sdk_python():
    """Test the sdk-python package."""
    print("Testing sdk-python package...")
    
    try:
        import clip_sdk
        print(f"✓ clip_sdk imported successfully (version: {clip_sdk.__version__})")
        
        # Test basic functionality
        from clip_sdk import CLIPValidator, CLIPFetcher
        
        validator = CLIPValidator()
        print("✓ CLIPValidator created successfully")
        
        fetcher = CLIPFetcher()
        print("✓ CLIPFetcher created successfully")
        
        print("✓ sdk-python package test passed")
        return True
        
    except Exception as e:
        print(f"✗ sdk-python package test failed: {e}")
        return False

def test_decoder_python():
    """Test the decoder-python package."""
    print("\nTesting decoder-python package...")
    
    try:
        import decoder_lib
        print("✓ decoder_lib imported successfully")
        
        # Test basic functionality
        from decoder_lib import get_library_info, get_supported_formats
        
        info = get_library_info()
        print(f"✓ Library info: {info['name']} v{info['version']}")
        
        formats = get_supported_formats()
        print(f"✓ Planned formats: {formats}")
        
        print("✓ decoder-python package test passed")
        return True
        
    except Exception as e:
        print(f"✗ decoder-python package test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("CLIP Toolkit Python Packages Test")
    print("=" * 40)
    
    sdk_ok = test_sdk_python()
    decoder_ok = test_decoder_python()
    
    print("\n" + "=" * 40)
    if sdk_ok and decoder_ok:
        print("✓ All package tests passed!")
        return 0
    else:
        print("✗ Some package tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 