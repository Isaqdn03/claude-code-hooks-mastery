# Monday.com Priority Tasks

Show upcoming tasks that need attention in the next 7 days, perfect for weekly planning.

## Usage
```bash
/monday_priorities [board_id]
```

## What it does
- Lists tasks due in the next 7 days
- Color-codes urgency (red: ≤2 days, yellow: ≤5 days, green: >5 days)
- Sorts by due date for easy prioritization
- Excludes completed tasks

## Setup Required
1. Add your Monday.com API token to environment:
   ```bash
   export MONDAY_API_TOKEN="your_api_token_here"
   ```

2. Find your board ID using `/monday_boards`

## Example Output
```
Priority Tasks (Next 7 Days):
  - 🔴 Concrete Delivery - Due in 1 day (2025-01-23)
  - 🔴 Building Permit Renewal - Due in 2 days (2025-01-24)
  - 🟡 Framing Inspection - Due in 4 days (2025-01-26)
  - 🟡 Material Order Deadline - Due in 5 days (2025-01-27)
  - 🟢 Safety Training Session - Due in 6 days (2025-01-28)
```

## Use Cases
- Weekly planning meetings
- Client status updates
- Scheduling critical path activities
- Preventing last-minute rushes