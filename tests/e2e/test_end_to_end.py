"""
End-to-end tests for Claude Code Hooks.

These tests simulate real-world usage scenarios and verify that the entire
hook system works as expected in a production-like environment.
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path
import pytest

# Path to the hooks
HOOKS_DIR = Path(__file__).parent.parent.parent / "hooks"
EMOJI_HOOK_PATH = HOOKS_DIR / "check-no-emojis.py"


class TestEmojiHookE2E:
    """End-to-end tests for emoji checker hook in real scenarios."""

    def test_real_python_code_with_emojis(self):
        """Test with realistic Python code containing emojis."""
        python_code = '''#!/usr/bin/env python3
"""
A sample Python application with emojis that should be blocked.
"""

def main():
    print("Starting application... 🚀")
    
    # Process data
    data = process_data()
    
    if data:
        print("Success! ✅")
        return True
    else:
        print("Failed! ❌") 
        return False

def process_data():
    """Process some data."""
    # Simulate processing
    return {"status": "complete", "emoji": "🎉"}

if __name__ == "__main__":
    main()
'''
        
        input_data = {
            "tool_name": "Write",
            "tool_input": {
                "file_path": "app.py",
                "content": python_code
            }
        }
        
        # Run the hook
        process = subprocess.run(
            [sys.executable, str(EMOJI_HOOK_PATH)],
            input=json.dumps(input_data),
            text=True,
            capture_output=True
        )
        
        assert process.returncode == 0
        output = json.loads(process.stdout)
        assert output["hookSpecificOutput"]["permissionDecision"] == "deny"
        
        # Should mention specific emojis found
        reason = output["hookSpecificOutput"]["permissionDecisionReason"]
        assert any(emoji in reason for emoji in ["🚀", "✅", "❌", "🎉"])

    def test_clean_python_code(self):
        """Test with clean Python code that should be allowed."""
        python_code = '''#!/usr/bin/env python3
"""
A sample Python application without emojis.
"""

import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main application entry point."""
    logger.info("Starting application...")
    
    # Process data
    data = process_data()
    
    if data:
        logger.info("Processing completed successfully")
        print("Status: Complete")
        return True
    else:
        logger.error("Processing failed")  
        print("Status: Failed")
        return False

def process_data():
    """Process some data and return results."""
    try:
        # Simulate data processing
        result = {"status": "complete", "count": 42}
        logger.debug(f"Processed data: {result}")
        return result
    except Exception as e:
        logger.error(f"Error processing data: {e}")
        return None

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
'''
        
        input_data = {
            "tool_name": "Write",
            "tool_input": {
                "file_path": "app.py",
                "content": python_code
            }
        }
        
        # Run the hook
        process = subprocess.run(
            [sys.executable, str(EMOJI_HOOK_PATH)],
            input=json.dumps(input_data),
            text=True,
            capture_output=True
        )
        
        # Should be allowed
        assert process.returncode == 0
        assert process.stdout.strip() == ""

    def test_markdown_documentation_with_emojis(self):
        """Test with Markdown documentation containing emojis."""
        markdown_content = '''# My Awesome Project 🚀

Welcome to our project! This is a comprehensive guide.

## Features ✨

- Fast performance 
- Easy to use ✅
- Well documented 📚
- Active community 👥

## Installation

```bash
pip install my-project
```

## Quick Start 🏁

1. Import the library
2. Configure your settings  
3. Run your first command 🎉

## Support ❤️

If you need help, please:

- Check the docs 📖
- Open an issue 🐛
- Join our Discord 💬

Happy coding! 😄
'''
        
        input_data = {
            "tool_name": "Write",
            "tool_input": {
                "file_path": "README.md",
                "content": markdown_content
            }
        }
        
        # Run the hook
        process = subprocess.run(
            [sys.executable, str(EMOJI_HOOK_PATH)],
            input=json.dumps(input_data),
            text=True,
            capture_output=True
        )
        
        assert process.returncode == 0
        output = json.loads(process.stdout)
        assert output["hookSpecificOutput"]["permissionDecision"] == "deny"
        assert "Markdown" in output["hookSpecificOutput"]["permissionDecisionReason"]

    def test_professional_markdown_without_emojis(self):
        """Test professional Markdown that should be allowed."""
        markdown_content = '''# My Professional Project

Welcome to our project documentation.

## Features

- High performance architecture
- Comprehensive API coverage  
- Extensive test coverage
- Professional documentation standards

## Installation

```bash
pip install my-project
```

## Quick Start

1. Import the library:
   ```python
   import my_project
   ```

