#!/usr/bin/env python3
"""
Quick test to verify the simplified FastAPI server can be imported and created
"""

import sys
from pathlib import Path

# Add browser-use to path if running from source
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def test_simple_server():
    """Test that we can create the simplified FastAPI app"""
    try:
        from browser_use.api.simple_server import create_app
        
        print("✓ Successfully imported create_app from simple_server")
        
        app = create_app()
        print("✓ Successfully created FastAPI app")
        
        # Check some basic properties
        print(f"✓ App title: {app.title}")
        print(f"✓ App version: {app.version}")
        
        # Check that we have routes
        print(f"✓ Registered {len(app.routes)} routes")
        
        if len(app.routes) > 5:
            print("✓ App has expected number of routes")
        else:
            print("✗ App has fewer routes than expected")
        
        print("\n🎉 Simplified FastAPI server appears to be working correctly!")
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_simple_server()
    sys.exit(0 if success else 1)
