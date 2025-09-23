# Monday.com Daily Construction Report

Generate a comprehensive daily operations report from your Monday.com project boards.

## Usage
```bash
/monday_daily_report [board_id]
```

## What it does
- Identifies overdue tasks and their severity
- Lists upcoming priorities for the next 7 days
- Analyzes workload distribution across team members
- Provides actionable recommendations for operations management

## Setup Required
1. Add your Monday.com API token to environment:
   ```bash
   export MONDAY_API_TOKEN="your_api_token_here"
   ```

2. Find your board ID using:
   ```bash
   /monday_boards
   ```

## Example Output
```
# Daily Construction Operations Report - 2025-01-22

## 🚨 OVERDUE TASKS
- **Foundation Pour - Building A** - 3 days overdue (Due: 2025-01-19)
- **Electrical Rough-In** - 1 day overdue (Due: 2025-01-21)

## 📋 UPCOMING PRIORITIES (Next 7 Days)
- 🔴 **Concrete Delivery** - Due in 1 day (2025-01-23)
- 🟡 **Framing Inspection** - Due in 4 days (2025-01-26)

## 👥 WORKLOAD DISTRIBUTION
- **John Smith**: 8 active tasks (2 overdue)
- **Maria Garcia**: 5 active tasks
- **Bob Johnson**: 12 active tasks (1 overdue)

## 💡 RECOMMENDATIONS
- **Immediate Action Required**: 2 overdue tasks need attention
- **Workload Imbalance**: Consider redistributing tasks for better balance
```