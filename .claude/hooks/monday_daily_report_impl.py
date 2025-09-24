#!/usr/bin/env python3
# /// script
# dependencies = ["requests"]
# ///

"""
Monday.com Daily Report Command Implementation

Generates comprehensive daily operations reports from Monday.com data.
"""

import sys
import os
import argparse
import json
from datetime import datetime, timedelta, date
from pathlib import Path
from collections import defaultdict, Counter

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
            # Try to parse JSON values (status, date, etc.)
            if column['value'].startswith('{'):
                return json.loads(column['value'])
            return column['value']
        return column.get('text', '')
    except (json.JSONDecodeError, AttributeError):
        return column.get('text', '')

def get_status_from_column(item, status_column_ids=None):
    """Extract status information from item columns"""
    if not status_column_ids:
        status_column_ids = ['status', 'status_1', 'status_2']

    for column in item.get('column_values', []):
        if column['id'] in status_column_ids or 'status' in column['id'].lower():
            value = parse_column_value(column)
            if isinstance(value, dict) and 'text' in value:
                return value['text']
            elif isinstance(value, str) and value:
                return value
    return 'Unknown'

def get_date_from_column(item, date_column_ids=None):
    """Extract date information from item columns - always returns datetime.date or None"""
    if not date_column_ids:
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

def get_priority_from_column(item, priority_column_ids=None):
    """Extract priority information from item columns"""
    if not priority_column_ids:
        priority_column_ids = ['priority', 'priority_1', 'urgency']

    for column in item.get('column_values', []):
        if column['id'] in priority_column_ids or 'priority' in column['id'].lower():
            value = parse_column_value(column)
            if isinstance(value, dict) and 'text' in value:
                return value['text']
            elif isinstance(value, str) and value:
                return value
    return 'Normal'

def is_item_updated_today(item):
    """Check if item was updated today"""
    try:
        updated_at = datetime.fromisoformat(item['updated_at'].replace('Z', '+00:00'))
        return updated_at.date() == datetime.now().date()
    except (ValueError, KeyError):
        return False

def is_item_created_today(item):
    """Check if item was created today"""
    try:
        created_at = datetime.fromisoformat(item['created_at'].replace('Z', '+00:00'))
        return created_at.date() == datetime.now().date()
    except (ValueError, KeyError):
        return False

