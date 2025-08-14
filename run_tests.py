#!/usr/bin/env python3
"""
Test runner script for Claude Code Hooks.

This script provides different testing modes:
- Unit tests only
- Integration tests only  
- E2E tests only
- All tests
- Coverage reports
"""

import sys
import subprocess
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print('='*60)
    
    try:
        result = subprocess.run(cmd, check=True, text=True, capture_output=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Command failed with exit code {e.returncode}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False
    except FileNotFoundError:
        print(f"ERROR: Command not found: {cmd[0]}")
        print("Make sure pytest is installed: uv add --group test pytest pytest-cov")
        return False

def main():
    """Main test runner."""
    if len(sys.argv) < 2:
        print("Usage: python run_tests.py <mode>")
        print("Modes: unit, integration, e2e, all, coverage")
        sys.exit(1)
    
    mode = sys.argv[1].lower()
    project_root = Path(__file__).parent
    
    # Base pytest command
    base_cmd = [sys.executable, "-m", "pytest"]
    
    if mode == "unit":
        cmd = base_cmd + ["tests/unit/", "-v", "-m", "unit"]
        success = run_command(cmd, "Unit Tests")
        
    elif mode == "integration":  
        cmd = base_cmd + ["tests/integration/", "-v", "-m", "integration"]
        success = run_command(cmd, "Integration Tests")
        
    elif mode == "e2e":
        cmd = base_cmd + ["tests/e2e/", "-v", "-m", "e2e"]
        success = run_command(cmd, "E2E Tests")
        
    elif mode == "all":
        success = True
        
        # Run unit tests
        cmd = base_cmd + ["tests/unit/", "-v"]
        success &= run_command(cmd, "Unit Tests")
        
        # Run integration tests  
        cmd = base_cmd + ["tests/integration/", "-v"]
        success &= run_command(cmd, "Integration Tests")
        
        # Run E2E tests
        cmd = base_cmd + ["tests/e2e/", "-v"] 
        success &= run_command(cmd, "E2E Tests")
        
    elif mode == "coverage":
        cmd = base_cmd + ["--cov=hooks", "--cov-report=term-missing", "--cov-report=html", "-v"]
        success = run_command(cmd, "All Tests with Coverage")
        
        if success:
            print(f"\nCoverage HTML report generated at: {project_root}/htmlcov/index.html")
    
    else:
        print(f"Unknown mode: {mode}")
        print("Available modes: unit, integration, e2e, all, coverage")
        sys.exit(1)
    
    if success:
        print(f"\n✅ {mode.title()} tests completed successfully!")
        sys.exit(0)
    else:
        print(f"\n❌ {mode.title()} tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()