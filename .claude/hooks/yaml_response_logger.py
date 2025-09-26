#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pyyaml",
# ]
# ///

"""
YAML Response Logger for PostToolUse Hook
==========================================
Captures YAML-formatted content from tool outputs and builds a knowledge base.
Integrated with PostToolUse hook to capture responses in real-time.
"""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import hashlib

try:
    import yaml
except ImportError:
    yaml = None

def extract_yaml_from_content(content: str) -> List[Dict[str, Any]]:
    """
    Extract YAML blocks from any text content.
    """
    if not yaml or not content:
        return []

    yaml_blocks = []

    # Find YAML code blocks
    yaml_pattern = r'```yaml\n(.*?)\n```'
    matches = re.findall(yaml_pattern, content, re.DOTALL)

    for match in matches:
        try:
            parsed = yaml.safe_load(match)
            if parsed and isinstance(parsed, dict):
                yaml_blocks.append(parsed)
        except:
            continue

    return yaml_blocks

def process_tool_output(input_data: Dict[str, Any]):
    """
    Process PostToolUse hook data to extract and save YAML responses.
    """
    # Get tool name and output
    tool_name = input_data.get('tool', '')
    tool_output = input_data.get('output', '')

    # Skip if no output
    if not tool_output:
        return

    # Convert output to string if needed
    if isinstance(tool_output, dict):
        tool_output = json.dumps(tool_output, indent=2)
    elif not isinstance(tool_output, str):
        tool_output = str(tool_output)

    # Extract YAML blocks
    yaml_blocks = extract_yaml_from_content(tool_output)

    if not yaml_blocks:
        return

    # Setup storage
    notes_dir = Path.cwd() / 'notes' / 'knowledge' / '.realtime'
    notes_dir.mkdir(parents=True, exist_ok=True)

    # Save each YAML block
    for yaml_content in yaml_blocks:
        if not yaml_content or not isinstance(yaml_content, dict):
            continue

        # Create note entry
        note = {
            'timestamp': datetime.now().isoformat(),
            'tool': tool_name,
            'content': yaml_content,
            'categories': categorize_content(yaml_content, tool_name)
        }

        # Save to daily file using consistent local timezone
        daily_file = notes_dir / f"{datetime.now().strftime('%Y-%m-%d')}.jsonl"
        with open(daily_file, 'a') as f:
            f.write(json.dumps(note) + '\n')

def categorize_content(yaml_content: Dict[str, Any], tool_name: str) -> List[str]:
    """
    Quick categorization based on content.
    """
    categories = []

    # Check task field
    task = str(yaml_content.get('task', '')).lower()

    if 'git' in task or 'commit' in task:
        categories.append('git')
    if 'file' in task or 'edit' in task:
        categories.append('files')
    if 'test' in task or 'debug' in task:
        categories.append('debugging')

    # Add tool category
    if 'bash' in tool_name.lower():
        categories.append('bash')
    elif 'write' in tool_name.lower() or 'edit' in tool_name.lower():
        categories.append('code_changes')

    # Status
    status = yaml_content.get('status', '').lower()
    if 'success' in status:
        categories.append('success')
    elif 'fail' in status or 'error' in status:
        categories.append('error')

    return categories if categories else ['general']

def main():
    try:
        # Read from stdin
        input_data = json.load(sys.stdin)

        # Process the tool output
        process_tool_output(input_data)

        # Also log to standard post_tool_use.json
        log_dir = Path.cwd() / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / 'post_tool_use.json'

        # Read existing log data
        if log_path.exists():
            with open(log_path, 'r') as f:
                try:
                    log_data = json.load(f)
                except (json.JSONDecodeError, ValueError):
                    log_data = []
        else:
            log_data = []

        # Append new data
        log_data.append(input_data)

        # Write back
        with open(log_path, 'w') as f:
            json.dump(log_data, f, indent=2)

        sys.exit(0)

    except:
        # Always exit cleanly
        sys.exit(0)

if __name__ == '__main__':
    main()