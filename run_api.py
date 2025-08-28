#!/usr/bin/env python3
"""
Simple runner script for the toolbelt API that sets up the Python path correctly.
Run this from the root directory: python3 run_api.py
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Now import and run the API
from api.api import app
import uvicorn

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
