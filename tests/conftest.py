"""
Pytest configuration and shared fixtures.
"""

import pytest
import sys
from pathlib import Path

# Add the hooks directory to Python path for testing
project_root = Path(__file__).parent.parent
hooks_dir = project_root / "hooks"
sys.path.insert(0, str(hooks_dir))


@pytest.fixture
def sample_json_input():
    """Sample JSON input for hook testing."""
    return {
        "tool_name": "Write",
        "tool_input": {
            "file_path": "/test/example.py",
            "content": "print('Hello World')"
        }
    }


@pytest.fixture
def emoji_json_input():
    """JSON input containing emojis for testing."""
    return {
        "tool_name": "Write", 
        "tool_input": {
            "file_path": "/test/example.py",
            "content": "print('Hello World! 🚀')"
        }
    }


@pytest.fixture
def edit_json_input():
    """JSON input for Edit operation testing."""
    return {
        "tool_name": "Edit",
        "tool_input": {
            "file_path": "/test/example.py",
            "old_string": "old_code",
            "new_string": "new_code"
        }
    }


@pytest.fixture
def multiedit_json_input():
    """JSON input for MultiEdit operation testing."""
    return {
        "tool_name": "MultiEdit",
        "tool_input": {
            "file_path": "/test/example.py",
            "edits": [
                {"old_string": "old1", "new_string": "new1"},
                {"old_string": "old2", "new_string": "new2"}
            ]
        }
    }