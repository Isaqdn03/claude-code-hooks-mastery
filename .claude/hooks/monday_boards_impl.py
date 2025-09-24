#!/usr/bin/env python3
# /// script
# dependencies = ["requests"]
# ///

"""
Monday.com Boards Command Implementation

Lists all Monday.com boards accessible to your account with their IDs and group information.
"""

import sys
import os
import argparse
from pathlib import Path

# Add utils directory to path
utils_path = Path(__file__).parent / "utils"
sys.path.insert(0, str(utils_path))

try:
    from monday_api import MondayAPIClient, MondayAPIError
except ImportError as e:
    print(f"❌ Error importing Monday API client: {e}")
    print("Please ensure monday_api.py is in the utils directory")
    sys.exit(1)

def format_board_output(boards, simple_mode=False):
    """Format board data for display"""

    if not boards:
        print("📋 No Monday.com boards found")
        return

    print("📋 Available Monday.com Boards & Groups:\n")

    color_map = {
        'red': '🔴',
        'green': '🟢',
        'blue': '🔵',
        'yellow': '🟡',
        'orange': '🟠',
        'purple': '🟣',
        'black': '⚫',
        'white': '⚪',
        'pink': '🩷',
        'brown': '🤎',
        'grey': '⚪',
        'gray': '⚪'
    }

    for board in boards:
        # Board header with state indicator
        state_emoji = "🏗️" if board.get('state') == 'active' else "📦"
        print(f"{state_emoji} Board ID: {board['id']} - {board['name']}")

        if board.get('description'):
            print(f"   📝 {board['description']}")

        if not simple_mode and board.get('groups'):
            # Sort groups by position if available
            groups = sorted(board['groups'], key=lambda g: g.get('position', 0))

            for group in groups:
                color_emoji = color_map.get(group.get('color', ''), '⚪')
                print(f"   📁 Group: {group['id']} → \"{group['title']}\" ({color_emoji})")

        print()

    print(f"Found {len(boards)} boards total")

def main():
    parser = argparse.ArgumentParser(description="List Monday.com boards and groups")
    parser.add_argument('--simple', action='store_true',
                       help='List boards only (no groups)')
    parser.add_argument('--board-ids', nargs='+',
                       help='Specific board IDs to query')
    parser.add_argument('--active-only', action='store_true',
                       help='Show only active boards')

    args = parser.parse_args()

    try:
        # Initialize API client
        client = MondayAPIClient()

        # Test connection with user info
        try:
            user_info = client.get_user_info()
            print(f"🔗 Connected as: {user_info['name']} ({user_info['email']})")
            print(f"📊 Account: {user_info['account']['name']}\n")
        except Exception as e:
            print(f"⚠️  Warning: Could not fetch user info: {e}")

        # Get boards with groups
        boards = client.get_boards_with_groups(args.board_ids)

        # Filter active boards if requested
        if args.active_only:
            boards = [board for board in boards if board.get('state') == 'active']

        # Format and display output
        format_board_output(boards, args.simple)

    except MondayAPIError as e:
        print(f"❌ Monday.com API Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()