import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Disable tracing before importing navigate
os.environ['ENABLE_PHOENIX_TRACING'] = 'false'

from navigate import app

__all__ = ['app']
