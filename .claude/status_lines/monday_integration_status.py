#!/usr/bin/env -S uv run --quiet
# /// script
# dependencies = [
#     "requests",
#     "python-dateutil",
# ]
# ///

"""
Monday.com Integration Status Line for Claude Code
Live project status with task counts, priorities, sprint progress, and team workload
"""

import json
import os
import sys
from datetime import datetime, timedelta, timezone
from dateutil import parser
from typing import Dict, List, Any, Optional
import requests

# ANSI color codes
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GRAY = "\033[90m"
    MAGENTA = "\033[95m"
    WHITE = "\033[97m"

def get_priority_color(priority: str) -> str:
    """Get color based on priority level."""
    priority_lower = priority.lower() if priority else ""
    if "critical" in priority_lower or "urgent" in priority_lower:
        return Colors.RED
    elif "high" in priority_lower:
        return Colors.YELLOW
    elif "medium" in priority_lower:
        return Colors.CYAN
    elif "low" in priority_lower:
        return Colors.GREEN
    else:
        return Colors.GRAY

def get_status_color(status: str) -> str:
    """Get color based on status."""
    status_lower = status.lower() if status else ""
    if "done" in status_lower or "complete" in status_lower:
        return Colors.GREEN
    elif "working" in status_lower or "progress" in status_lower:
        return Colors.YELLOW
    elif "stuck" in status_lower or "blocked" in status_lower:
        return Colors.RED
    elif "review" in status_lower:
        return Colors.CYAN
    else:
        return Colors.GRAY

def parse_date_safely(date_value: Any) -> Optional[datetime]:
    """Safely parse various date formats."""
    if not date_value:
        return None

    try:
        if isinstance(date_value, dict) and 'date' in date_value:
            date_str = date_value['date']
        else:
            date_str = str(date_value)

        # Try parsing the date
        parsed = parser.parse(date_str)

        # Make timezone-aware if needed
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)

        return parsed
    except:
        return None

