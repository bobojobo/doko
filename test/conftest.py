"""
Test configuration for pytest.

This file automatically configures the Python path for all tests,
eliminating the need for manual sys.path manipulation in individual test files.
"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
