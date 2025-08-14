"""
Integration tests for Claude Code Hooks.

These tests verify that hooks work correctly when called as modules
and integrate properly with the overall hook system.
"""

import json
import subprocess
import sys
from pathlib import Path
import pytest

# Path to the hooks
HOOKS_DIR = Path(__file__).parent.parent.parent / "hooks"
EMOJI_HOOK_PATH = HOOKS_DIR / "check-no-emojis.py"


class TestEmojiHookIntegration:
    """Integration tests for the emoji checker hook."""

    def test_hook_allows_clean_content(self):
        """Test that hook allows content without emojis."""
        input_data = {
            "tool_name": "Write",
            "tool_input": {
                "file_path": "test.py",
                "content": "def hello():\n    print('Hello World')\n    return True"
            }
        }
        
        # Run the hook as a subprocess
        process = subprocess.run(
            [sys.executable, str(EMOJI_HOOK_PATH)],
            input=json.dumps(input_data),
            text=True,
            capture_output=True
        )
        
        # Should exit with code 0 (allowed)
        assert process.returncode == 0
        assert process.stdout.strip() == ""

    def test_hook_blocks_emoji_content(self):
        """Test that hook blocks content with emojis."""
        input_data = {
            "tool_name": "Write",
            "tool_input": {
                "file_path": "test.py",
                "content": "def hello():\n    print('Hello World! 🚀')\n    return True"
            }
        }
        
        # Run the hook as a subprocess
        process = subprocess.run(
            [sys.executable, str(EMOJI_HOOK_PATH)],
            input=json.dumps(input_data),
            text=True,
            capture_output=True
        )
        
        # Should exit with code 0 but output hook result
        assert process.returncode == 0
        
        # Parse the JSON output
        output = json.loads(process.stdout)
        assert output["hookSpecificOutput"]["permissionDecision"] == "deny"
        assert "🚀" in output["hookSpecificOutput"]["permissionDecisionReason"]

    def test_hook_allows_monochrome_symbols(self):
        """Test that hook allows monochrome Unicode symbols."""
        input_data = {
            "tool_name": "Write",
            "tool_input": {
                "file_path": "test.py",
                "content": "# Status: ✓ Complete\n# Progress: →\n• Item 1\n• Item 2"
            }
        }
        
        # Run the hook as a subprocess
        process = subprocess.run(
            [sys.executable, str(EMOJI_HOOK_PATH)],
            input=json.dumps(input_data),
            text=True,
            capture_output=True
        )
        
        # Should exit with code 0 (allowed)
        assert process.returncode == 0
        assert process.stdout.strip() == ""

    def test_hook_ignores_non_python_files(self):
        """Test that hook ignores non-Python/Markdown files."""
        input_data = {
            "tool_name": "Write",
            "tool_input": {
                "file_path": "test.txt",
                "content": "Hello World! 🚀 ✅ ❌"
            }
        }
        
        # Run the hook as a subprocess
        process = subprocess.run(
            [sys.executable, str(EMOJI_HOOK_PATH)],
            input=json.dumps(input_data),
            text=True,
            capture_output=True
        )
        
        # Should exit with code 0 (allowed) since it's a .txt file
        assert process.returncode == 0
        assert process.stdout.strip() == ""

    def test_hook_ignores_non_write_operations(self):
        """Test that hook ignores operations other than Write/Edit/MultiEdit."""
        input_data = {
            "tool_name": "Read",
            "tool_input": {
                "file_path": "test.py"
            }
        }
        
        # Run the hook as a subprocess
        process = subprocess.run(
            [sys.executable, str(EMOJI_HOOK_PATH)],
            input=json.dumps(input_data),
            text=True,
            capture_output=True
        )
        
        # Should exit with code 0 (allowed)
        assert process.returncode == 0
        assert process.stdout.strip() == ""

    def test_hook_handles_edit_operations(self):
        """Test hook handling of Edit operations."""
        input_data = {
            "tool_name": "Edit",
            "tool_input": {
                "file_path": "test.py",
                "old_string": "old_code",
                "new_string": "print('New code! 🚀')"
            }
        }
        
        # Run the hook as a subprocess
        process = subprocess.run(
            [sys.executable, str(EMOJI_HOOK_PATH)],
            input=json.dumps(input_data),
            text=True,
            capture_output=True
        )
        
        # Should exit with code 0 but block the operation
        assert process.returncode == 0
        
        # Parse the JSON output
        output = json.loads(process.stdout)
        assert output["hookSpecificOutput"]["permissionDecision"] == "deny"

    def test_hook_handles_multiedit_operations(self):
        """Test hook handling of MultiEdit operations."""
        input_data = {
            "tool_name": "MultiEdit",
            "tool_input": {
                "file_path": "test.py",
                "edits": [
                    {"old_string": "old1", "new_string": "Clean code"},
                    {"old_string": "old2", "new_string": "Code with emoji 🚀"}
                ]
            }
        }
        
        # Run the hook as a subprocess
        process = subprocess.run(
            [sys.executable, str(EMOJI_HOOK_PATH)],
            input=json.dumps(input_data),
            text=True,
            capture_output=True
        )
        
        # Should exit with code 0 but block the operation
        assert process.returncode == 0
        
        # Parse the JSON output
        output = json.loads(process.stdout)
        assert output["hookSpecificOutput"]["permissionDecision"] == "deny"

    def test_hook_handles_invalid_json(self):
        """Test hook handling of invalid JSON input."""
        # Run the hook with invalid JSON
        process = subprocess.run(
            [sys.executable, str(EMOJI_HOOK_PATH)],
            input="invalid json",
            text=True,
            capture_output=True
        )
        
        # Should exit with code 1 (error)
        assert process.returncode == 1
        assert "Invalid JSON input" in process.stderr

    def test_hook_markdown_files(self):
        """Test hook works with Markdown files."""
        input_data = {
            "tool_name": "Write",
            "tool_input": {
                "file_path": "README.md",
                "content": "# Project Title\n\nThis is awesome! 🚀"
            }
        }
        
        # Run the hook as a subprocess
        process = subprocess.run(
            [sys.executable, str(EMOJI_HOOK_PATH)],
            input=json.dumps(input_data),
            text=True,
            capture_output=True
        )
        
        # Should block the operation
        assert process.returncode == 0
        
        # Parse the JSON output
        output = json.loads(process.stdout)
        assert output["hookSpecificOutput"]["permissionDecision"] == "deny"
        assert "Markdown" in output["hookSpecificOutput"]["permissionDecisionReason"]