def fetch_monday_data(api_token: str) -> Optional[Dict[str, Any]]:
    """Fetch data from Monday.com API."""
    if not api_token:
        return None

    url = "https://api.monday.com/v2"
    headers = {
        "Authorization": api_token,
        "Content-Type": "application/json"
    }

    # Query to get user's items and board information
    query = """
    {
        me {
            name
        }
        boards(limit: 10, order_by: used_at) {
            id
            name
            items_page(limit: 500) {
                items {
                    id
                    name
                    column_values {
                        id
                        text
                        value
                    }
                }
            }
        }
    }
    """

    try:
        response = requests.post(url, json={"query": query}, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        if "errors" in data:
            return None

        return data.get("data")
    except:
        return None

def analyze_items(boards: List[Dict]) -> Dict[str, Any]:
    """Analyze items across all boards."""
    stats = {
        'total_items': 0,
        'my_items': 0,
        'overdue': 0,
        'due_today': 0,
        'due_this_week': 0,
        'in_progress': 0,
        'blocked': 0,
        'completed_today': 0,
        'high_priority': 0,
        'by_status': {},
        'sprint_progress': 0,
        'sprint_total': 0
    }

    now = datetime.now(timezone.utc)
    today = now.date()
    week_end = (now + timedelta(days=7)).date()

    for board in boards:
        items = board.get('items_page', {}).get('items', [])

        for item in items:
            stats['total_items'] += 1

            # Parse column values
            columns = {}
            for col in item.get('column_values', []):
                col_id = col['id']
                columns[col_id] = {
                    'text': col.get('text', ''),
                    'value': col.get('value')
                }

            # Check status
            status = None
            for col_id, col_data in columns.items():
                if 'status' in col_id.lower():
                    status = col_data['text']
                    break

            if status:
                status_lower = status.lower()
                stats['by_status'][status] = stats['by_status'].get(status, 0) + 1

                if 'progress' in status_lower or 'working' in status_lower:
                    stats['in_progress'] += 1
                elif 'stuck' in status_lower or 'blocked' in status_lower:
                    stats['blocked'] += 1
                elif 'done' in status_lower or 'complete' in status_lower:
                    # Check if completed today
                    for col_id, col_data in columns.items():
                        if 'date' in col_id.lower() and col_data['value']:
                            try:
                                date_val = json.loads(col_data['value'])
                                if date_val and 'date' in date_val:
                                    completed_date = parse_date_safely(date_val)
                                    if completed_date and completed_date.date() == today:
                                        stats['completed_today'] += 1
                                        break
                            except:
                                pass

            # Check priority
            for col_id, col_data in columns.items():
                if 'priority' in col_id.lower():
                    priority = col_data['text']
                    if priority and any(p in priority.lower() for p in ['high', 'urgent', 'critical']):
                        stats['high_priority'] += 1
                    break

            # Check due dates
            for col_id, col_data in columns.items():
                if 'date' in col_id.lower() or 'due' in col_id.lower():
                    if col_data['value']:
                        try:
                            date_val = json.loads(col_data['value'])
                            if date_val and 'date' in date_val:
                                due_date = parse_date_safely(date_val)
                                if due_date:
                                    due_date_only = due_date.date()
                                    if due_date_only < today:
                                        stats['overdue'] += 1
                                    elif due_date_only == today:
                                        stats['due_today'] += 1
                                    elif due_date_only <= week_end:
                                        stats['due_this_week'] += 1
                                    break
                        except:
                            pass

            # Check if in current sprint
            for col_id, col_data in columns.items():
                if 'sprint' in col_id.lower():
                    if col_data['text'] and 'current' in col_data['text'].lower():
                        stats['sprint_total'] += 1
                        if status and ('done' in status.lower() or 'complete' in status.lower()):
                            stats['sprint_progress'] += 1
                    break

    return stats

def format_status_distribution(by_status: Dict[str, int]) -> str:
    """Format status distribution as a compact string."""
    if not by_status:
        return ""

    # Sort by count
    sorted_statuses = sorted(by_status.items(), key=lambda x: x[1], reverse=True)[:3]  # Top 3

    parts = []
    for status, count in sorted_statuses:
        color = get_status_color(status)
        # Shorten status names
        short_status = status[:8] if len(status) > 8 else status
        parts.append(f"{color}{short_status}:{count}{Colors.RESET}")

    return " ".join(parts)

def main():
    """Generate Monday.com integration status line."""
    api_token = os.environ.get('MONDAY_API_TOKEN')

    if not api_token:
        print(f"{Colors.YELLOW}📋 Monday.com: {Colors.GRAY}No API token configured{Colors.RESET}")
        return

    try:
        # Fetch data from Monday.com
        data = fetch_monday_data(api_token)

        if not data:
            print(f"{Colors.RED}📋 Monday.com: Connection failed{Colors.RESET}")
            return

        # Get user name
        user_name = data.get('me', {}).get('name', 'Unknown')
        boards = data.get('boards', [])

        if not boards:
            print(f"{Colors.GRAY}📋 Monday.com: No boards found{Colors.RESET}")
            return

        # Analyze items
        stats = analyze_items(boards)

        # Build status line components
        status_parts = []

        # Board count
        status_parts.append(f"{Colors.CYAN}📋 {len(boards)} boards{Colors.RESET}")

        # Total items
        if stats['total_items'] > 0:
            status_parts.append(f"{Colors.WHITE}{stats['total_items']} items{Colors.RESET}")

        # Critical indicators
        if stats['overdue'] > 0:
            status_parts.append(f"{Colors.RED}⚠ {stats['overdue']} overdue{Colors.RESET}")

        if stats['due_today'] > 0:
            status_parts.append(f"{Colors.YELLOW}📅 {stats['due_today']} today{Colors.RESET}")

        if stats['blocked'] > 0:
            status_parts.append(f"{Colors.RED}🚫 {stats['blocked']} blocked{Colors.RESET}")

        # Progress indicators
        if stats['in_progress'] > 0:
            status_parts.append(f"{Colors.YELLOW}⚡ {stats['in_progress']} active{Colors.RESET}")

        if stats['high_priority'] > 0:
            status_parts.append(f"{Colors.MAGENTA}🔥 {stats['high_priority']} high-pri{Colors.RESET}")

        # Sprint progress
        if stats['sprint_total'] > 0:
            sprint_percent = (stats['sprint_progress'] / stats['sprint_total']) * 100
            sprint_color = Colors.GREEN if sprint_percent >= 75 else Colors.YELLOW if sprint_percent >= 50 else Colors.CYAN
            status_parts.append(f"{sprint_color}Sprint: {sprint_percent:.0f}%{Colors.RESET}")

        # Completed today
        if stats['completed_today'] > 0:
            status_parts.append(f"{Colors.GREEN}✓ {stats['completed_today']} done{Colors.RESET}")

        # Status distribution (compact)
        status_dist = format_status_distribution(stats['by_status'])
        if status_dist:
            status_parts.append(f"{Colors.GRAY}[{status_dist}{Colors.GRAY}]{Colors.RESET}")

        # Join all parts
        status_line = " │ ".join(status_parts)

        # Add urgency indicator if needed
        urgent_items = stats['overdue'] + stats['due_today']
        if urgent_items > 5:
            status_line = f"{Colors.RED}🔴 URGENT ({urgent_items}){Colors.RESET} │ " + status_line
        elif urgent_items > 0:
            status_line = f"{Colors.YELLOW}⚡ Action needed{Colors.RESET} │ " + status_line

        print(status_line)

    except Exception as e:
        print(f"{Colors.RED}📋 Monday.com Error: {str(e)[:50]}{Colors.RESET}")

if __name__ == "__main__":
    main()