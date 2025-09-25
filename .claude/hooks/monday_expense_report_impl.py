#!/usr/bin/env python3
# /// script
# dependencies = ["requests"]
# ///

"""
Monday.com Expense Report Implementation - Extract Financial Data

Specifically designed to extract monetary information from Monday.com boards.
"""

import sys
import os
import json
import argparse
from datetime import datetime
from pathlib import Path
from collections import defaultdict

# Add utils directory to path
utils_path = Path(__file__).parent / "utils"
sys.path.insert(0, str(utils_path))

try:
    from monday_api import MondayAPIClient, MondayAPIError
except ImportError as e:
    print(f"❌ Error importing Monday API client: {e}")
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

def extract_monetary_value(column):
    """Extract monetary value from numbers column"""
    if column['type'] != 'numbers':
        return None

    # Try text first (formatted display value)
    text_value = column.get('text', '')
    if text_value:
        # Remove currency symbols and formatting
        import re
        clean_value = re.sub(r'[^\d.-]', '', text_value)
        try:
            return float(clean_value)
        except ValueError:
            pass

    # Try raw value
    raw_value = column.get('value', '')
    if raw_value:
        try:
            # Remove quotes if present
            clean_value = raw_value.strip('"')
            return float(clean_value)
        except ValueError:
            pass

    return None

def extract_service_description(item):
    """Extract service description from long_text columns"""
    for column in item.get('column_values', []):
        if column['type'] == 'long_text':
            value = parse_column_value(column)
            if isinstance(value, dict) and 'text' in value:
                return value['text']
            elif isinstance(value, str) and value:
                return value
    return 'N/A'

def extract_payment_date(item):
    """Extract payment date from date columns"""
    for column in item.get('column_values', []):
        if column['type'] == 'date':
            value = parse_column_value(column)
            if isinstance(value, dict) and 'date' in value:
                return value['date']
            elif isinstance(value, str) and value:
                return value
    return None

def extract_payment_method(item):
    """Extract payment method from dropdown columns"""
    for column in item.get('column_values', []):
        if column['type'] == 'dropdown':
            text_value = column.get('text', '')
            if text_value and text_value != 'None':
                return text_value
    return 'N/A'

def extract_files_info(item):
    """Extract file information"""
    files = []
    for column in item.get('column_values', []):
        if column['type'] == 'file':
            text_value = column.get('text', '')
            if text_value and text_value.startswith('http'):
                # Extract filename from URL
                filename = text_value.split('/')[-1] if '/' in text_value else text_value
                files.append({
                    'filename': filename,
                    'url': text_value
                })
    return files

