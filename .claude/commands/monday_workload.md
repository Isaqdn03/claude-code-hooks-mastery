# Monday.com Workload Analysis

Analyze task distribution and workload balance across your team with advanced metrics.

## Usage
```bash
/monday_workload                          # All active boards
/monday_workload --board-ids ID1 ID2     # Specific boards
/monday_workload --person "John Smith"    # Focus on specific person
/monday_workload --include-completed      # Include completed items
```

**Implementation:** Uses `uv run .claude/hooks/monday_workload_impl.py`

## What it does
- **Advanced workload metrics** with effort point analysis
- Shows total active tasks and effort distribution per team member
- Identifies overdue tasks and upcoming deadlines by assignee
- Calculates workload balance ratios and completion rates
- Highlights overloaded and underloaded team members
- Analyzes unassigned items and their effort requirements
- Provides actionable recommendations for resource allocation
- **✅ ENHANCED:** Now properly extracts all data types for comprehensive analysis
- **💡 TIP:** Combine with `/monday_complete_data` for detailed workload breakdown

## Setup Required
1. Add your Monday.com API token to environment:
   ```bash
   export MONDAY_API_TOKEN="your_api_token_here"
   ```

2. Find your board ID using `/monday_boards`

## Example Output
```
👥 Monday.com Workload Analysis - January 22, 2025

📊 **WORKLOAD OVERVIEW**
   • Total items analyzed: 72
   • Total effort points: 156.5
   • Team members with assignments: 4
   • Unassigned items: 8

👨‍💼 **TEAM WORKLOAD DISTRIBUTION**
   🧑‍💻 **John Smith**
      • Active items: 12 (24.5 effort points)
      • Total items: 15 (31.0 effort points)
      • Workload share: 28.3% of total effort
      • Completion rate: 20.0%
      • ⚠️  Overdue items: 2
      • 📅 Upcoming deadlines: 3

⚖️  **WORKLOAD BALANCE ANALYSIS**
   • Average workload: 18.2 effort points
   • Workload range: 8.5 - 24.5 effort points
   • ⚠️  Workload imbalance detected (ratio: 0.35)
   • 📈 Potentially overloaded: John Smith, Bob Johnson
   • 📉 Potentially underloaded: Sarah Wilson

🔍 **UNASSIGNED ITEMS**
   • Total unassigned effort: 12.5 points
   • High-effort unassigned items:
     - Foundation Review (3.0 points, In Progress)
     - Safety Audit (2.5 points, Not Started)
```

## Use Cases
- **Daily standup preparation** with detailed metrics
- **Resource reallocation decisions** based on effort analysis
- **Identifying team members who need support** or are overloaded
- **Preventing burnout and task bottlenecks** with balance ratios
- **Sprint planning** with capacity analysis
- **Performance reviews** with completion rate tracking

## Advanced Features
- **Effort Point Analysis:** Calculates workload based on task complexity
- **Balance Ratio Calculation:** Quantifies workload distribution fairness
- **Upcoming Deadline Tracking:** Shows deadlines within next 7 days
- **Completion Rate Metrics:** Tracks individual productivity
- **Unassigned Item Analysis:** Identifies work that needs assignment