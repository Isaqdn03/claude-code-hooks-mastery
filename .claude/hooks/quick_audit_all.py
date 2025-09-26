#!/usr/bin/env python3
"""
Quick audit across all boards to assess overall data quality
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
        print("🔍 Quick Data Quality Assessment Across All Boards")
        print("=" * 60)

        # Get all boards
        boards = client.get_boards_with_groups()
        print(f"Found {len(boards)} boards\n")

        board_scores = []
        total_items = 0

        for board in boards[:10]:  # Test first 10 boards to avoid API limits
            try:
                items = client.get_board_items_paginated(board['id'])
                item_count = len(items)
                total_items += item_count

                if item_count == 0:
                    completion_score = 0
                    status = "🚫 Empty"
                else:
                    # Calculate completion
                    total_fields = sum(len(item['column_values']) for item in items)
                    populated_fields = sum(
                        1 for item in items
                        for col in item['column_values']
                        if col['text'] and col['text'].strip()
                    )

                    completion_score = (populated_fields / total_fields) * 100 if total_fields > 0 else 0

                    if completion_score >= 80:
                        status = "🟢 Excellent"
                    elif completion_score >= 60:
                        status = "🟡 Good"
                    elif completion_score >= 40:
                        status = "🟠 Fair"
                    else:
                        status = "🔴 Poor"

                board_scores.append(completion_score)

                print(f"📋 {board['name'][:40]:<40} | {item_count:>3} items | {completion_score:>5.1f}% | {status}")

            except Exception as e:
                print(f"❌ {board['name'][:40]:<40} | Error: {str(e)[:30]}")

        print("\n" + "=" * 60)

        # Overall assessment
        if board_scores:
            avg_score = sum(board_scores) / len(board_scores)
            print(f"📊 OVERALL SYSTEM DATA QUALITY: {avg_score:.1f}%")
            print(f"📈 Total items analyzed: {total_items}")

            # Categorize boards
            excellent = sum(1 for s in board_scores if s >= 80)
            good = sum(1 for s in board_scores if 60 <= s < 80)
            fair = sum(1 for s in board_scores if 40 <= s < 60)
            poor = sum(1 for s in board_scores if s < 40)

            print(f"\n📈 Board Quality Distribution:")
            print(f"  🟢 Excellent (80%+):  {excellent}")
            print(f"  🟡 Good (60-79%):     {good}")
            print(f"  🟠 Fair (40-59%):     {fair}")
            print(f"  🔴 Poor (<40%):       {poor}")

            print(f"\n🎯 AUTOMATION READINESS ASSESSMENT:")
            if avg_score >= 70:
                print("✅ READY for sophisticated automation and analytics")
                print("   💡 Recommended: Cash flow prediction, resource optimization, project analytics")
            elif avg_score >= 50:
                print("⚠️ PARTIAL automation possible with data quality improvements")
                print("   💡 Recommended: Simple aggregation, basic reporting, overdue alerts")
                print("   🔧 Focus on: Improving date entry, status consistency, critical field completion")
            else:
                print("🚫 NOT READY for reliable automation")
                print("   🔧 Priority: Data entry training, field completion requirements, process standardization")

            print(f"\n💭 HONEST ASSESSMENT:")
            print(f"   Your current data quality of {avg_score:.1f}% means that:")
            if avg_score < 50:
                print("   - Most sophisticated scripts I suggested earlier would FAIL or be misleading")
                print("   - Focus on data collection improvement before building automation")
                print("   - Start with simple data quality monitoring and improvement tools")
            else:
                print("   - Basic automation scripts will work but need validation")
                print("   - Sophisticated analytics need careful data validation first")
                print("   - Gradual improvement will unlock more advanced workflows")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()