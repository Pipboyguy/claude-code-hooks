#!/usr/bin/env python3

"""

Claude Code hook to prevent colorful emojis from being written to Python and Markdown files.

Intercepts Write, Edit, and MultiEdit operations and blocks them if colorful emojis are detected.

Allows monochrome Unicode symbols like ✓ × → • but blocks colorful emojis like 🚀 ✅ 😀.

"""

import json
import re
import sys
from pathlib import Path


def has_emojis(text: str) -> bool:
    """Check if text contains colorful emoji characters (allows monochrome symbols)."""

    if not text:
        return False

    # Check for specific colorful symbols first

    colorful_symbols = {
        "\u2705",  # ✅ green checkmark
        "\u274c",  # ❌ red X
        "\u2b50",  # ⭐ star
        "\u2764",  # ❤️ red heart
        "\u2728",  # ✨ sparkles
        "\u2733",  # ✳️ eight-spoked asterisk
        "\u2734",  # ✴️ eight-pointed star
        "\u2747",  # ❇️ sparkle
        "\u2757",  # ❗ exclamation mark
        "\u2753",  # ❓ question mark
        "\u2755",  # ❕ white exclamation mark
        "\u2795",  # ➕ plus sign
        "\u2796",  # ➖ minus sign
        "\u2797",  # ➗ division sign
    }

    for char in text:
        if char in colorful_symbols:
            return True

    # Check for colorful emoji ranges (definitely colorful emojis)

    colorful_emoji_pattern = re.compile(
        "["
        "\U0001f600-\U0001f64f"  # emoticons (😀😃😄😊😢😭)
        "\U0001f680-\U0001f6ff"  # transport & map symbols (🚀🚂🚗✈️🏠)
        "\U0001f300-\U0001f5ff"  # miscellaneous symbols (🌟🎉📱💻🎈)
        "\U0001f900-\U0001f9ff"  # supplemental symbols (🤔🦄🧠🤖)
        "\U0001f1e0-\U0001f1ff"  # regional indicators/flags (🇺🇸🇬🇧)
        "]+",
        flags=re.UNICODE,
    )

    return bool(colorful_emoji_pattern.search(text))


def get_emoji_examples(text: str, max_examples: int = 3) -> list[str]:
    """Extract colorful emoji examples from text for error reporting."""

    emojis = []

    # Check for specific colorful symbols first

    colorful_symbols = {
        "\u2705",  # ✅ green checkmark
        "\u274c",  # ❌ red X
        "\u2b50",  # ⭐ star
        "\u2764",  # ❤️ red heart
        "\u2728",  # ✨ sparkles
        "\u2733",  # ✳️ eight-spoked asterisk
        "\u2734",  # ✴️ eight-pointed star
        "\u2747",  # ❇️ sparkle
        "\u2757",  # ❗ exclamation mark
        "\u2753",  # ❓ question mark
        "\u2755",  # ❕ white exclamation mark
        "\u2795",  # ➕ plus sign
        "\u2796",  # ➖ minus sign
        "\u2797",  # ➗ division sign
    }

    for char in text:
        if char in colorful_symbols and char not in emojis:
            emojis.append(char)

            if len(emojis) >= max_examples:
                return emojis

    # Check for colorful emoji ranges

    if len(emojis) < max_examples:
        colorful_emoji_pattern = re.compile(
            "["
            "\U0001f600-\U0001f64f"  # emoticons (😀😃😄😊😢😭)
            "\U0001f680-\U0001f6ff"  # transport & map symbols (🚀🚂🚗✈️🏠)
            "\U0001f300-\U0001f5ff"  # miscellaneous symbols (🌟🎉📱💻🎈)
            "\U0001f900-\U0001f9ff"  # supplemental symbols (🤔🦄🧠🤖)
            "\U0001f1e0-\U0001f1ff"  # regional indicators/flags (🇺🇸🇬🇧)
            "]+",
            flags=re.UNICODE,
        )

        for match in colorful_emoji_pattern.finditer(text):
            for char in match.group():
                if char not in emojis:
                    emojis.append(char)

                    if len(emojis) >= max_examples:
                        break

            if len(emojis) >= max_examples:
                break

    return emojis


def is_python_or_markdown_file(file_path: str) -> bool:
    """Check if the file is a Python or Markdown file."""

    if not file_path:
        return False

    path = Path(file_path)

    return path.suffix.lower() in [".py", ".md", ".mdx"]


def extract_content_from_tool_input(tool_name: str, tool_input: dict) -> str:
    """Extract content to check from different tool types."""

    content = ""

    if tool_name == "Write":
        content = tool_input.get("content", "")

    elif tool_name == "Edit":
        content = tool_input.get("new_string", "")

    elif tool_name == "MultiEdit":
        # Check all edits

        edits = tool_input.get("edits", [])

        content_parts = []

        for edit in edits:
            new_string = edit.get("new_string", "")

            if new_string:
                content_parts.append(new_string)

        content = " ".join(content_parts)

    return content


def main():
    """Main hook function."""

    try:
        input_data = json.load(sys.stdin)

    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)

        sys.exit(1)

    tool_name = input_data.get("tool_name", "")

    tool_input = input_data.get("tool_input", {})

    # Only check Write/Edit/MultiEdit operations

    if tool_name not in ["Write", "Edit", "MultiEdit"]:
        sys.exit(0)

    # Get file path

    file_path = tool_input.get("file_path", "")

    # Check if it's a Python or Markdown file

    if not is_python_or_markdown_file(file_path):
        sys.exit(0)

    # Extract content to check

    content = extract_content_from_tool_input(tool_name, tool_input)

    # Check for emojis

    if has_emojis(content):
        emoji_examples = get_emoji_examples(content)

        examples_str = " ".join(emoji_examples) if emoji_examples else "detected"

        file_type = "Python" if file_path.endswith(".py") else "Markdown"

        # Use JSON output for better control

        output = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": f"❌ Colorful emojis detected in {file_type} file '{file_path}': {examples_str}\n\nPython and Markdown files should not contain colorful emojis for professional code standards. Simple symbols like ✓ × → • are allowed. Please remove the colorful emojis and try again.",
            }
        }

        print(json.dumps(output))

        sys.exit(0)

    # Allow the operation if no emojis found

    sys.exit(0)


if __name__ == "__main__":
    main()
