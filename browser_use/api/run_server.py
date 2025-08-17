#!/usr/bin/env python3
"""
Startup script for browser-use FastAPI server
"""

import sys
import os
from pathlib import Path

# Add browser-use to path if running from source
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

if __name__ == "__main__":
    from browser_use.api.server import main
    main()
