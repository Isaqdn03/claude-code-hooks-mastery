#!/usr/bin/env python3
# /// script
# dependencies = ["requests"]
# ///

"""
Monday.com Priorities Command Implementation

Analyzes and displays prioritized tasks and urgent items across Monday.com boards.
"""

import sys
import os
import argparse
import json
from datetime import datetime, timedelta, date
from pathlib import Path
from collections import defaultdict

# Add utils directory to path
utils_path = Path(__file__).parent / "utils"
sys.path.insert(0, str(utils_path))

try:
    from monday_api import MondayAPIClient, MondayAPIError
except ImportError as e:
    print(f"❌ Error importing Monday API client: {e}")
    print("Please ensure monday_api.py is in the utils directory")
    sys.exit(1)

def parse_column_value(column):
    """Parse Monday.com column values safely"""
    try:
        if column.get('value'):
            if column['value'].startswith('{'):
                return json.loads(column['value'])
            return column['value']
        return column.get('text', '')
    except (json.JSONDecodeError, AttributeError):
        return column.get('text', '')

def get_priority_from_item(item):
    """Extract priority information from item columns"""
    priority_columns = ['priority', 'priority_1', 'urgency', 'importance']

    for column in item.get('column_values', []):
        if any(priority_col in column['id'].lower() for priority_col in priority_columns):
            value = parse_column_value(column)
            if isinstance(value, dict) and 'text' in value:
                return value['text']
            elif isinstance(value, str) and value:
                return value

    return 'Normal'

def get_status_from_column(item):
    """Extract status information from item columns"""
    status_column_ids = ['status', 'status_1', 'status_2']

    for column in item.get('column_values', []):
        if column['id'] in status_column_ids or 'status' in column['id'].lower():
            value = parse_column_value(column)
            if isinstance(value, dict) and 'text' in value:
                return value['text']
            elif isinstance(value, str) and value:
                return value
    return 'Unknown'

def get_due_date_from_item(item):
    """Extract due date from item columns - always returns datetime.date or None"""
    date_column_ids = ['date', 'due_date', 'timeline', 'date_1']

    for column in item.get('column_values', []):
        if column['id'] in date_column_ids or 'date' in column['id'].lower():
            value = parse_column_value(column)

            # Handle dict format (JSON parsed dates)
            if isinstance(value, dict) and 'date' in value:
                date_str = value['date']
                if date_str:
                    return parse_date_string(date_str)

            # Handle string format (raw date strings)
            elif isinstance(value, str) and value.strip():
                return parse_date_string(value.strip())

    return None

