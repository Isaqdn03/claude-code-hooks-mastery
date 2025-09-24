# Monday.com Daily Report

Generate a comprehensive daily operations report from your Monday.com project boards.

## Usage
```bash
/monday_daily_report                           # All active boards
/monday_daily_report --board-ids ID1 ID2      # Specific boards
/monday_daily_report --include-completed       # Include completed items
```

**Implementation:** Uses `uv run .claude/hooks/monday_daily_report_impl.py`

## What it does
- **Real-time data analysis** from Monday.com API
- Identifies overdue tasks and their severity
- Shows items created and updated today
- Lists items due today and upcoming deadlines
- Analyzes status distribution across all projects
- Provides priority breakdown with actionable insights
- Board-level activity summaries with detailed metrics

## Setup Required
1. Add your Monday.com API token to environment:
   ```bash
   export MONDAY_API_TOKEN="your_api_token_here"
   ```

2. Find your board ID using:
   ```bash
   /monday_boards
   ```

## Enhanced Features
- **Smart Date Parsing:** Automatically detects and parses various date formats
- **Priority Analysis:** Identifies high-priority and urgent items
- **Status Intelligence:** Recognizes completed vs active items automatically
- **Board Aggregation:** Combines data from multiple boards seamlessly
- **Real-time Metrics:** Live data directly from Monday.com with proper error handling
- **⚠️ KNOWN ISSUE:** Date comparison error in implementation (being addressed)
- **💡 Alternative:** Use `/monday_complete_data` or `/monday_expense_report` for reliable data extraction

## Example Output
```
📊 Monday.com Daily Report - January 22, 2025

🎯 **DAILY HIGHLIGHTS**
   • 3 new items created
   • 12 items updated
   • 5 items due today
   • 2 overdue items

📈 **STATUS OVERVIEW**
   • In Progress: 45 items (62.5%)
   • Done: 18 items (25.0%)
   • Stuck: 5 items (6.9%)
   • Not Started: 4 items (5.6%)

⚠️  **OVERDUE ITEMS**
   • Foundation Pour - Building A (In Progress) - 3 days overdue - Construction
   • Electrical Rough-In (Not Started) - 1 day overdue - Engineering

📅 **DUE TODAY**
   • Concrete Delivery (In Progress) - Construction
   • Safety Inspection (Not Started) - Quality Control

📊 **BOARD ACTIVITY**
   🏗️ Construction Projects
      • Total items: 28
      • Created today: 2
      • Updated today: 8
```