#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml"]
# ///

"""
Daily Summary Generator
========================
Generates a daily summary of all YAML responses logged during the day.
Can be called manually or triggered automatically at session end.
"""

import json
import sys
from pathlib import Path
from datetime import datetime, date, timedelta
from typing import List, Dict, Any
from collections import defaultdict

try:
    import yaml
except ImportError:
    yaml = None

def load_daily_notes(target_date: date = None) -> List[Dict[str, Any]]:
    """
    Load all notes from a specific day.
    """
    if target_date is None:
        target_date = date.today()

    notes_dir = Path.cwd() / 'notes' / 'knowledge'
    chronicle_dir = notes_dir / '.chronicle'

    if not chronicle_dir.exists():
        return []

    # Load from monthly chronicle
    chronicle_file = chronicle_dir / f"{target_date.strftime('%Y-%m')}.json"
    if not chronicle_file.exists():
        return []

    daily_notes = []
    target_date_str = target_date.isoformat()

    try:
        with open(chronicle_file, 'r') as f:
            all_notes = json.load(f)

        for note in all_notes:
            note_date = datetime.fromisoformat(note['timestamp']).date()
            if note_date == target_date:
                daily_notes.append(note)

    except (json.JSONDecodeError, ValueError):
        pass

    return daily_notes

