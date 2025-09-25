# Monday.com Priority Analysis

Intelligent priority analysis with scoring system and multi-criteria ranking.

## Usage

### New User-Friendly Syntax (Recommended)
```bash
/monday_priorities                                    # All active boards
/monday_priorities --boards "RSR Miami" "Kitchen"    # Specific boards by name
/monday_priorities --boards "Miami Roof" --person "John Smith"  # Focus on specific person
/monday_priorities --boards "Office" --limit 30      # Show top 30 items (default: 20)
```

### Traditional ID-Based Syntax (Still Supported)
```bash
/monday_priorities --board-ids ID1 ID2               # Specific boards by ID
/monday_priorities --person "John Smith"             # Focus on specific person
/monday_priorities --limit 30                        # Show top 30 items (default: 20)
```

**Implementation:** Uses `uv run .claude/hooks/monday_priorities_impl.py`

## What it does
- **Intelligent priority scoring** based on multiple criteria
- Analyzes priority levels, due dates, and status conditions
- Categorizes items: Critical, Urgent, Overdue, Due Today, Blocked
- Shows comprehensive item details: assignees, status, group, due dates
- Calculates priority scores for objective ranking
- Identifies blocked and stuck items requiring attention
- Filters by person for individual priority lists
- **✅ FIXED:** Now properly extracts data from all column types
- **Enhanced:** Full data parsing including numbers, files, and relationships

## Setup Required
1. Add your Monday.com API token to environment:
   ```bash
   export MONDAY_API_TOKEN="your_api_token_here"
   ```

2. Find your board ID using `/monday_boards`

## Example Output
```
🎯 Monday.com Priorities Report - January 22, 2025

🚨 CRITICAL ITEMS
   • Foundation Safety Review
     👤 John Smith | 📊 In Progress | 🎯 Critical | 📁 Construction | ⚠️ 2 days overdue

⚠️ OVERDUE ITEMS
   • Building Permit Renewal
     👤 Maria Garcia | 📊 Not Started | 🎯 High | 📁 Permits | ⚠️ 1 day overdue

📅 DUE TODAY
   • Concrete Delivery Coordination
     👤 Bob Johnson | 📊 In Progress | 🎯 Urgent | 📁 Materials | 📅 Due today

🚧 BLOCKED ITEMS
   • Electrical Inspection
     👤 Sarah Wilson | 📊 Stuck | 🎯 High | 📁 Quality Control

🎖️ TOP PRIORITIES (Overall)
   • Foundation Safety Review [350]
     👤 John Smith | 📊 In Progress | 🎯 Critical | 📁 Construction | ⚠️ 2 days overdue
   • Concrete Delivery Coordination [270]
     👤 Bob Johnson | 📊 In Progress | 🎯 Urgent | 📁 Materials | 📅 Due today
```

## Use Cases
- **Weekly planning meetings** with objective priority ranking
- **Daily standups** with filtered individual priorities
- **Client status updates** with intelligent urgency assessment
- **Resource allocation** based on priority scores
- **Risk management** by identifying critical and blocked items
- **Project management** with comprehensive priority visibility

## Priority Scoring System
- **Priority Level:** Critical (100), Urgent (80), High (60), Medium (40), Normal (20), Low (10)
- **Status Conditions:** Blocked/Stuck (+50), In Progress (+30), Completed (-100)
- **Due Date Urgency:** Overdue (+200), Due Today (+150), Due This Week (+100)
- **Combined Scoring:** Multi-factor analysis for objective ranking

## Advanced Features
- **Multi-Criteria Analysis:** Combines priority, status, and timing
- **Smart Categorization:** Automatically groups by urgency type
- **Person Filtering:** Individual priority views for team members
- **Comprehensive Details:** Shows all relevant item information
- **Objective Ranking:** Numerical scores remove subjective bias