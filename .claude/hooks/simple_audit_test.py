#!/usr/bin/env python3
"""
Quick Monday.com Data Quality Test
"""
# /// script
# dependencies = ["requests"]
# ///

import sys
from pathlib import Path

# Add utils directory to path
utils_path = Path(__file__).parent / "utils"
sys.path.insert(0, str(utils_path))

try:
    from monday_api import MondayAPIClient, MondayAPIError
except ImportError as e:
    print(f"❌ Error importing Monday API client: {e}")
    sys.exit(1)

def main():
    client = MondayAPIClient()

    try:
        # Test with Task Planner board
        board_id = "9730238568"
        print(f"🔍 Testing data quality on board {board_id}...")

        # Get board info
        boards = client.get_boards_with_groups([board_id])
        if not boards:
            print("❌ No board found")
            return

        board = boards[0]
        print(f"📋 Board: {board['name']} ({board.get('items_count', '?')} items)")

        # Get items
        items = client.get_board_items_paginated(board_id)
        print(f"📊 Retrieved {len(items)} items")

        if items:
            print("\n🔍 Sample item analysis:")
            item = items[0]
            print(f"Item: {item['name']}")
            print(f"Group: {item['group']['title'] if item['group'] else 'No Group'}")
            print(f"Columns: {len(item['column_values'])}")

            populated_cols = 0
            for col in item['column_values']:
                if col['text'] and col['text'].strip():
                    populated_cols += 1

            completion_rate = (populated_cols / len(item['column_values'])) * 100
            print(f"Data completion: {completion_rate:.1f}%")

            # Show column analysis
            print("\n📊 Column Analysis:")
            for col in item['column_values'][:5]:  # First 5 columns
                has_data = "✅" if (col['text'] and col['text'].strip()) else "❌"
                print(f"  {has_data} {col['id']}: {col['type']} = '{col['text'] or 'EMPTY'}'")
        else:
            print("⚠️ No items found in board")

        # Overall assessment
        if not items:
            print("\n🚫 DATA QUALITY: Cannot assess - no items found")
        elif len(items) < 5:
            print("\n⚠️ DATA QUALITY: Too few items for reliable automation")
        else:
            # Quick analysis
            total_fields = sum(len(item['column_values']) for item in items)
            populated_fields = sum(
                1 for item in items
                for col in item['column_values']
                if col['text'] and col['text'].strip()
            )

            overall_completion = (populated_fields / total_fields) * 100 if total_fields > 0 else 0
            print(f"\n📈 OVERALL DATA QUALITY: {overall_completion:.1f}%")

            if overall_completion >= 70:
                print("✅ READY for basic automation scripts")
            elif overall_completion >= 40:
                print("⚠️ LIMITED automation possible - improve data entry first")
            else:
                print("🚫 NOT READY for automation - focus on data quality improvement")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()