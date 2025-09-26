#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pyyaml",
#     "python-dotenv",
# ]
# ///

"""
YAML Response Logging Hook
===========================
Captures and intelligently organizes YAML-formatted responses from Claude,
building a searchable knowledge base of interactions and solutions.

Features:
- Automatic extraction of YAML content from responses
- Metadata enrichment with session, timestamp, and context
- Intelligent categorization based on task types
- Multiple storage formats (Markdown, JSON)
- Knowledge graph building for pattern discovery
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
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    yaml = None
    pass

def extract_yaml_blocks(content: str) -> List[Dict[str, Any]]:
    """
    Extract YAML blocks from response content.

    Returns:
        List of parsed YAML dictionaries
    """
    if not yaml:
        return []

    yaml_blocks = []

    # Find all YAML code blocks
    yaml_pattern = r'```yaml\n(.*?)\n```'
    matches = re.findall(yaml_pattern, content, re.DOTALL)

    for match in matches:
        try:
            parsed = yaml.safe_load(match)
            if parsed and isinstance(parsed, dict):
                yaml_blocks.append(parsed)
        except yaml.YAMLError:
            continue

    return yaml_blocks

def categorize_response(yaml_content: Dict[str, Any], input_data: Dict[str, Any]) -> List[str]:
    """
    Categorize response based on content and context.

    Returns:
        List of category tags
    """
    categories = []

    # Check task field for keywords
    task = str(yaml_content.get('task', '')).lower()

    # Command categories
    if 'git' in task or 'commit' in task or 'branch' in task:
        categories.append('git')
    if 'monday' in task or 'board' in task or 'project' in task:
        categories.append('monday')
    if 'crypto' in task or 'bitcoin' in task or 'ethereum' in task:
        categories.append('crypto')
    if 'file' in task or 'edit' in task or 'create' in task or 'write' in task:
        categories.append('file_operations')
    if 'test' in task or 'debug' in task or 'fix' in task:
        categories.append('debugging')
    if 'install' in task or 'setup' in task or 'config' in task:
        categories.append('setup')
    if 'analysis' in task or 'research' in task or 'understand' in task:
        categories.append('research')
    if 'hook' in task or 'agent' in task or 'command' in task:
        categories.append('claude_customization')

    # Status-based categories
    status = yaml_content.get('status', '').lower()
    if status == 'success':
        categories.append('completed')
    elif status == 'failed' or status == 'error':
        categories.append('errors')
    elif 'progress' in status:
        categories.append('in_progress')

    # Check for file modifications
    if yaml_content.get('files') or yaml_content.get('files_modified'):
        categories.append('code_changes')

    # Check for commands
    if yaml_content.get('commands'):
        categories.append('commands_to_run')

    # Tool usage from input data
    tools_used = input_data.get('tools_used', [])
    if tools_used:
        if any('bash' in str(tool).lower() for tool in tools_used):
            categories.append('bash_operations')
        if any('read' in str(tool).lower() or 'write' in str(tool).lower() for tool in tools_used):
            categories.append('file_io')

    # Default category if none found
    if not categories:
        categories.append('general')

    return categories

def generate_note_id(content: Dict[str, Any]) -> str:
    """Generate a unique ID for the note based on content hash."""
    content_str = json.dumps(content, sort_keys=True)
    return hashlib.md5(content_str.encode()).hexdigest()[:8]

def save_to_markdown(enriched_note: Dict[str, Any], notes_dir: Path):
    """
    Save enriched note to markdown file with YAML frontmatter.
    """
    # Create directory structure
    date_str = datetime.fromisoformat(enriched_note['timestamp']).strftime('%Y-%m-%d')
    day_dir = notes_dir / 'knowledge' / date_str
    day_dir.mkdir(parents=True, exist_ok=True)

    # Generate filename
    note_id = enriched_note['note_id']
    task_slug = re.sub(r'[^\w\s-]', '', enriched_note['response'].get('task', 'note'))[:50]
    task_slug = re.sub(r'[-\s]+', '-', task_slug).strip('-')
    filename = f"{note_id}_{task_slug}.md"

    # Create markdown content with YAML frontmatter
    frontmatter = {
        'id': note_id,
        'timestamp': enriched_note['timestamp'],
        'session_id': enriched_note['session_id'],
        'categories': enriched_note['categories'],
        'tools_used': enriched_note.get('tools_used', []),
        'status': enriched_note['response'].get('status', 'unknown')
    }

    content = "---\n"
    content += yaml.safe_dump(frontmatter, default_flow_style=False) if yaml else json.dumps(frontmatter, indent=2)
    content += "---\n\n"

    # Add user query if available
    if enriched_note.get('user_query'):
        content += f"## User Query\n\n{enriched_note['user_query']}\n\n"

    # Add YAML response
    content += "## Response\n\n```yaml\n"
    content += yaml.safe_dump(enriched_note['response'], default_flow_style=False) if yaml else json.dumps(enriched_note['response'], indent=2)
    content += "```\n\n"

    # Add context if available
    if enriched_note.get('context'):
        content += "## Context\n\n"
        for key, value in enriched_note['context'].items():
            content += f"- **{key}**: {value}\n"
        content += "\n"

    # Write to file
    file_path = day_dir / filename
    with open(file_path, 'w') as f:
        f.write(content)

    return file_path

def save_to_json_chronicle(enriched_note: Dict[str, Any], notes_dir: Path):
    """
    Append to JSON chronicle for fast searching and analysis.
    """
    chronicle_dir = notes_dir / 'knowledge' / '.chronicle'
    chronicle_dir.mkdir(parents=True, exist_ok=True)

    # Monthly chronicle files for manageable size
    date = datetime.fromisoformat(enriched_note['timestamp'])
    chronicle_file = chronicle_dir / f"{date.strftime('%Y-%m')}.json"

    # Read existing chronicle or initialize
    chronicle = []
    if chronicle_file.exists():
        try:
            with open(chronicle_file, 'r') as f:
                chronicle = json.load(f)
        except (json.JSONDecodeError, ValueError):
            chronicle = []

    # Append new note
    chronicle.append(enriched_note)

    # Write back
    with open(chronicle_file, 'w') as f:
        json.dump(chronicle, f, indent=2, default=str)

    return chronicle_file

def update_category_index(categories: List[str], note_id: str, timestamp: str, notes_dir: Path):
    """
    Update category index for fast category-based retrieval.
    """
    index_file = notes_dir / 'knowledge' / '.index' / 'categories.json'
    index_file.parent.mkdir(parents=True, exist_ok=True)

    # Load existing index
    index = {}
    if index_file.exists():
        try:
            with open(index_file, 'r') as f:
                index = json.load(f)
        except (json.JSONDecodeError, ValueError):
            index = {}

    # Update index
    for category in categories:
        if category not in index:
            index[category] = []

        # Add note reference
        note_ref = {
            'id': note_id,
            'timestamp': timestamp
        }

        # Avoid duplicates
        if not any(n['id'] == note_id for n in index[category]):
            index[category].append(note_ref)
            # Keep sorted by timestamp (newest first)
            index[category].sort(key=lambda x: x['timestamp'], reverse=True)
            # Limit to 100 most recent per category
            index[category] = index[category][:100]

    # Write back
    with open(index_file, 'w') as f:
        json.dump(index, f, indent=2)

def get_session_data() -> Dict[str, Any]:
    """
    Get current session data from global session storage.
    """
    session_file = Path.home() / '.claude' / 'data' / 'sessions' / 'current_session.json'
    if session_file.exists():
        try:
            with open(session_file, 'r') as f:
                return json.load(f)
        except:
            pass
    return {}

def main():
    try:
        # Read input from stdin
        input_data = json.load(sys.stdin)

        # Extract response content
        response_content = input_data.get('response', {}).get('content', '')
        if not response_content:
            sys.exit(0)

        # Extract YAML blocks
        yaml_blocks = extract_yaml_blocks(response_content)
        if not yaml_blocks:
            sys.exit(0)

        # Get session data
        session_data = get_session_data()
        session_id = input_data.get('session_id', session_data.get('session_id', 'unknown'))

        # Setup notes directory
        notes_dir = Path.cwd() / 'notes'
        notes_dir.mkdir(exist_ok=True)

        # Process each YAML block
        for yaml_content in yaml_blocks:
            # Skip empty or invalid blocks
            if not yaml_content or not isinstance(yaml_content, dict):
                continue

            # Generate note ID
            note_id = generate_note_id(yaml_content)

            # Categorize response
            categories = categorize_response(yaml_content, input_data)

            # Build enriched note
            enriched_note = {
                'note_id': note_id,
                'timestamp': datetime.now().isoformat(),
                'session_id': session_id,
                'categories': categories,
                'response': yaml_content,
                'user_query': input_data.get('user_query', ''),
                'tools_used': input_data.get('tools_used', []),
                'context': {
                    'working_directory': os.getcwd(),
                    'project': Path.cwd().name
                }
            }

            # Add file modifications if present
            if 'files_modified' in input_data:
                enriched_note['files_modified'] = input_data['files_modified']

            # Save in multiple formats
            md_path = save_to_markdown(enriched_note, notes_dir)
            json_path = save_to_json_chronicle(enriched_note, notes_dir)

            # Update category index
            update_category_index(categories, note_id, enriched_note['timestamp'], notes_dir)

            # Log success (optional, for debugging)
            if os.getenv('DEBUG'):
                print(f"Saved YAML response: {md_path}", file=sys.stderr)

        # Generate daily summary if it's end of day (optional enhancement)
        # This could be triggered based on time or session end

        sys.exit(0)

    except Exception as e:
        # Log error if debugging
        if os.getenv('DEBUG'):
            print(f"Error in post_response hook: {e}", file=sys.stderr)
        # Always exit cleanly to not disrupt Claude
        sys.exit(0)

if __name__ == '__main__':
    main()