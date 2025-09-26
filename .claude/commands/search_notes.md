# Search Notes

Search through your saved YAML response knowledge base to find previous solutions, patterns, and insights.

## Usage
```
/search_notes [query] [--category CATEGORY] [--days DAYS] [--status STATUS]
```

## Arguments
- `query`: Search term or phrase to look for in saved responses
- `--category`: Filter by category (git, monday, crypto, debugging, etc.)
- `--days`: Limit search to last N days (default: all)
- `--status`: Filter by status (success, failed, in_progress)

## Examples

Search for all git-related responses:
```
/search_notes --category git
```

Find responses about Monday.com from the last week:
```
/search_notes monday --days 7
```

Search for successful file operations:
```
/search_notes "file edit" --status success
```

Find debugging solutions:
```
/search_notes error --category debugging
```

## Implementation

The search command scans through the knowledge base stored in `notes/knowledge/` and returns:
- Matching YAML responses with context
- Links to full markdown notes
- Summary of categories and patterns found
- Suggestions for similar searches

Results are ranked by:
1. Relevance to search query
2. Recency (newer results ranked higher)
3. Success status (successful solutions prioritized)

## Categories

The system automatically categorizes responses:
- **git**: Version control operations
- **monday**: Project management tasks
- **crypto**: Cryptocurrency analysis
- **file_operations**: File creation/editing
- **debugging**: Bug fixes and error resolution
- **setup**: Installation and configuration
- **research**: Analysis and investigation
- **claude_customization**: Hooks, agents, commands
- **bash_operations**: Shell commands
- **completed**: Successfully finished tasks
- **errors**: Failed operations
- **in_progress**: Ongoing work

## Implementation Script

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml"]
# ///

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
    Format search results for display.
    """
    if not results:
        return "No matching notes found."

    output = []
    output.append(f"# Found {len(results)} matching note(s)\n")

    # Group by category
    categories_found = {}
    for result in results[:20]:  # Limit display to 20 most recent
        for cat in result.get('categories', ['general']):
            if cat not in categories_found:
                categories_found[cat] = 0
            categories_found[cat] += 1

    # Category summary
    if categories_found:
        output.append("## Categories")
        for cat, count in sorted(categories_found.items(), key=lambda x: x[1], reverse=True):
            output.append(f"- **{cat}**: {count} note(s)")
        output.append("")

    # Display results
    output.append("## Results\n")

    for i, result in enumerate(results[:10], 1):  # Show top 10
        timestamp = datetime.fromisoformat(result['timestamp'])
        date_str = timestamp.strftime('%Y-%m-%d %H:%M')

        response = result.get('response', {})
        task = response.get('task', 'Untitled')
        status = response.get('status', 'unknown')
        categories = ', '.join(result.get('categories', ['general']))

        output.append(f"### {i}. {task}")
        output.append(f"- **Date**: {date_str}")
        output.append(f"- **Status**: {status}")
        output.append(f"- **Categories**: {categories}")
        output.append(f"- **ID**: {result.get('note_id', 'unknown')}")

        # Show snippet of user query if available
        if result.get('user_query'):
            query_snippet = result['user_query'][:100]
            if len(result['user_query']) > 100:
                query_snippet += "..."
            output.append(f"- **Query**: {query_snippet}")

        # Show key details from response
        if response.get('details'):
            output.append("- **Details**:")
            details = response['details']
            if isinstance(details, dict):
                for key, value in list(details.items())[:3]:  # First 3 items
                    output.append(f"  - {key}: {str(value)[:50]}")
            elif isinstance(details, str):
                output.append(f"  - {details[:100]}")

        output.append("")

    if len(results) > 10:
        output.append(f"\n*Showing 10 of {len(results)} results. Refine your search for more specific results.*")

    return '\n'.join(output)

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
```