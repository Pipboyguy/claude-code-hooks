# Claude Code Hooks

This directory contains Claude Code hooks that enhance your development workflow by enforcing coding standards and best practices.

## Structure

```
hooks/
├── __init__.py                 # Package initialization
├── claude_code_hooks/          # Main hooks module
│   ├── __init__.py            # Module exports
│   └── emoji_checker.py       # EmojiChecker hook implementation
├── check-no-emojis.py         # Hook entry point (executable)
└── README.md                  # This documentation
```

## Available Hooks

### EmojiChecker (`check-no-emojis.py`)

Prevents colorful emojis from being written to Python and Markdown files while allowing monochrome Unicode symbols.

**Allowed symbols:**
- ✓ (checkmark)
- × (cross)
- → (arrow) 
- • (bullet)
- – (en dash)
- — (em dash)

**Blocked emojis:**
- 🚀 (rocket)
- ✅ (green checkmark)
- ❌ (red X)
- ⭐ (star)
- And other colorful emojis

**Usage:**
```bash
# As a Claude Code hook (automatically called)
./hooks/check-no-emojis.py

# As a Python module  
python -m claude_code_hooks.emoji_checker
```

## Testing

The hooks come with comprehensive test coverage:

- **Unit tests**: Test individual hook components
- **Integration tests**: Test hooks as complete modules
- **E2E tests**: Test real-world scenarios

### Running Tests

```bash
# Install test dependencies
uv add --group test pytest pytest-cov

# Run all tests
python -m pytest

# Run specific test types
python -m pytest tests/unit/        # Unit tests only
python -m pytest tests/integration/ # Integration tests only  
python -m pytest tests/e2e/        # E2E tests only

# Run with coverage
python -m pytest --cov=hooks --cov-report=html

# Use the test runner script
python run_tests.py all            # All tests
python run_tests.py coverage       # All tests with coverage
python run_tests.py unit          # Unit tests only
```

## Development

### Adding New Hooks

1. Create your hook class in `claude_code_hooks/your_hook.py`
2. Add the class to `claude_code_hooks/__init__.py`
3. Create an executable script in the hooks/ directory
4. Add comprehensive tests in the appropriate test directories
5. Update this documentation

### Hook Structure

Each hook should follow this pattern:

```python
class YourHook:
    """Description of what the hook does."""
    
    @classmethod
    def process_hook_request(cls, input_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Process a hook request.
        
        Returns None if operation should be allowed, or a dict with hook output
        if the operation should be blocked.
        """
        # Your hook logic here
        pass

def main():
    """Main function for command-line usage."""
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)
    
    result = YourHook.process_hook_request(input_data)
    
    if result:
        print(json.dumps(result))
        sys.exit(0)
    
    sys.exit(0)

if __name__ == "__main__":
    main()
```

## Configuration

The hooks follow uv best practices:

- Python >=3.13 required
- Type hints throughout
- Comprehensive error handling
- Modular, testable design
- Clear separation of concerns

## Contributing

1. Ensure all tests pass: `python run_tests.py all`
2. Add tests for new functionality
3. Follow the existing code style
4. Update documentation as needed