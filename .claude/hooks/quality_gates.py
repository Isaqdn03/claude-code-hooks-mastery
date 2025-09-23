#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["python-dotenv"]
# ///

import json
import sys
import subprocess
from pathlib import Path

def run_tests():
    """Run project tests and return success status."""
    # Detect test framework
    if Path('package.json').exists():
        # Node.js project - check if test script exists
        try:
            with open('package.json', 'r') as f:
                package_data = json.load(f)
                if 'test' in package_data.get('scripts', {}):
                    result = subprocess.run(['npm', 'test'], capture_output=True)
                    return result.returncode == 0, "npm test"
        except:
            pass
    elif Path('requirements.txt').exists() or Path('pyproject.toml').exists():
        # Python project
        if Path('tests').exists() or Path('test').exists():
            result = subprocess.run(['python', '-m', 'pytest', '--tb=short', '-q'], capture_output=True)
            return result.returncode == 0, "pytest"

    return True, "no tests detected"  # No tests detected, allow completion

def check_build():
    """Verify project builds successfully."""
    if Path('package.json').exists():
        try:
            with open('package.json', 'r') as f:
                package_data = json.load(f)
                if 'build' in package_data.get('scripts', {}):
                    result = subprocess.run(['npm', 'run', 'build'], capture_output=True)
                    return result.returncode == 0, "npm run build"
        except:
            pass
    elif Path('Cargo.toml').exists():
        result = subprocess.run(['cargo', 'check'], capture_output=True)
        return result.returncode == 0, "cargo check"

    return True, "no build script detected"

def main():
    try:
        # Read JSON input from stdin
        input_data = json.load(sys.stdin)

        # Only run quality gates if this is a natural stop (not forced)
        if not input_data.get('stop_hook_active', False):

            # Run quality checks
            tests_pass, test_command = run_tests()
            build_passes, build_command = check_build()

            if not tests_pass:
                result = {
                    "decision": "block",
                    "reason": f"Tests are failing ({test_command}). Please fix failing tests before completing."
                }
                print(json.dumps(result))
                sys.exit(0)

            if not build_passes:
                result = {
                    "decision": "block",
                    "reason": f"Build is failing ({build_command}). Please fix build errors before completing."
                }
                print(json.dumps(result))
                sys.exit(0)

        # If all checks pass, allow completion
        print("✅ All quality gates passed!")

    except Exception as e:
        # Don't block on hook errors, just log them
        print(f"Quality gate check error: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()