def generate_expense_report(board_id, group_ids=None):
    """Generate comprehensive expense report with financial data"""

    client = MondayAPIClient()

    print("💰 Monday.com Expense Report Generator")
    print("=" * 60)

    # Get user info
    try:
        user_info = client.get_user_info()
        print(f"🔗 Connected as: {user_info['name']} ({user_info['email']})")
        print(f"📊 Account: {user_info['account']['name']}\n")
    except Exception as e:
        print(f"⚠️  Could not get user info: {e}\n")

    # Get board columns to understand data structure
    columns = client.get_board_columns(board_id)
    monetary_columns = [col for col in columns if col['type'] == 'numbers']

    print("💰 MONETARY COLUMNS FOUND:")
    for col in monetary_columns:
        print(f"   • {col['title']} (ID: {col['id']})")
    print()

    # Get items from specified groups
    items = client.get_board_items_paginated(board_id, group_ids)

    if not items:
        print("❌ No items found in specified board/groups")
        return

    # Extract financial data from all items
    expense_data = []
    total_amount = 0

    for item in items:
        item_data = {
            'name': item['name'],
            'group': item['group']['title'],
            'amounts': {},
            'total_amount': 0,
            'service_description': extract_service_description(item),
            'payment_date': extract_payment_date(item),
            'payment_method': extract_payment_method(item),
            'files': extract_files_info(item)
        }

        # Extract all monetary values
        for column in item.get('column_values', []):
            if column['type'] == 'numbers':
                amount = extract_monetary_value(column)
                if amount is not None:
                    # Find column title
                    col_title = next((col['title'] for col in columns if col['id'] == column['id']), column['id'])
                    item_data['amounts'][col_title] = amount
                    item_data['total_amount'] += amount

        if item_data['total_amount'] > 0:  # Only include items with monetary values
            expense_data.append(item_data)
            total_amount += item_data['total_amount']

    # Generate report
    print(f"📋 EXPENSE REPORT - {datetime.now().strftime('%B %d, %Y')}")
    print("=" * 60)

    group_totals = defaultdict(float)

    for expense in expense_data:
        group_totals[expense['group']] += expense['total_amount']

        print(f"\n💳 {expense['name']}")
        print(f"   📁 Group: {expense['group']}")
        print(f"   📝 Service: {expense['service_description']}")
        print(f"   📅 Date: {expense['payment_date'] or 'Not specified'}")
        print(f"   💳 Method: {expense['payment_method']}")

        # Show all monetary amounts
        for amount_type, amount in expense['amounts'].items():
            print(f"   💰 {amount_type}: ${amount:,.2f}")

        print(f"   🔢 Item Total: ${expense['total_amount']:,.2f}")

        # Show files if any
        if expense['files']:
            print(f"   📎 Files: {len(expense['files'])} attached")

    # Summary
    print("\n" + "=" * 60)
    print("📊 EXPENSE SUMMARY")
    print("=" * 60)

    for group, group_total in group_totals.items():
        print(f"📁 {group}: ${group_total:,.2f}")

    print(f"\n💰 GRAND TOTAL: ${total_amount:,.2f}")
    print(f"📈 Total Items: {len(expense_data)}")
    print(f"📊 Report generated at {datetime.now().strftime('%I:%M %p')}")

    return expense_data, total_amount

def main():
    parser = argparse.ArgumentParser(description='Generate Monday.com expense reports with financial data')

    # Board identification - support both ID and name
    board_group = parser.add_mutually_exclusive_group(required=True)
    board_group.add_argument('--board-id', help='Monday.com board ID (numeric)')
    board_group.add_argument('--board', '--board-name', dest='board_name', help='Board name or partial board name')

    # Group identification - support both IDs and names
    group_group = parser.add_mutually_exclusive_group()
    group_group.add_argument('--group-ids', nargs='+', help='Specific group IDs to analyze')
    group_group.add_argument('--groups', '--group-names', dest='group_names', nargs='+', help='Group names or partial group names')

    parser.add_argument('--output-json', help='Save report data as JSON file')

    args = parser.parse_args()

    try:
        # Initialize client for board/group resolution
        client = MondayAPIClient()

        # Resolve board identifier to board info
        if args.board_id:
            board_identifier = args.board_id
        else:
            board_identifier = args.board_name

        print(f"🔍 Resolving board: '{board_identifier}'...")
        board_info = client.resolve_board(board_identifier)
        board_id = board_info['id']
        print(f"✅ Found board: '{board_info['name']}' (ID: {board_id})")

        # Resolve group identifiers if provided
        group_ids = None
        if args.group_ids:
            group_ids = args.group_ids
            print(f"📁 Using group IDs: {group_ids}")
        elif args.group_names:
            print(f"🔍 Resolving groups: {args.group_names}...")
            resolved_groups = []
            for group_name in args.group_names:
                group_info = client.resolve_group(board_info, group_name)
                resolved_groups.append(group_info['id'])
                print(f"✅ Found group: '{group_info['title']}' (ID: {group_info['id']})")
            group_ids = resolved_groups

        expense_data, total_amount = generate_expense_report(board_id, group_ids)

        # Save JSON output if requested
        if args.output_json:
            output_data = {
                'generated_at': datetime.now().isoformat(),
                'board_id': board_id,
                'board_name': board_info['name'],
                'group_ids': group_ids,
                'total_amount': total_amount,
                'expenses': expense_data
            }

            with open(args.output_json, 'w') as f:
                json.dump(output_data, f, indent=2)
            print(f"\n💾 Report data saved to: {args.output_json}")

    except MondayAPIError as e:
        print(f"❌ Monday.com API Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()