def parse_date_string(date_str):
    """Parse various date string formats into datetime.date object"""
    if not date_str or date_str in ['', 'null', 'None']:
        return None

    try:
        # Try ISO format first (most common from Monday.com)
        if 'T' in date_str:
            # Full datetime string
            return datetime.fromisoformat(date_str.replace('Z', '+00:00')).date()
        else:
            # Date-only string (YYYY-MM-DD)
            return datetime.strptime(date_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        try:
            # Try other common formats
            for fmt in ['%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d', '%m-%d-%Y', '%d-%m-%Y']:
                return datetime.strptime(date_str, fmt).date()
        except (ValueError, TypeError):
            # If all parsing fails, return None rather than crashing
            print(f"⚠️  Warning: Could not parse date string: '{date_str}'")
            return None

def get_assignees_from_item(item):
    """Extract assigned people from item columns"""
    assignees = []

    for column in item.get('column_values', []):
        if column['type'] == 'multiple-person' or 'person' in column['id'].lower():
            value = parse_column_value(column)
            if isinstance(value, dict) and 'personsAndTeams' in value:
                for person in value['personsAndTeams']:
                    if person.get('kind') == 'person':
                        assignees.append(person.get('name', 'Unknown'))
            elif isinstance(value, list):
                for person in value:
                    if isinstance(person, dict) and person.get('name'):
                        assignees.append(person.get('name'))

    return assignees

def calculate_priority_score(item):
    """Calculate a priority score for ranking items"""
    priority = get_priority_from_item(item).lower()
    status = get_status_from_column(item).lower()
    due_date = get_due_date_from_item(item)

    score = 0

    # Priority-based scoring
    priority_scores = {
        'critical': 100,
        'urgent': 80,
        'high': 60,
        'medium': 40,
        'normal': 20,
        'low': 10
    }

    for priority_key, priority_score in priority_scores.items():
        if priority_key in priority:
            score += priority_score
            break

    # Status-based scoring
    if 'blocked' in status or 'stuck' in status:
        score += 50  # Blocked items need attention
    elif 'in progress' in status or 'working' in status:
        score += 30  # Active items maintain priority
    elif 'done' in status or 'completed' in status:
        score -= 100  # Completed items have low priority

    # Due date scoring with type safety
    if due_date and isinstance(due_date, date):
        try:
            today = datetime.now().date()
            days_until_due = (due_date - today).days

            if days_until_due < 0:  # Overdue
                score += 200
            elif days_until_due == 0:  # Due today
                score += 150
            elif days_until_due <= 3:  # Due this week
                score += 100
            elif days_until_due <= 7:  # Due next week
                score += 50
        except TypeError as e:
            # Handle any remaining type comparison issues gracefully
            print(f"⚠️  Warning: Date scoring issue for item '{item.get('name', 'Unknown')}': {e}")
            pass

    return max(score, 0)  # Ensure non-negative score

def analyze_priorities(all_items, focus_person=None):
    """Analyze and categorize items by priority"""

    # Filter by person if specified
    if focus_person:
        filtered_items = []
        for item in all_items:
            assignees = get_assignees_from_item(item)
            if any(focus_person.lower() in assignee.lower() for assignee in assignees):
                filtered_items.append(item)
        all_items = filtered_items

    # Filter out completed items
    active_items = [
        item for item in all_items
        if get_status_from_column(item).lower() not in ['done', 'completed', 'finished', 'closed']
    ]

    # Calculate priority scores and sort
    scored_items = []
    for item in active_items:
        score = calculate_priority_score(item)
        scored_items.append((score, item))

    scored_items.sort(key=lambda x: x[0], reverse=True)

    # Categorize items
    today = datetime.now().date()

    critical_items = []
    urgent_items = []
    overdue_items = []
    due_today = []
    due_this_week = []
    blocked_items = []
    high_priority = []

    for score, item in scored_items:
        priority = get_priority_from_item(item).lower()
        status = get_status_from_column(item).lower()
        due_date = get_due_date_from_item(item)

        # Categorize by various criteria
        if 'critical' in priority:
            critical_items.append((score, item))
        elif 'urgent' in priority or score >= 150:
            urgent_items.append((score, item))

        if 'blocked' in status or 'stuck' in status:
            blocked_items.append((score, item))

        if due_date:
            days_until_due = (due_date - today).days
            if days_until_due < 0:
                overdue_items.append((score, item))
            elif days_until_due == 0:
                due_today.append((score, item))
            elif days_until_due <= 7:
                due_this_week.append((score, item))

        if 'high' in priority:
            high_priority.append((score, item))

    return {
        'all_scored': scored_items,
        'critical': critical_items,
        'urgent': urgent_items,
        'overdue': overdue_items,
        'due_today': due_today,
        'due_this_week': due_this_week,
        'blocked': blocked_items,
        'high_priority': high_priority
    }

def format_item_display(score, item, show_score=False):
    """Format an item for display"""
    priority = get_priority_from_item(item)
    status = get_status_from_column(item)
    assignees = get_assignees_from_item(item)
    due_date = get_due_date_from_item(item)
    group_name = item.get('group', {}).get('title', 'Unknown')

    # Format assignees
    assignee_str = ', '.join(assignees[:2]) if assignees else 'Unassigned'
    if len(assignees) > 2:
        assignee_str += f' +{len(assignees) - 2} more'

    # Format due date with type safety
    due_str = ''
    if due_date and isinstance(due_date, date):
        try:
            today = datetime.now().date()
            days_until_due = (due_date - today).days
            if days_until_due < 0:
                due_str = f' | ⚠️  {abs(days_until_due)} days overdue'
            elif days_until_due == 0:
                due_str = ' | 📅 Due today'
            elif days_until_due <= 7:
                due_str = f' | 📅 Due in {days_until_due} days'
        except TypeError as e:
            # Fallback if date arithmetic still fails
            due_str = f' | 📅 Due: {due_date}'

    score_str = f' [{score}]' if show_score else ''

    return f"   • {item['name']}{score_str}\n     👤 {assignee_str} | 📊 {status} | 🎯 {priority} | 📁 {group_name}{due_str}"

def generate_priorities_report(client, board_ids=None, focus_person=None, limit=20):
    """Generate comprehensive priorities report"""

    title = f"🎯 Monday.com Priorities Report"
    if focus_person:
        title += f" - {focus_person}"
    title += f" - {datetime.now().strftime('%B %d, %Y')}"

    print(f"{title}\n")

    # Get all boards if none specified
    if not board_ids:
        boards = client.get_boards_with_groups()
        board_ids = [board['id'] for board in boards if board.get('state') == 'active']
        print(f"📋 Analyzing priorities across {len(board_ids)} active boards\n")
    else:
        print(f"📋 Analyzing priorities across {len(board_ids)} specified boards\n")

    # Collect data from all boards
    all_items = []

    for board_id in board_ids:
        try:
            items = client.get_board_items_paginated(board_id)
            all_items.extend(items)
        except Exception as e:
            print(f"⚠️  Warning: Could not fetch data from board {board_id}: {e}")

    if not all_items:
        print("❌ No items found in any boards")
        return

    # Analyze priorities
    priority_analysis = analyze_priorities(all_items, focus_person)

    # Report sections
    sections = [
        ('🚨 CRITICAL ITEMS', priority_analysis['critical']),
        ('⚠️  OVERDUE ITEMS', priority_analysis['overdue']),
        ('📅 DUE TODAY', priority_analysis['due_today']),
        ('🚧 BLOCKED ITEMS', priority_analysis['blocked']),
        ('🔥 URGENT ITEMS', priority_analysis['urgent']),
        ('📋 DUE THIS WEEK', priority_analysis['due_this_week']),
        ('⭐ HIGH PRIORITY', priority_analysis['high_priority'])
    ]

    for section_title, items in sections:
        if items:
            print(f"{section_title}")
            for score, item in items[:limit]:
                print(format_item_display(score, item))
            if len(items) > limit:
                print(f"   ... and {len(items) - limit} more items")
            print()

    # Top priorities summary
    print("🎖️  **TOP PRIORITIES (Overall)**")
    top_items = priority_analysis['all_scored'][:limit]
    for score, item in top_items:
        print(format_item_display(score, item, show_score=True))

    if len(priority_analysis['all_scored']) > limit:
        print(f"   ... and {len(priority_analysis['all_scored']) - limit} more items")

    print()
    print(f"📈 Report generated at {datetime.now().strftime('%I:%M %p')}")
    print(f"📊 Total active items analyzed: {len(priority_analysis['all_scored'])}")

def main():
    parser = argparse.ArgumentParser(description="Analyze Monday.com priorities and urgent items")

    # Board identification - support both IDs and names
    parser.add_argument('--board-ids', nargs='+',
                       help='Specific board IDs to analyze')
    parser.add_argument('--boards', '--board-names', dest='board_names', nargs='+',
                       help='Board names or partial board names to analyze')
    parser.add_argument('--person',
                       help='Focus analysis on specific person')
    parser.add_argument('--limit', type=int, default=20,
                       help='Maximum number of items to show per section (default: 20)')

    args = parser.parse_args()

    try:
        # Initialize API client
        client = MondayAPIClient()

        # Resolve board names to IDs if needed
        board_ids = args.board_ids
        if args.board_names:
            print(f"🔍 Resolving boards: {args.board_names}...")
            resolved_board_ids = []
            for board_name in args.board_names:
                board_info = client.resolve_board(board_name)
                resolved_board_ids.append(board_info['id'])
                print(f"✅ Found board: '{board_info['name']}' (ID: {board_info['id']})")
            board_ids = resolved_board_ids

        # Generate and display report
        generate_priorities_report(client, board_ids, args.person, args.limit)

    except MondayAPIError as e:
        print(f"❌ Monday.com API Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()