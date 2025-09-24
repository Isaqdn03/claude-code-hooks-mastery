#!/usr/bin/env python3
# /// script
# dependencies = ["requests"]
# ///

"""
Monday.com Workload Analysis Command Implementation

Analyzes team workload distribution and capacity across Monday.com boards.
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
            if column['value'].startswith('{'):
                return json.loads(column['value'])
            return column['value']
        return column.get('text', '')
    except (json.JSONDecodeError, AttributeError):
        return column.get('text', '')

def get_assignees_from_item(item):
    """Extract assigned people from item columns"""
    assignees = []

    for column in item.get('column_values', []):
        if column['type'] == 'multiple-person' or 'person' in column['id'].lower():
            value = parse_column_value(column)
            if isinstance(value, dict) and 'personsAndTeams' in value:
                for person in value['personsAndTeams']:
                    if person.get('kind') == 'person':
                        assignees.append({
                            'id': person.get('id'),
                            'name': person.get('name', 'Unknown')
                        })
            elif isinstance(value, list):
                for person in value:
                    if isinstance(person, dict) and person.get('name'):
                        assignees.append({
                            'id': person.get('id'),
                            'name': person.get('name')
                        })

    return assignees

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

def get_effort_from_item(item):
    """Extract effort/time estimate from item columns"""
    effort_columns = ['numbers', 'effort', 'hours', 'estimate', 'story_points']

    for column in item.get('column_values', []):
        if any(effort_col in column['id'].lower() for effort_col in effort_columns):
            value = parse_column_value(column)
            try:
                if isinstance(value, (int, float)):
                    return float(value)
                elif isinstance(value, str) and value.isdigit():
                    return float(value)
            except (ValueError, TypeError):
                pass

    # Default effort estimation based on item complexity
    return 1.0  # Default to 1 unit of effort

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

def calculate_workload_metrics(all_items):
    """Calculate comprehensive workload metrics"""

    # Initialize metrics
    person_workload = defaultdict(lambda: {
        'total_items': 0,
        'active_items': 0,
        'completed_items': 0,
        'overdue_items': 0,
        'total_effort': 0.0,
        'active_effort': 0.0,
        'items_by_status': defaultdict(int),
        'items_by_board': defaultdict(int),
        'upcoming_deadlines': []
    })

    today = datetime.now().date()
    next_week = today + timedelta(days=7)

    unassigned_items = []
    total_effort = 0.0
    status_distribution = Counter()

    for item in all_items:
        assignees = get_assignees_from_item(item)
        status = get_status_from_column(item)
        effort = get_effort_from_item(item)
        due_date = get_due_date_from_item(item)

        total_effort += effort
        status_distribution[status] += 1

        # Track unassigned items
        if not assignees:
            unassigned_items.append({
                'item': item,
                'effort': effort,
                'status': status,
                'due_date': due_date
            })
            continue

        # Process each assignee
        for assignee in assignees:
            person_id = assignee['id']
            person_name = assignee['name']

            # Update person's workload
            metrics = person_workload[person_name]
            metrics['total_items'] += 1
            metrics['total_effort'] += effort
            metrics['items_by_status'][status] += 1

            if item.get('group'):
                board_name = f"{item['group'].get('title', 'Unknown')}"
                metrics['items_by_board'][board_name] += 1

            # Categorize by status
            if status.lower() in ['done', 'completed', 'finished', 'closed']:
                metrics['completed_items'] += 1
            elif status.lower() not in ['stuck', 'blocked', 'on hold']:
                metrics['active_items'] += 1
                metrics['active_effort'] += effort

            # Check for overdue items with type safety
            if due_date and isinstance(due_date, date):
                try:
                    if due_date < today:
                        metrics['overdue_items'] += 1

                    # Track upcoming deadlines
                    if today <= due_date <= next_week:
                        metrics['upcoming_deadlines'].append({
                            'item_name': item['name'],
                            'due_date': due_date,
                            'effort': effort,
                            'status': status
                        })
                except TypeError as e:
                    # Handle any remaining type comparison issues gracefully
                    print(f"⚠️  Warning: Date comparison issue for item '{item.get('name', 'Unknown')}': {e}")
                    continue

    return person_workload, unassigned_items, total_effort, status_distribution

def generate_workload_report(client, board_ids=None, include_completed=False):
    """Generate comprehensive workload analysis report"""

    print(f"👥 Monday.com Workload Analysis - {datetime.now().strftime('%B %d, %Y')}\n")

    # Get all boards if none specified
    if not board_ids:
        boards = client.get_boards_with_groups()
        board_ids = [board['id'] for board in boards if board.get('state') == 'active']
        print(f"📋 Analyzing workload across {len(board_ids)} active boards\n")
    else:
        print(f"📋 Analyzing workload across {len(board_ids)} specified boards\n")

    # Collect data from all boards
    all_items = []
    board_names = {}

    for board_id in board_ids:
        try:
            items = client.get_board_items_paginated(board_id)
            board_info = client.get_boards_with_groups([board_id])[0]

            all_items.extend(items)
            board_names[board_id] = board_info['name']

        except Exception as e:
            print(f"⚠️  Warning: Could not fetch data from board {board_id}: {e}")

    if not all_items:
        print("❌ No items found in any boards")
        return

    # Filter out completed items if not requested
    if not include_completed:
        all_items = [
            item for item in all_items
            if get_status_from_column(item).lower() not in ['done', 'completed', 'finished', 'closed']
        ]

    # Calculate workload metrics
    person_workload, unassigned_items, total_effort, status_distribution = calculate_workload_metrics(all_items)

    # Generate report sections
    print("📊 **WORKLOAD OVERVIEW**")
    print(f"   • Total items analyzed: {len(all_items)}")
    print(f"   • Total effort points: {total_effort:.1f}")
    print(f"   • Team members with assignments: {len(person_workload)}")
    print(f"   • Unassigned items: {len(unassigned_items)}")
    print()

    # Team workload distribution
    if person_workload:
        print("👨‍💼 **TEAM WORKLOAD DISTRIBUTION**")

        # Sort by active effort (descending)
        sorted_workload = sorted(
            person_workload.items(),
            key=lambda x: x[1]['active_effort'],
            reverse=True
        )

        for person_name, metrics in sorted_workload:
            active_ratio = (metrics['active_effort'] / total_effort * 100) if total_effort > 0 else 0
            completion_rate = (metrics['completed_items'] / metrics['total_items'] * 100) if metrics['total_items'] > 0 else 0

            print(f"   🧑‍💻 **{person_name}**")
            print(f"      • Active items: {metrics['active_items']} ({metrics['active_effort']:.1f} effort points)")
            print(f"      • Total items: {metrics['total_items']} ({metrics['total_effort']:.1f} effort points)")
            print(f"      • Workload share: {active_ratio:.1f}% of total effort")
            print(f"      • Completion rate: {completion_rate:.1f}%")

            if metrics['overdue_items'] > 0:
                print(f"      • ⚠️  Overdue items: {metrics['overdue_items']}")

            if metrics['upcoming_deadlines']:
                print(f"      • 📅 Upcoming deadlines: {len(metrics['upcoming_deadlines'])}")
                for deadline in metrics['upcoming_deadlines'][:3]:  # Show top 3
                    days_until = (deadline['due_date'] - datetime.now().date()).days
                    print(f"        - {deadline['item_name']} ({days_until} days)")

            print()

    # Workload balance analysis
    if len(person_workload) > 1:
        print("⚖️  **WORKLOAD BALANCE ANALYSIS**")

        effort_values = [metrics['active_effort'] for metrics in person_workload.values()]
        avg_effort = sum(effort_values) / len(effort_values)
        max_effort = max(effort_values)
        min_effort = min(effort_values)

        print(f"   • Average workload: {avg_effort:.1f} effort points")
        print(f"   • Workload range: {min_effort:.1f} - {max_effort:.1f} effort points")

        if max_effort > 0:
            balance_ratio = min_effort / max_effort
            if balance_ratio < 0.5:
                print(f"   • ⚠️  Workload imbalance detected (ratio: {balance_ratio:.2f})")
            else:
                print(f"   • ✅ Workload appears balanced (ratio: {balance_ratio:.2f})")

        # Identify overloaded and underloaded team members
        overloaded = [name for name, metrics in person_workload.items()
                     if metrics['active_effort'] > avg_effort * 1.5]
        underloaded = [name for name, metrics in person_workload.items()
                      if metrics['active_effort'] < avg_effort * 0.5 and metrics['active_effort'] > 0]

        if overloaded:
            print(f"   • 📈 Potentially overloaded: {', '.join(overloaded)}")
        if underloaded:
            print(f"   • 📉 Potentially underloaded: {', '.join(underloaded)}")

        print()

    # Unassigned items
    if unassigned_items:
        print("🔍 **UNASSIGNED ITEMS**")
        total_unassigned_effort = sum(item['effort'] for item in unassigned_items)
        print(f"   • Total unassigned effort: {total_unassigned_effort:.1f} points")

        # Show high-effort unassigned items
        high_effort_unassigned = [item for item in unassigned_items if item['effort'] > 1.0]
        if high_effort_unassigned:
            print("   • High-effort unassigned items:")
            for item in sorted(high_effort_unassigned, key=lambda x: x['effort'], reverse=True)[:5]:
                print(f"     - {item['item']['name']} ({item['effort']:.1f} points, {item['status']})")

        print()

    # Status distribution
    print("📈 **STATUS DISTRIBUTION**")
    for status, count in status_distribution.most_common():
        percentage = (count / len(all_items)) * 100
        print(f"   • {status}: {count} items ({percentage:.1f}%)")

    print()
    print(f"📈 Report generated at {datetime.now().strftime('%I:%M %p')}")

def main():
    parser = argparse.ArgumentParser(description="Analyze Monday.com workload distribution")
    parser.add_argument('--board-ids', nargs='+',
                       help='Specific board IDs to analyze')
    parser.add_argument('--include-completed', action='store_true',
                       help='Include completed items in analysis')
    parser.add_argument('--person',
                       help='Focus analysis on specific person')

    args = parser.parse_args()

    try:
        # Initialize API client
        client = MondayAPIClient()

        # Generate and display report
        generate_workload_report(client, args.board_ids, args.include_completed)

    except MondayAPIError as e:
        print(f"❌ Monday.com API Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()