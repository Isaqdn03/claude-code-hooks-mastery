# List Monday.com Boards And Groups

Display all Monday.com boards accessible to your account with their IDs and group information for use in other commands.

## Usage
```bash
/monday_boards           # List all boards with groups
/monday_boards --simple  # List boards only (no groups)
```

## What it does
- Lists all boards you have access to
- Shows board IDs needed for other Monday.com commands
- **NEW:** Displays all groups within each board with their IDs
- Shows group colors and organization
- Provides comprehensive project structure overview

## Setup Required
Add your Monday.com API token to environment:
```bash
export MONDAY_API_TOKEN="your_api_token_here"
```

## Example Output
```
📋 Available Monday.com Boards & Groups:

🏗️ Board ID: 9767588982 - Accounts Payable - Payment Log
   📁 Group: topics → "216 NE 14TH - Mark Grimmel" (🟢)
   📁 Group: group_mktvd2kr → "RSR Miami Roof - RSR" (🟡)
   📁 Group: group_mkttzx99 → "16431 Maddalena Pl - Lawrence Shulman" (⚫)
   📁 Group: group_mktvrjc5 → "220 Macfarlane DR - Bob Nash" (🔵)

🏢 Board ID: 9690081901 - Signed Projects
   📁 Group: topics → "Active Projects" (🟢)
   📁 Group: group_abc123 → "Completed Projects" (🔴)
```

## Enhanced Features
- **Group IDs:** Essential for targeted queries within specific project groups
- **Visual Indicators:** Color-coded groups for easy identification
- **Project Organization:** See how projects are structured within boards
- **Complete Reference:** All IDs needed for Monday.com API integration

## Use Cases
- Target specific project groups in reports
- Filter data by project phases or categories
- Build project-specific dashboards
- Automate workflows for specific groups

## API Integration
Use board and group IDs together:
```graphql
query {
  boards(ids: [BOARD_ID]) {
    groups(ids: [GROUP_ID]) {
      items {
        name
        column_values { text }
      }
    }
  }
}
```

## Getting Your API Token
1. Go to Monday.com → Profile → Admin → API
2. Generate a new token with appropriate permissions
3. Copy the token to your environment variables