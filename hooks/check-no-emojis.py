#!/usr/bin/env python3

"""
Wrapper script for the EmojiChecker hook.

This maintains backward compatibility while using the new namespaced module structure.
"""

import sys
from pathlib import Path

# Add the hooks directory to the Python path
hooks_dir = Path(__file__).parent
sys.path.insert(0, str(hooks_dir))

from claude_code_hooks.emoji_checker import main

if __name__ == "__main__":
    main()