def generate_daily_report(client, board_ids=None, include_completed=False):
    """Generate comprehensive daily report"""

    print(f"📊 Monday.com Daily Report - {datetime.now().strftime('%B %d, %Y')}\n")

    # Get all boards if none specified
    if not board_ids:
        boards = client.get_boards_with_groups()
        board_ids = [board['id'] for board in boards if board.get('state') == 'active']
        print(f"📋 Analyzing {len(board_ids)} active boards\n")
    else:
        print(f"📋 Analyzing {len(board_ids)} specified boards\n")

    # Collect data from all boards
    all_items = []
    board_summaries = {}

    for board_id in board_ids:
        try:
            items = client.get_board_items_paginated(board_id)
            board_info = client.get_boards_with_groups([board_id])[0]

            all_items.extend(items)
            board_summaries[board_id] = {
                'name': board_info['name'],
                'total_items': len(items),
                'items': items
            }

        except Exception as e:
            print(f"⚠️  Warning: Could not fetch data from board {board_id}: {e}")

    if not all_items:
        print("❌ No items found in any boards")
        return

    # Analyze data
    today = datetime.now().date()

    # Items created today
    created_today = [item for item in all_items if is_item_created_today(item)]

    # Items updated today
    updated_today = [item for item in all_items if is_item_updated_today(item)]

    # Status analysis
    status_counts = Counter()
    priority_counts = Counter()
    group_activity = defaultdict(list)

    # Due items analysis
    due_today = []
    overdue_items = []

    for item in all_items:
        # Skip completed items if not requested
        status = get_status_from_column(item)
        if not include_completed and status.lower() in ['done', 'completed', 'finished', 'closed']:
            continue

        status_counts[status] += 1
        priority_counts[get_priority_from_column(item)] += 1

        # Group activity
        if item.get('group'):
            group_activity[item['group']['title']].append(item)

        # Due date analysis with type safety
        due_date = get_date_from_column(item)
        if due_date and isinstance(due_date, date):
            try:
                if due_date == today:
                    due_today.append(item)
                elif due_date < today:
                    overdue_items.append(item)
            except TypeError as e:
                # Handle any remaining type comparison issues gracefully
                print(f"⚠️  Warning: Date comparison issue for item '{item.get('name', 'Unknown')}': {e}")
                continue

    # Generate report sections
    print("🎯 **DAILY HIGHLIGHTS**")
    print(f"   • {len(created_today)} new items created")
    print(f"   • {len(updated_today)} items updated")
    print(f"   • {len(due_today)} items due today")
    print(f"   • {len(overdue_items)} overdue items")
    print()

    # Status breakdown
    print("📈 **STATUS OVERVIEW**")
    for status, count in status_counts.most_common():
        percentage = (count / len(all_items)) * 100
        print(f"   • {status}: {count} items ({percentage:.1f}%)")
    print()

    # Priority breakdown
    if any(priority_counts.values()):
        print("🚨 **PRIORITY BREAKDOWN**")
        for priority, count in priority_counts.most_common():
            if priority != 'Normal':  # Highlight non-normal priorities
                print(f"   • {priority}: {count} items")
        print()

    # Items due today
    if due_today:
        print("📅 **DUE TODAY**")
        for item in due_today:
            status = get_status_from_column(item)
            group_name = item.get('group', {}).get('title', 'Unknown')
            print(f"   • {item['name']} ({status}) - {group_name}")
        print()

    # Overdue items
    if overdue_items:
        print("⚠️  **OVERDUE ITEMS**")
        for item in overdue_items[:10]:  # Limit to top 10
            status = get_status_from_column(item)
            due_date = get_date_from_column(item)
            group_name = item.get('group', {}).get('title', 'Unknown')

            # Safe date arithmetic
            try:
                days_overdue = (today - due_date).days if due_date and isinstance(due_date, date) else 0
                print(f"   • {item['name']} ({status}) - {days_overdue} days overdue - {group_name}")
            except TypeError as e:
                # Fallback if date arithmetic still fails
                print(f"   • {item['name']} ({status}) - overdue - {group_name}")

        if len(overdue_items) > 10:
            print(f"   ... and {len(overdue_items) - 10} more overdue items")
        print()

    # New items created today
    if created_today:
        print("✨ **NEW ITEMS TODAY**")
        for item in created_today[:10]:  # Limit to top 10
            status = get_status_from_column(item)
            group_name = item.get('group', {}).get('title', 'Unknown')
            print(f"   • {item['name']} ({status}) - {group_name}")
        if len(created_today) > 10:
            print(f"   ... and {len(created_today) - 10} more new items")
        print()

    # Board-level summaries
    print("📊 **BOARD ACTIVITY**")
    for board_id, summary in board_summaries.items():
        board_updated_today = [item for item in summary['items'] if is_item_updated_today(item)]
        board_created_today = [item for item in summary['items'] if is_item_created_today(item)]

        print(f"   🏗️ {summary['name']}")
        print(f"      • Total items: {summary['total_items']}")
        print(f"      • Created today: {len(board_created_today)}")
        print(f"      • Updated today: {len(board_updated_today)}")

    print()
    print(f"📈 Report generated at {datetime.now().strftime('%I:%M %p')}")

def main():
    parser = argparse.ArgumentParser(description="Generate Monday.com daily report")
    parser.add_argument('--board-ids', nargs='+',
                       help='Specific board IDs to include in report')
    parser.add_argument('--include-completed', action='store_true',
                       help='Include completed/done items in analysis')
    parser.add_argument('--json', action='store_true',
                       help='Output report in JSON format')

    args = parser.parse_args()

    try:
        # Initialize API client
        client = MondayAPIClient()

        # Generate and display report
        if args.json:
            # TODO: Implement JSON output format
            print("JSON output not yet implemented")
        else:
            generate_daily_report(client, args.board_ids, args.include_completed)

    except MondayAPIError as e:
        print(f"❌ Monday.com API Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()