"""
Unit tests for EmojiChecker hook.
"""

import pytest
from claude_code_hooks.emoji_checker import EmojiChecker


class TestEmojiDetection:
    """Test emoji detection functionality."""

    def test_has_emojis_with_colorful_emojis(self):
        """Test detection of colorful emojis."""
        test_cases = [
            "Hello 🚀",
            "Test ✅",
            "Error ❌",
            "Star ⭐",
            "Heart ❤️",
            "Sparkles ✨",
        ]
        
        for text in test_cases:
            assert EmojiChecker.has_emojis(text), f"Should detect emoji in: {text}"

    def test_has_emojis_with_allowed_symbols(self):
        """Test that monochrome symbols are allowed."""
        test_cases = [
            "Check ✓",
            "Cross ×",
            "Arrow →",
            "Bullet •",
            "Dash –",
            "Em dash —",
        ]
        
        for text in test_cases:
            assert not EmojiChecker.has_emojis(text), f"Should allow symbol in: {text}"

    def test_has_emojis_with_empty_string(self):
        """Test with empty string."""
        assert not EmojiChecker.has_emojis("")

    def test_has_emojis_with_none(self):
        """Test with None input."""
        assert not EmojiChecker.has_emojis(None)

    def test_has_emojis_with_plain_text(self):
        """Test with plain text."""
        assert not EmojiChecker.has_emojis("Hello World")

    def test_get_emoji_examples(self):
        """Test emoji examples extraction."""
        text = "Hello 🚀 world ✅ test ❌"
        examples = EmojiChecker.get_emoji_examples(text, max_examples=2)
        assert len(examples) == 2
        assert "🚀" in examples
        assert "✅" in examples

    def test_get_emoji_examples_empty(self):
        """Test emoji examples with no emojis."""
        examples = EmojiChecker.get_emoji_examples("Hello World")
        assert examples == []

    def test_get_emoji_examples_max_limit(self):
        """Test emoji examples respects max limit."""
        text = "🚀✅❌⭐❤️✨"
        examples = EmojiChecker.get_emoji_examples(text, max_examples=3)
        assert len(examples) == 3


class TestFileMonitoring:
    """Test file monitoring functionality."""

    def test_is_monitored_file_python(self):
        """Test Python file monitoring."""
        assert EmojiChecker.is_monitored_file("test.py")
        assert EmojiChecker.is_monitored_file("/path/to/file.py")

    def test_is_monitored_file_markdown(self):
        """Test Markdown file monitoring."""
        assert EmojiChecker.is_monitored_file("README.md")
        assert EmojiChecker.is_monitored_file("docs/guide.md")
        assert EmojiChecker.is_monitored_file("file.mdx")

    def test_is_monitored_file_other(self):
        """Test other file types are not monitored."""
        assert not EmojiChecker.is_monitored_file("file.txt")
        assert not EmojiChecker.is_monitored_file("script.js")
        assert not EmojiChecker.is_monitored_file("style.css")

    def test_is_monitored_file_empty(self):
        """Test with empty file path."""
        assert not EmojiChecker.is_monitored_file("")
        assert not EmojiChecker.is_monitored_file(None)

    def test_is_monitored_file_case_insensitive(self):
        """Test file extension case insensitivity."""
        assert EmojiChecker.is_monitored_file("file.PY")
        assert EmojiChecker.is_monitored_file("file.MD")
        assert EmojiChecker.is_monitored_file("file.MDX")


