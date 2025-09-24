#!/usr/bin/env python3
# /// script
# dependencies = ["requests"]
# ///

"""
Monday.com Complete Data Extractor - No Filtering, Everything As-Is

Fetches ALL data from Monday.com boards and groups exactly as it exists,
without any interpretation, filtering, or selective parsing.
"""

import sys
import os
import json
import argparse
from datetime import datetime
from pathlib import Path

# Add utils directory to path
utils_path = Path(__file__).parent / "utils"
sys.path.insert(0, str(utils_path))

try:
    from monday_api import MondayAPIClient, MondayAPIError
except ImportError as e:
    print(f"❌ Error importing Monday API client: {e}")
    sys.exit(1)

def extract_complete_board_data(board_id, group_ids=None, output_format='json'):
    """Extract ALL data from Monday.com board/groups without any filtering"""

    client = MondayAPIClient()

    print("🔍 Monday.com Complete Data Extractor")
    print("=" * 60)

    # Get user info
    try:
        user_info = client.get_user_info()
        print(f"🔗 Connected as: {user_info['name']} ({user_info['email']})")
        print(f"📊 Account: {user_info['account']['name']}\n")
    except Exception as e:
        print(f"⚠️  Could not get user info: {e}\n")

    # Get complete board information
    boards = client.get_boards_with_groups([board_id])
    if not boards:
        print(f"❌ Board {board_id} not found")
        return None

    board = boards[0]
    print(f"📋 Board: {board['name']} (ID: {board['id']})")
    print(f"📝 Description: {board.get('description', 'N/A')}")
    print(f"🏷️  State: {board.get('state', 'N/A')}")

    # Show all groups
    print(f"\n📁 Groups ({len(board['groups'])} total):")
    for group in board['groups']:
        marker = "✅" if not group_ids or group['id'] in group_ids else "⚪"
        print(f"   {marker} {group['id']}: '{group['title']}' (Color: {group.get('color', 'N/A')})")

    # Get ALL column definitions
    print(f"\n📊 Getting complete column definitions...")
    columns = client.get_board_columns(board_id)

    print(f"\n📋 ALL COLUMNS ({len(columns)} total):")
    column_lookup = {}
    for i, col in enumerate(columns, 1):
        print(f"   {i:2d}. ID: {col['id']:20s} | Title: '{col['title']:25s}' | Type: {col['type']:15s}")
        if col.get('settings_str'):
            try:
                settings = json.loads(col['settings_str'])
                if settings:
                    print(f"       Settings: {settings}")
            except:
                pass
        column_lookup[col['id']] = col

    # Get ALL items from specified groups (or all groups if none specified)
    print(f"\n📦 Fetching ALL items data...")
    items = client.get_board_items_paginated(board_id, group_ids)

    if not items:
        print("❌ No items found")
        return None

    print(f"✅ Retrieved {len(items)} items")

    # Build complete data structure
    complete_data = {
        'extraction_info': {
            'timestamp': datetime.now().isoformat(),
            'board_id': board_id,
            'group_ids': group_ids,
            'total_items': len(items),
            'extractor': 'monday_complete_data_impl.py'
        },
        'user_info': user_info,
        'board_info': board,
        'columns': columns,
        'items': []
    }

    # Process each item - extract EVERYTHING
    print(f"\n🔄 Processing items...")
    for i, item in enumerate(items, 1):
        print(f"   Processing {i}/{len(items)}: {item['name']}", end='\r')

        item_data = {
            'id': item['id'],
            'name': item['name'],
            'state': item['state'],
            'created_at': item['created_at'],
            'updated_at': item['updated_at'],
            'group': {
                'id': item['group']['id'],
                'title': item['group']['title']
            },
            'columns': {}
        }

        # Extract ALL column values without any filtering
        for col_val in item.get('column_values', []):
            column_info = column_lookup.get(col_val['id'], {})

            item_data['columns'][col_val['id']] = {
                'column_title': column_info.get('title', 'Unknown'),
                'column_type': col_val['type'],
                'text_value': col_val['text'],
                'raw_value': col_val['value'],
                'column_settings': column_info.get('settings_str')
            }

            # Try to parse JSON values but keep original
            if col_val['value'] and col_val['value'].startswith('{'):
                try:
                    item_data['columns'][col_val['id']]['parsed_value'] = json.loads(col_val['value'])
                except:
                    item_data['columns'][col_val['id']]['parsed_value'] = None

        complete_data['items'].append(item_data)

    print(f"\n✅ Processing complete!")

    # Output based on format
    if output_format == 'json':
        print(f"\n📄 COMPLETE JSON DATA:")
        print("=" * 60)
        print(json.dumps(complete_data, indent=2))

    elif output_format == 'summary':
        print(f"\n📊 DATA SUMMARY:")
        print("=" * 60)

        # Group summary
        group_counts = {}
        for item in complete_data['items']:
            group_name = item['group']['title']
            group_counts[group_name] = group_counts.get(group_name, 0) + 1

        for group_name, count in group_counts.items():
            print(f"📁 {group_name}: {count} items")

        # Column summary
        print(f"\n📋 Column Types Found:")
        column_types = {}
        for col in complete_data['columns']:
            col_type = col['type']
            column_types[col_type] = column_types.get(col_type, 0) + 1

        for col_type, count in column_types.items():
            print(f"   {col_type}: {count} columns")

        # Sample item data
        if complete_data['items']:
            print(f"\n🔍 SAMPLE ITEM DATA (First Item):")
            sample_item = complete_data['items'][0]
            print(f"Item: {sample_item['name']}")
            print(f"Group: {sample_item['group']['title']}")
            print(f"Columns ({len(sample_item['columns'])}):")

            for col_id, col_data in sample_item['columns'].items():
                print(f"   • {col_data['column_title']} ({col_data['column_type']}):")
                print(f"     Text: {col_data['text_value']}")
                if col_data['raw_value']:
                    print(f"     Raw: {col_data['raw_value'][:100]}{'...' if len(str(col_data['raw_value'])) > 100 else ''}")

    elif output_format == 'detailed':
        print(f"\n📋 DETAILED ITEM BREAKDOWN:")
        print("=" * 60)

        for item in complete_data['items']:
            print(f"\n🏷️  ITEM: {item['name']}")
            print(f"   ID: {item['id']}")
            print(f"   Group: {item['group']['title']}")
            print(f"   State: {item['state']}")
            print(f"   Created: {item['created_at']}")
            print(f"   Updated: {item['updated_at']}")
            print(f"   Columns:")

            for col_id, col_data in item['columns'].items():
                print(f"     • {col_data['column_title']} ({col_data['column_type']}):")
                print(f"       Text: {col_data['text_value']}")
                print(f"       Raw: {col_data['raw_value']}")
                if col_data.get('parsed_value'):
                    print(f"       Parsed: {col_data['parsed_value']}")

    return complete_data

def main():
    parser = argparse.ArgumentParser(description='Extract complete data from Monday.com boards without filtering')
    parser.add_argument('--board-id', required=True, help='Monday.com board ID')
    parser.add_argument('--group-ids', nargs='+', help='Specific group IDs to extract (optional - gets all if not specified)')
    parser.add_argument('--output-format', choices=['json', 'summary', 'detailed'], default='summary',
                        help='Output format: json (raw), summary (overview), detailed (full breakdown)')
    parser.add_argument('--save-json', help='Save complete JSON data to file')

    args = parser.parse_args()

    try:
        complete_data = extract_complete_board_data(
            args.board_id,
            args.group_ids,
            args.output_format
        )

        if complete_data and args.save_json:
            with open(args.save_json, 'w') as f:
                json.dump(complete_data, f, indent=2)
            print(f"\n💾 Complete data saved to: {args.save_json}")

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