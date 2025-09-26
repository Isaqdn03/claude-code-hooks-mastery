#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pyyaml",
# ]
# ///

"""
YAML Transcript Processor
=========================
Processes conversation transcripts to extract and log YAML responses.
Called by the Stop hook to analyze completed conversations.
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

def extract_yaml_from_text(text: str) -> List[Dict[str, Any]]:
    """Extract YAML blocks from text content."""
    if not yaml or not text:
        return []

    yaml_blocks = []

    # Find YAML code blocks
    yaml_pattern = r'```yaml\s*\n(.*?)\n```'
    matches = re.findall(yaml_pattern, text, re.DOTALL)

    for match in matches:
        try:
            parsed = yaml.safe_load(match)
            if parsed and isinstance(parsed, dict):
                yaml_blocks.append({
                    'raw': match.strip(),
                    'parsed': parsed
                })
        except:
            continue

    return yaml_blocks

def process_transcript(transcript_path: str, session_id: str) -> List[Dict[str, Any]]:
    """Process a transcript file to extract YAML responses."""
    if not os.path.exists(transcript_path):
        return []

    yaml_responses = []

    try:
        with open(transcript_path, 'r') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())

                    # Look for assistant messages
                    if (entry.get('type') == 'assistant' and
                        'message' in entry and
                        entry['message'].get('role') == 'assistant'):

                        message = entry['message']
                        content = message.get('content', [])

                        # Process text content
                        for item in content:
                            if item.get('type') == 'text':
                                text_content = item.get('text', '')
                                yaml_blocks = extract_yaml_from_text(text_content)

                                for block in yaml_blocks:
                                    # Create enriched response entry
                                    response_entry = {
                                        'note_id': hashlib.md5(
                                            (session_id + block['raw']).encode()
                                        ).hexdigest()[:8],
                                        'timestamp': entry.get('timestamp', datetime.now().isoformat()),
                                        'session_id': session_id,
                                        'message_id': message.get('id', ''),
                                        'yaml_content': block['parsed'],
                                        'raw_yaml': block['raw'],
                                        'categories': categorize_yaml_content(block['parsed']),
                                        'context': {
                                            'working_directory': entry.get('cwd', ''),
                                            'model': message.get('model', ''),
                                            'usage': message.get('usage', {}),
                                            'project': Path(entry.get('cwd', '')).name if entry.get('cwd') else ''
                                        }
                                    }

                                    yaml_responses.append(response_entry)

                except (json.JSONDecodeError, KeyError):
                    continue

    except Exception:
        pass

    return yaml_responses

def categorize_yaml_content(content: Dict[str, Any]) -> List[str]:
    """Categorize YAML content based on its structure and content."""
    categories = []

    # Check task field
    task = str(content.get('task', '')).lower()

    # Content-based categorization
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
    if 'hook' in task or 'agent' in task or 'command' in task:
        categories.append('claude_customization')
    if 'yaml' in task or 'logging' in task or 'response' in task:
        categories.append('system_development')

    # Status-based categorization
    status = str(content.get('status', '')).lower()
    if 'success' in status or 'complete' in status:
        categories.append('completed')
    elif 'fail' in status or 'error' in status:
        categories.append('failed')
    elif 'progress' in status:
        categories.append('in_progress')

    # Structure-based categorization
    if content.get('files'):
        categories.append('file_changes')
    if content.get('commands'):
        categories.append('commands_provided')
    if content.get('implementation_summary'):
        categories.append('implementation')
    if content.get('notes'):
        categories.append('documented')

    return categories if categories else ['general']

def save_yaml_responses(responses: List[Dict[str, Any]]):
    """Save YAML responses to the knowledge base."""
    if not responses:
        return []

    notes_dir = Path.cwd() / 'notes' / 'knowledge'
    notes_dir.mkdir(parents=True, exist_ok=True)

    saved_files = []

    for response in responses:
        # Create date-based directory using local timezone for consistency
        # Parse timestamp but convert to local timezone to avoid date folder confusion
        try:
            timestamp = datetime.fromisoformat(response['timestamp'].replace('Z', '+00:00'))
            # Convert to local timezone for consistent date folder naming
            local_timestamp = timestamp.astimezone()
            date_str = local_timestamp.strftime('%Y-%m-%d')
        except (ValueError, TypeError):
            # Fallback to current local date if timestamp parsing fails
            date_str = datetime.now().strftime('%Y-%m-%d')

        day_dir = notes_dir / date_str
        day_dir.mkdir(exist_ok=True)

        # Generate filename from task
        yaml_content = response['yaml_content']
        task = yaml_content.get('task', 'Untitled')
        task_slug = re.sub(r'[^\w\s-]', '', task)[:50]
        task_slug = re.sub(r'[-\s]+', '-', task_slug).strip('-')

        filename = f"{response['note_id']}_{task_slug}.md"
        file_path = day_dir / filename

        # Skip if file already exists (avoid duplicates)
        if file_path.exists():
            continue

        # Create markdown content with frontmatter
        frontmatter = {
            'id': response['note_id'],
            'timestamp': response['timestamp'],
            'session_id': response['session_id'],
            'message_id': response['message_id'],
            'categories': response['categories'],
            'status': yaml_content.get('status', 'unknown')
        }

        content = "---\n"
        if yaml:
            content += yaml.safe_dump(frontmatter, default_flow_style=False)
        else:
            content += json.dumps(frontmatter, indent=2)
        content += "---\n\n"

        # Add YAML response
        content += "## YAML Response\n\n"
        content += f"```yaml\n{response['raw_yaml']}\n```\n\n"

        # Add context
        if response.get('context'):
            content += "## Context\n\n"
            for key, value in response['context'].items():
                if value:
                    content += f"- **{key}**: {value}\n"
            content += "\n"

        # Write file
        try:
            with open(file_path, 'w') as f:
                f.write(content)
            saved_files.append(str(file_path))
        except:
            continue

        # Also save to JSON chronicle
        try:
            save_to_json_chronicle(response, notes_dir)
        except:
            pass

    return saved_files

def save_to_json_chronicle(response: Dict[str, Any], notes_dir: Path):
    """Save to JSON chronicle for searching."""
    chronicle_dir = notes_dir / '.chronicle'
    chronicle_dir.mkdir(exist_ok=True)

    # Monthly files - use local timezone for consistency
    try:
        timestamp = datetime.fromisoformat(response['timestamp'].replace('Z', '+00:00'))
        local_timestamp = timestamp.astimezone()
        chronicle_file = chronicle_dir / f"{local_timestamp.strftime('%Y-%m')}.json"
    except (ValueError, TypeError):
        # Fallback to current local date if timestamp parsing fails
        chronicle_file = chronicle_dir / f"{datetime.now().strftime('%Y-%m')}.json"

    # Load existing
    chronicle = []
    if chronicle_file.exists():
        try:
            with open(chronicle_file, 'r') as f:
                chronicle = json.load(f)
        except:
            chronicle = []

    # Add new response
    chronicle.append(response)

    # Save
    with open(chronicle_file, 'w') as f:
        json.dump(chronicle, f, indent=2, default=str)

def main():
    """Main function called by Stop hook."""
    try:
        # Read input from Stop hook
        input_data = json.load(sys.stdin)

        transcript_path = input_data.get('transcript_path')
        session_id = input_data.get('session_id', 'unknown')

        if not transcript_path:
            sys.exit(0)

        # Process transcript
        yaml_responses = process_transcript(transcript_path, session_id)

        if yaml_responses:
            saved_files = save_yaml_responses(yaml_responses)

            # Optional: Output summary for debugging
            if os.getenv('DEBUG_YAML_LOGGING'):
                print(f"Processed {len(yaml_responses)} YAML responses", file=sys.stderr)
                print(f"Saved {len(saved_files)} new files", file=sys.stderr)

        sys.exit(0)

    except Exception as e:
        # Log error if debugging enabled
        if os.getenv('DEBUG_YAML_LOGGING'):
            print(f"Error in YAML transcript processor: {e}", file=sys.stderr)
        sys.exit(0)

if __name__ == '__main__':
    main()