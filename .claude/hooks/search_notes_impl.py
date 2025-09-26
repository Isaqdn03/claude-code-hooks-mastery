#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml"]
# ///

"""
Search Notes Implementation
============================
Search through saved YAML response knowledge base.
"""

import json
import sys
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any
import re

try:
    import yaml
except ImportError:
    yaml = None

def search_notes(query: str = None, category: str = None, days: int = None, status: str = None) -> List[Dict[str, Any]]:
    """
    Search through the knowledge base for matching notes.
    """
    notes_dir = Path.cwd() / 'notes' / 'knowledge'
    if not notes_dir.exists():
        return []

    results = []

    # Calculate date filter
    date_limit = None
    if days:
        date_limit = datetime.now() - timedelta(days=days)

    # Search through chronicle files (faster for large searches)
    chronicle_dir = notes_dir / '.chronicle'
    if chronicle_dir.exists():
        for chronicle_file in sorted(chronicle_dir.glob('*.json'), reverse=True):
            try:
                with open(chronicle_file, 'r') as f:
                    notes = json.load(f)

                for note in notes:
                    # Apply filters
                    if date_limit:
                        note_date = datetime.fromisoformat(note['timestamp'])
                        if note_date < date_limit:
                            continue

                    if category and category not in note.get('categories', []):
                        continue

                    if status:
                        note_status = note.get('response', {}).get('status', '')
                        if status.lower() != note_status.lower():
                            continue

                    if query:
                        # Search in response content
                        response_str = json.dumps(note.get('response', {})).lower()
                        if query.lower() not in response_str:
                            # Also check user query
                            user_query = note.get('user_query', '').lower()
                            if query.lower() not in user_query:
                                continue

                    results.append(note)

            except (json.JSONDecodeError, ValueError):
                continue

    # Sort by relevance and recency
    results.sort(key=lambda x: x['timestamp'], reverse=True)

    return results

def format_results(results: List[Dict[str, Any]]) -> str:
    """
    Format search results for display in YAML style.
    """
    if not results:
        output = {
            "search_results": "No matching notes found",
            "suggestions": [
                "Try a broader search term",
                "Check if notes have been created yet",
                "Use /search_notes without arguments to see all notes"
            ]
        }
        if yaml:
            return "```yaml\n" + yaml.safe_dump(output, default_flow_style=False) + "```"
        else:
            return json.dumps(output, indent=2)

    # Build structured output
    output = {
        "search_summary": {
            "total_found": len(results),
            "showing": min(10, len(results)),
            "categories_found": {}
        },
        "results": []
    }

    # Count categories
    for result in results:
        for cat in result.get('categories', ['general']):
            if cat not in output['search_summary']['categories_found']:
                output['search_summary']['categories_found'][cat] = 0
            output['search_summary']['categories_found'][cat] += 1

    # Format top results
    for i, result in enumerate(results[:10], 1):
        timestamp = datetime.fromisoformat(result['timestamp'])
        response = result.get('response', {})

        result_entry = {
            "index": i,
            "task": response.get('task', 'Untitled'),
            "date": timestamp.strftime('%Y-%m-%d %H:%M'),
            "status": response.get('status', 'unknown'),
            "categories": result.get('categories', ['general']),
            "note_id": result.get('note_id', 'unknown')
        }

        # Add user query snippet if available
        if result.get('user_query'):
            query_snippet = result['user_query'][:100]
            if len(result['user_query']) > 100:
                query_snippet += "..."
            result_entry['user_query'] = query_snippet

        # Add key details
        if response.get('details'):
            details = response['details']
            if isinstance(details, dict):
                result_entry['details'] = {}
                for key, value in list(details.items())[:3]:
                    result_entry['details'][key] = str(value)[:100]
            else:
                result_entry['details'] = str(details)[:150]

        # Add notes if present
        if response.get('notes'):
            notes = response['notes']
            if isinstance(notes, list):
                result_entry['notes'] = notes[:2]  # First 2 notes
            else:
                result_entry['notes'] = str(notes)[:150]

        output['results'].append(result_entry)

    # Add navigation hints
    if len(results) > 10:
        output['navigation'] = {
            "total_results": len(results),
            "hint": "Showing top 10 results. Refine search for more specific results."
        }

    # Suggestions for related searches
    if output['search_summary']['categories_found']:
        top_categories = sorted(
            output['search_summary']['categories_found'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]
        output['suggested_searches'] = [
            f"/search_notes --category {cat[0]}"
            for cat in top_categories
        ]

    # Return as YAML
    if yaml:
        return "```yaml\n" + yaml.safe_dump(output, default_flow_style=False, sort_keys=False) + "```"
    else:
        return "```json\n" + json.dumps(output, indent=2) + "\n```"

def main():
    parser = argparse.ArgumentParser(description='Search YAML response knowledge base')
    parser.add_argument('query', nargs='*', help='Search query')
    parser.add_argument('--category', help='Filter by category')
    parser.add_argument('--days', type=int, help='Limit to last N days')
    parser.add_argument('--status', help='Filter by status')

    args = parser.parse_args()

    # Join query words
    query = ' '.join(args.query) if args.query else None

    # Search notes
    results = search_notes(
        query=query,
        category=args.category,
        days=args.days,
        status=args.status
    )

    # Format and display results
    output = format_results(results)
    print(output)

if __name__ == '__main__':
    main()