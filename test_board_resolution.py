#!/usr/bin/env python3
# Quick test of board name resolution

import sys
from pathlib import Path

# Add utils to path
utils_path = Path(__file__).parent / ".claude/hooks/utils"
sys.path.insert(0, str(utils_path))

from monday_api import MondayAPIClient, MondayAPIError

def test_board_resolution():
    try:
        client = MondayAPIClient()
        print("🧪 Testing Board Name Resolution")
        print("=" * 40)

        # First, list some boards to see what we have
        print("\n📋 Available boards:")
        boards = client.get_boards_with_groups()[:5]  # Show first 5
        for board in boards:
            print(f"   • '{board['name']}' (ID: {board['id']})")

        if boards:
            # Test resolution with first board
            test_board = boards[0]
            print(f"\n🔍 Testing resolution with: '{test_board['name']}'")

            # Test exact name
            resolved = client.resolve_board(test_board['name'])
            print(f"✅ Exact name resolved to: '{resolved['name']}' (ID: {resolved['id']})")

            # Test partial name (first word)
            first_word = test_board['name'].split()[0]
            if len(first_word) > 2:
                try:
                    resolved_partial = client.resolve_board(first_word)
                    print(f"✅ Partial name '{first_word}' resolved to: '{resolved_partial['name']}'")
                except MondayAPIError as e:
                    print(f"ℹ️  Partial name '{first_word}' failed (expected): {e}")

        print("\n✅ Board resolution test completed!")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

    return True

if __name__ == "__main__":
    success = test_board_resolution()
    sys.exit(0 if success else 1)