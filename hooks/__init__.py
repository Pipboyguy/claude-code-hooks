"""
Claude Code Hooks Package

This package contains Claude Code hooks for enhancing development workflows.
Each hook is designed to be modular and testable.
"""

__version__ = "0.1.0"
__author__ = "Claude Code Hooks Contributors"

from pathlib import Path

HOOKS_DIR = Path(__file__).parent
PROJECT_ROOT = HOOKS_DIR.parent

__all__ = ["HOOKS_DIR", "PROJECT_ROOT"]