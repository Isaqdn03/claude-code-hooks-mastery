#!/usr/bin/env python3
# /// script
# dependencies = ["requests"]
# ///

"""
Debug RSR Miami Roof data to find monetary columns
"""

import sys
import os
import json
from pathlib import Path

# Add utils directory to path
utils_path = Path(__file__).parent / ".claude" / "hooks" / "utils"
sys.path.insert(0, str(utils_path))

from monday_api import MondayAPIClient, MondayAPIError

def debug_rsr_data():
    """Debug RSR Miami Roof group to find monetary information"""

    client = MondayAPIClient()
    board_id = "9767588982"  # Accounts Payable Payment Log
    rsr_group_id = "group_mktvd2kr"  # RSR Miami Roof - RSR

    print("🔍 DEBUGGING RSR MIAMI ROOF DATA")
    print("=" * 60)

    # Get column definitions for this board
    print("\n📋 BOARD COLUMN DEFINITIONS:")
    columns = client.get_board_columns(board_id)
    for col in columns:
        print(f"  • {col['id']}: '{col['title']}' (Type: {col['type']})")

        # Show settings for numeric/money columns
        if col['type'] in ['numbers', 'numeric', 'money', 'budget']:
            if col.get('settings_str'):
                try:
                    settings = json.loads(col['settings_str'])
                    print(f"    💰 Settings: {settings}")
                except:
                    pass

    # Get first few items from RSR group to see their data
    print(f"\n📊 RSR GROUP SAMPLE DATA:")
    items = client.get_board_items_paginated(board_id, [rsr_group_id])

    print(f"Total items in RSR group: {len(items)}")

    # Show detailed data for first 3 items
    for i, item in enumerate(items[:3]):
        print(f"\n🏷️  SAMPLE ITEM {i+1}: '{item['name']}'")

        for col_val in item['column_values']:
            # Only show columns that might contain financial data
            if any(keyword in col_val['id'].lower() for keyword in ['amount', 'cost', 'price', 'budget', 'money', 'pay', 'total', 'value']):
                print(f"   💰 POTENTIAL MONEY COLUMN:")
                print(f"      ID: {col_val['id']}")
                print(f"      Type: {col_val['type']}")
                print(f"      Text: {col_val['text']}")
                print(f"      Value: {col_val['value']}")

                # Try to parse JSON value
                if col_val['value'] and col_val['value'].startswith('{'):
                    try:
                        parsed = json.loads(col_val['value'])
                        print(f"      Parsed: {parsed}")
                    except:
                        pass
                print()

    # Show ALL columns for one item to see everything available
    if items:
        print(f"\n🔍 ALL COLUMNS FOR ITEM: '{items[0]['name']}'")
        for col_val in items[0]['column_values']:
            if col_val['text'] or col_val['value']:  # Only show non-empty columns
                print(f"   {col_val['id']} ({col_val['type']}): Text='{col_val['text']}' | Value='{col_val['value'][:100] if col_val['value'] else ''}'")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    try:
        debug_rsr_data()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()