class TestContentExtraction:
    """Test content extraction from tool inputs."""

    def test_extract_content_write(self):
        """Test content extraction from Write tool."""
        tool_input = {"content": "Hello World"}
        content = EmojiChecker.extract_content_from_tool_input("Write", tool_input)
        assert content == "Hello World"

    def test_extract_content_edit(self):
        """Test content extraction from Edit tool."""
        tool_input = {"new_string": "Updated code"}
        content = EmojiChecker.extract_content_from_tool_input("Edit", tool_input)
        assert content == "Updated code"

    def test_extract_content_multiedit(self):
        """Test content extraction from MultiEdit tool."""
        tool_input = {
            "edits": [
                {"new_string": "First edit"},
                {"new_string": "Second edit"},
                {"new_string": "Third edit"}
            ]
        }
        content = EmojiChecker.extract_content_from_tool_input("MultiEdit", tool_input)
        assert content == "First edit Second edit Third edit"

    def test_extract_content_multiedit_empty_edits(self):
        """Test MultiEdit with empty edits."""
        tool_input = {"edits": []}
        content = EmojiChecker.extract_content_from_tool_input("MultiEdit", tool_input)
        assert content == ""

    def test_extract_content_multiedit_some_empty(self):
        """Test MultiEdit with some empty new_strings."""
        tool_input = {
            "edits": [
                {"new_string": "First edit"},
                {"new_string": ""},
                {"new_string": "Third edit"}
            ]
        }
        content = EmojiChecker.extract_content_from_tool_input("MultiEdit", tool_input)
        assert content == "First edit Third edit"

    def test_extract_content_unknown_tool(self):
        """Test content extraction from unknown tool."""
        content = EmojiChecker.extract_content_from_tool_input("UnknownTool", {})
        assert content == ""

    def test_extract_content_missing_keys(self):
        """Test content extraction with missing keys."""
        assert EmojiChecker.extract_content_from_tool_input("Write", {}) == ""
        assert EmojiChecker.extract_content_from_tool_input("Edit", {}) == ""
        assert EmojiChecker.extract_content_from_tool_input("MultiEdit", {}) == ""


class TestHookProcessing:
    """Test complete hook processing."""

    def test_process_hook_request_allowed(self):
        """Test hook request that should be allowed."""
        input_data = {
            "tool_name": "Write",
            "tool_input": {
                "file_path": "test.py",
                "content": "print('Hello World')"
            }
        }
        result = EmojiChecker.process_hook_request(input_data)
        assert result is None

    def test_process_hook_request_blocked(self):
        """Test hook request that should be blocked."""
        input_data = {
            "tool_name": "Write",
            "tool_input": {
                "file_path": "test.py",
                "content": "print('Hello World! 🚀')"
            }
        }
        result = EmojiChecker.process_hook_request(input_data)
        assert result is not None
        assert result["hookSpecificOutput"]["permissionDecision"] == "deny"
        assert "🚀" in result["hookSpecificOutput"]["permissionDecisionReason"]

    def test_process_hook_request_unmonitored_tool(self):
        """Test hook request with unmonitored tool."""
        input_data = {
            "tool_name": "Read",
            "tool_input": {
                "file_path": "test.py",
                "content": "print('Hello World! 🚀')"
            }
        }
        result = EmojiChecker.process_hook_request(input_data)
        assert result is None

    def test_process_hook_request_unmonitored_file(self):
        """Test hook request with unmonitored file type."""
        input_data = {
            "tool_name": "Write",
            "tool_input": {
                "file_path": "test.txt",
                "content": "Hello World! 🚀"
            }
        }
        result = EmojiChecker.process_hook_request(input_data)
        assert result is None

    def test_process_hook_request_edit_with_emoji(self):
        """Test Edit operation with emoji."""
        input_data = {
            "tool_name": "Edit",
            "tool_input": {
                "file_path": "test.py",
                "new_string": "Updated code 🚀"
            }
        }
        result = EmojiChecker.process_hook_request(input_data)
        assert result is not None
        assert result["hookSpecificOutput"]["permissionDecision"] == "deny"

    def test_process_hook_request_multiedit_with_emoji(self):
        """Test MultiEdit operation with emoji."""
        input_data = {
            "tool_name": "MultiEdit", 
            "tool_input": {
                "file_path": "test.py",
                "edits": [
                    {"new_string": "Clean code"},
                    {"new_string": "Code with emoji 🚀"}
                ]
            }
        }
        result = EmojiChecker.process_hook_request(input_data)
        assert result is not None
        assert result["hookSpecificOutput"]["permissionDecision"] == "deny"