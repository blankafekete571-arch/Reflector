"""
Vercel serverless function entry point
"""
import sys
import os

# Add parent directory to path to import navigate module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import and export the FastAPI app
from navigate import app

# This export is recognized by Vercel's Python builder
__all__ = ['app']