2. Configure your settings:
   ```python
   config = my_project.Config(
       api_key="your-key",
       debug=False
   )
   ```

3. Initialize the client:
   ```python
   client = my_project.Client(config)
   ```

## API Reference

### Client Methods

- `client.connect()` - Establish connection
- `client.query(sql)` - Execute query  
- `client.close()` - Close connection

## Contributing

Please read our contributing guidelines before submitting pull requests.

### Development Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements-dev.txt`
3. Run tests: `pytest`
4. Submit your changes

## License

This project is licensed under the MIT License.
'''
        
        input_data = {
            "tool_name": "Write",
            "tool_input": {
                "file_path": "README.md", 
                "content": markdown_content
            }
        }
        
        # Run the hook
        process = subprocess.run(
            [sys.executable, str(EMOJI_HOOK_PATH)],
            input=json.dumps(input_data),
            text=True,
            capture_output=True
        )
        
        # Should be allowed
        assert process.returncode == 0
        assert process.stdout.strip() == ""

    def test_complex_multiedit_scenario(self):
        """Test complex MultiEdit scenario with mixed content."""
        input_data = {
            "tool_name": "MultiEdit",
            "tool_input": {
                "file_path": "complex_app.py",
                "edits": [
                    {
                        "old_string": "# TODO: Add logging",
                        "new_string": "import logging\nlogger = logging.getLogger(__name__)"
                    },
                    {
                        "old_string": "print('Starting...')",
                        "new_string": "logger.info('Starting application')"
                    },
                    {
                        "old_string": "print('Done!')",
                        "new_string": "print('Process completed successfully! 🎉')"  # This should trigger block
                    },
                    {
                        "old_string": "return result",
                        "new_string": "logger.debug(f'Returning: {result}')\nreturn result"
                    }
                ]
            }
        }
        
        # Run the hook
        process = subprocess.run(
            [sys.executable, str(EMOJI_HOOK_PATH)],
            input=json.dumps(input_data),
            text=True,
            capture_output=True
        )
        
        assert process.returncode == 0
        output = json.loads(process.stdout)
        assert output["hookSpecificOutput"]["permissionDecision"] == "deny"
        assert "🎉" in output["hookSpecificOutput"]["permissionDecisionReason"]

    def test_edge_case_empty_content(self):
        """Test edge case with empty content."""
        input_data = {
            "tool_name": "Write",
            "tool_input": {
                "file_path": "empty.py",
                "content": ""
            }
        }
        
        # Run the hook
        process = subprocess.run(
            [sys.executable, str(EMOJI_HOOK_PATH)],
            input=json.dumps(input_data),
            text=True,
            capture_output=True
        )
        
        # Should be allowed
        assert process.returncode == 0
        assert process.stdout.strip() == ""

    def test_edge_case_whitespace_only(self):
        """Test edge case with whitespace-only content."""
        input_data = {
            "tool_name": "Write",
            "tool_input": {
                "file_path": "whitespace.py",
                "content": "   \n\n  \t  \n   "
            }
        }
        
        # Run the hook
        process = subprocess.run(
            [sys.executable, str(EMOJI_HOOK_PATH)],
            input=json.dumps(input_data),
            text=True,
            capture_output=True
        )
        
        # Should be allowed
        assert process.returncode == 0
        assert process.stdout.strip() == ""

    def test_mixed_symbols_scenario(self):
        """Test scenario with both allowed and forbidden symbols."""
        content = '''# Status Report

## Completed Tasks
✓ Setup development environment
✓ Implement core functionality  
✓ Add unit tests

## In Progress
→ Code review
→ Documentation updates

## Issues
• Performance optimization needed
• Memory usage concerns

## Celebration
Great work team! 🎉 We're almost done! 🚀
'''
        
        input_data = {
            "tool_name": "Write",
            "tool_input": {
                "file_path": "status.md",
                "content": content
            }
        }
        
        # Run the hook
        process = subprocess.run(
            [sys.executable, str(EMOJI_HOOK_PATH)],
            input=json.dumps(input_data),
            text=True,
            capture_output=True
        )
        
        # Should be blocked due to colorful emojis, even though it has allowed symbols
        assert process.returncode == 0
        output = json.loads(process.stdout)
        assert output["hookSpecificOutput"]["permissionDecision"] == "deny"
        
        # Should mention the problematic emojis but not the allowed symbols
        reason = output["hookSpecificOutput"]["permissionDecisionReason"]
        assert any(emoji in reason for emoji in ["🎉", "🚀"])
        # The allowed symbols should not be mentioned as problems
        assert "✓" not in reason or "allowed" in reason.lower()