def analyze_notes(notes: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze notes to extract patterns and statistics.
    """
    analysis = {
        'total_responses': len(notes),
        'categories': defaultdict(int),
        'statuses': defaultdict(int),
        'tools_usage': defaultdict(int),
        'tasks_completed': [],
        'tasks_failed': [],
        'tasks_in_progress': [],
        'key_accomplishments': [],
        'patterns': []
    }

    for note in notes:
        # Count categories
        for cat in note.get('categories', ['general']):
            analysis['categories'][cat] += 1

        # Count statuses
        response = note.get('response', {})
        status = response.get('status', 'unknown')
        analysis['statuses'][status] += 1

        # Track task outcomes
        task = response.get('task', 'Untitled task')
        task_entry = {
            'task': task,
            'time': datetime.fromisoformat(note['timestamp']).strftime('%H:%M'),
            'categories': note.get('categories', [])
        }

        if status == 'success' or status == 'completed':
            analysis['tasks_completed'].append(task_entry)
        elif status == 'failed' or status == 'error':
            analysis['tasks_failed'].append(task_entry)
        elif 'progress' in status.lower():
            analysis['tasks_in_progress'].append(task_entry)

        # Count tool usage
        for tool in note.get('tools_used', []):
            if isinstance(tool, str):
                analysis['tools_usage'][tool] += 1

        # Identify key accomplishments (completed tasks with files modified)
        if status == 'success' and note.get('files_modified'):
            analysis['key_accomplishments'].append({
                'task': task,
                'files_count': len(note['files_modified'])
            })

    # Convert defaultdicts to regular dicts for JSON serialization
    analysis['categories'] = dict(analysis['categories'])
    analysis['statuses'] = dict(analysis['statuses'])
    analysis['tools_usage'] = dict(analysis['tools_usage'])

    # Identify patterns
    if analysis['categories']:
        top_category = max(analysis['categories'].items(), key=lambda x: x[1])
        analysis['patterns'].append(f"Most work focused on: {top_category[0]} ({top_category[1]} responses)")

    if analysis['tools_usage']:
        top_tool = max(analysis['tools_usage'].items(), key=lambda x: x[1])
        analysis['patterns'].append(f"Most used tool: {top_tool[0]} ({top_tool[1]} times)")

    success_rate = 0
    if analysis['total_responses'] > 0:
        success_count = analysis['statuses'].get('success', 0) + analysis['statuses'].get('completed', 0)
        success_rate = (success_count / analysis['total_responses']) * 100
        analysis['success_rate'] = f"{success_rate:.1f}%"

    return analysis

def generate_markdown_summary(analysis: Dict[str, Any], target_date: date) -> str:
    """
    Generate a markdown summary from the analysis.
    """
    summary = []
    summary.append(f"# Daily Summary - {target_date.strftime('%B %d, %Y')}\n")

    # Overview
    summary.append("## Overview")
    summary.append(f"- **Total Responses**: {analysis['total_responses']}")
    if 'success_rate' in analysis:
        summary.append(f"- **Success Rate**: {analysis['success_rate']}")
    summary.append("")

    # Tasks Completed
    if analysis['tasks_completed']:
        summary.append(f"## ✅ Completed Tasks ({len(analysis['tasks_completed'])})")
        for task in analysis['tasks_completed'][:10]:  # Limit to 10
            summary.append(f"- [{task['time']}] {task['task']}")
        if len(analysis['tasks_completed']) > 10:
            summary.append(f"  *... and {len(analysis['tasks_completed']) - 10} more*")
        summary.append("")

    # Key Accomplishments
    if analysis['key_accomplishments']:
        summary.append("## 🎯 Key Accomplishments")
        for accomplishment in analysis['key_accomplishments'][:5]:
            summary.append(f"- {accomplishment['task']} ({accomplishment['files_count']} files modified)")
        summary.append("")

    # Failed Tasks
    if analysis['tasks_failed']:
        summary.append(f"## ❌ Failed Tasks ({len(analysis['tasks_failed'])})")
        for task in analysis['tasks_failed']:
            summary.append(f"- [{task['time']}] {task['task']}")
        summary.append("")

    # In Progress
    if analysis['tasks_in_progress']:
        summary.append(f"## 🔄 In Progress ({len(analysis['tasks_in_progress'])})")
        for task in analysis['tasks_in_progress']:
            summary.append(f"- {task['task']}")
        summary.append("")

    # Category Distribution
    if analysis['categories']:
        summary.append("## 📊 Work Distribution")
        sorted_categories = sorted(analysis['categories'].items(), key=lambda x: x[1], reverse=True)
        for cat, count in sorted_categories:
            bar = '█' * min(count * 2, 20)  # Visual bar chart
            summary.append(f"- **{cat}**: {bar} ({count})")
        summary.append("")

    # Tools Usage
    if analysis['tools_usage']:
        summary.append("## 🔧 Tools Used")
        sorted_tools = sorted(analysis['tools_usage'].items(), key=lambda x: x[1], reverse=True)[:5]
        for tool, count in sorted_tools:
            summary.append(f"- {tool}: {count} times")
        summary.append("")

    # Patterns and Insights
    if analysis['patterns']:
        summary.append("## 💡 Patterns & Insights")
        for pattern in analysis['patterns']:
            summary.append(f"- {pattern}")
        summary.append("")

    # Footer
    summary.append("---")
    summary.append(f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")

    return '\n'.join(summary)

def generate_yaml_summary(analysis: Dict[str, Any], target_date: date) -> str:
    """
    Generate a YAML-formatted summary.
    """
    summary = {
        'daily_summary': {
            'date': target_date.isoformat(),
            'generated_at': datetime.now().isoformat(),
            'overview': {
                'total_responses': analysis['total_responses'],
                'success_rate': analysis.get('success_rate', 'N/A')
            },
            'tasks': {
                'completed': len(analysis['tasks_completed']),
                'failed': len(analysis['tasks_failed']),
                'in_progress': len(analysis['tasks_in_progress'])
            },
            'top_categories': [],
            'top_tools': [],
            'key_accomplishments': [],
            'patterns': analysis['patterns']
        }
    }

    # Add top categories
    if analysis['categories']:
        sorted_cats = sorted(analysis['categories'].items(), key=lambda x: x[1], reverse=True)[:3]
        for cat, count in sorted_cats:
            summary['daily_summary']['top_categories'].append({
                'category': cat,
                'count': count
            })

    # Add top tools
    if analysis['tools_usage']:
        sorted_tools = sorted(analysis['tools_usage'].items(), key=lambda x: x[1], reverse=True)[:3]
        for tool, count in sorted_tools:
            summary['daily_summary']['top_tools'].append({
                'tool': tool,
                'usage': count
            })

    # Add key accomplishments
    for acc in analysis['key_accomplishments'][:5]:
        summary['daily_summary']['key_accomplishments'].append(acc['task'])

    if yaml:
        return yaml.safe_dump(summary, default_flow_style=False, sort_keys=False)
    else:
        return json.dumps(summary, indent=2)

def save_summary(summary_text: str, target_date: date, format: str = 'markdown'):
    """
    Save the summary to the notes directory.
    """
    notes_dir = Path.cwd() / 'notes' / 'knowledge' / 'summaries'
    notes_dir.mkdir(parents=True, exist_ok=True)

    extension = 'md' if format == 'markdown' else 'yaml'
    filename = f"daily_summary_{target_date.isoformat()}.{extension}"
    file_path = notes_dir / filename

    with open(file_path, 'w') as f:
        f.write(summary_text)

    return file_path

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Generate daily summary of YAML responses')
    parser.add_argument('--date', help='Target date (YYYY-MM-DD), defaults to today')
    parser.add_argument('--format', choices=['markdown', 'yaml'], default='markdown',
                        help='Output format (default: markdown)')
    parser.add_argument('--save', action='store_true', help='Save summary to file')

    args = parser.parse_args()

    # Parse target date
    if args.date:
        try:
            target_date = date.fromisoformat(args.date)
        except ValueError:
            print(f"Error: Invalid date format. Use YYYY-MM-DD")
            sys.exit(1)
    else:
        target_date = date.today()

    # Load notes
    notes = load_daily_notes(target_date)

    if not notes:
        print(f"No notes found for {target_date.isoformat()}")
        sys.exit(0)

    # Analyze notes
    analysis = analyze_notes(notes)

    # Generate summary
    if args.format == 'markdown':
        summary = generate_markdown_summary(analysis, target_date)
    else:
        summary = generate_yaml_summary(analysis, target_date)

    # Output or save
    if args.save:
        file_path = save_summary(summary, target_date, args.format)
        print(f"Summary saved to: {file_path}")
        print("\n" + summary)
    else:
        print(summary)

if __name__ == '__main__':
    main()