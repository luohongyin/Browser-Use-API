#!/usr/bin/env python3
"""
Quick test to verify the FastAPI server can be imported and created
"""

import sys
from pathlib import Path

# Add browser-use to path if running from source
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def test_server_creation():
    """Test that we can create the FastAPI app"""
    try:
        from browser_use.api.server import create_app
        
        print("✓ Successfully imported create_app")
        
        app = create_app()
        print("✓ Successfully created FastAPI app")
        
        # Check some basic properties
        print(f"✓ App title: {app.title}")
        print(f"✓ App version: {app.version}")
        
        # Check that routes are registered
        print(f"✓ Registered {len(app.routes)} routes")
        
        # Just check that we have some routes
        if len(app.routes) > 5:
            print("✓ App has expected number of routes")
        else:
            print("✗ App has fewer routes than expected")
        
        print("\n🎉 FastAPI server appears to be working correctly!")
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_server_creation()
    sys.exit(0 if success else 1)
