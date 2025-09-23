# Monday.com Workload Analysis

Analyze task distribution and workload balance across your construction team.

## Usage
```bash
/monday_workload [board_id]
```

## What it does
- Shows total active tasks per team member
- Identifies overdue tasks by assignee
- Highlights workload imbalances
- Helps with resource allocation decisions

## Setup Required
1. Add your Monday.com API token to environment:
   ```bash
   export MONDAY_API_TOKEN="your_api_token_here"
   ```

2. Find your board ID using `/monday_boards`

## Example Output
```
Workload Analysis:
  - John Smith: 8 tasks (2 overdue)
  - Maria Garcia: 5 tasks (0 overdue)
  - Bob Johnson: 12 tasks (1 overdue)
  - Sarah Wilson: 3 tasks (0 overdue)

⚠️  Workload Alert: Bob Johnson has significantly more tasks than others
💡 Recommendation: Consider redistributing 2-3 tasks from Bob to Sarah
```

## Use Cases
- Daily standup preparation
- Resource reallocation decisions
- Identifying team members who need support
- Preventing burnout and task bottlenecks