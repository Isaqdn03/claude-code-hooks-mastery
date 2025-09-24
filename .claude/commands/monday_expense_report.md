# Monday.com Expense Report Generator

Generate comprehensive expense reports with actual financial data extracted from Monday.com boards. Specifically designed to parse monetary values and create detailed financial analysis.

## Usage
```bash
/monday_expense_report --board-id BOARD_ID                           # Generate expense report for entire board
/monday_expense_report --board-id BOARD_ID --group-ids GROUP1 GROUP2 # Report for specific groups
/monday_expense_report --board-id BOARD_ID --output-json report.json # Save detailed JSON data
```

**Implementation:** Uses `uv run .claude/hooks/monday_expense_report_impl.py`

## What it does
- **Extracts Monetary Values:** Finds and parses all `numbers` type columns with financial data
- **Service Categorization:** Groups expenses by service descriptions and vendors
- **Payment Analysis:** Shows payment methods, dates, and patterns
- **File Documentation:** Lists attached receipts and supporting documents
- **Financial Summaries:** Calculates totals, averages, and category breakdowns
- **Vendor Tracking:** Links expenses to vendor/subcontractor relationships

## Example Output

```
💰 Monday.com Expense Report Generator
============================================================
🔗 Connected as: Isaque Nascimento (nascimentoisaque2403@gmail.com)
📊 Account: nascimentoisaque2403's Team

💰 MONETARY COLUMNS FOUND:
   • Payment Amount (ID: numeric_mktka24y)

📋 EXPENSE REPORT - September 23, 2025
============================================================

💳 Payment 1
   📁 Group: RSR Miami Roof - RSR
   📝 Service: City Fee
   📅 Date: 2025-08-16
   💳 Method: Wire
   💰 Payment Amount: $9,463.45
   🔢 Item Total: $9,463.45
   📎 Files: 1 attached

💳 Payment 2
   📁 Group: RSR Miami Roof - RSR
   📝 Service: Materials - Express Roofing Supply
   📅 Date: 2025-08-19
   💳 Method: Wire
   💰 Payment Amount: $153,379.67
   🔢 Item Total: $153,379.67
   📎 Files: 3 attached

============================================================
📊 EXPENSE SUMMARY
============================================================
📁 RSR Miami Roof - RSR: $278,872.33

💰 GRAND TOTAL: $278,872.33
📈 Total Items: 27
📊 Report generated at 04:26 PM
```

## Key Features

### Financial Data Extraction
- **Numbers Column Parsing**: Automatically finds monetary columns
- **Multiple Currency Support**: Handles different number formats
- **Calculation Fields**: Processes sum functions and totals
- **Decimal Precision**: Maintains exact financial amounts

### Expense Categorization
- **Service Grouping**: Groups by service description patterns
- **Vendor Analysis**: Links expenses to vendor relationships
- **Payment Method Tracking**: Categorizes by Wire, Card, Check, etc.
- **Date Range Analysis**: Shows spending patterns over time

### Documentation Tracking
- **Receipt Management**: Lists all attached files
- **Audit Trail**: Shows creation and modification dates
- **File Metadata**: Includes asset IDs and file types
- **Compliance Ready**: Full documentation for financial audits

### Summary Analytics
- **Category Totals**: Spending by service type
- **Payment Method Distribution**: Breakdown by payment type
- **Time-based Analysis**: Spending patterns by date
- **Vendor Summaries**: Total spending per contractor

## Advanced Features

### Multi-Board Support
```bash
# Compare expenses across multiple projects
/monday_expense_report --board-id 9767588982 --group-ids group_mktvd2kr --output-json rsr.json
/monday_expense_report --board-id 9664844405 --output-json kitchen.json
```

### Category Analysis
Automatically categorizes expenses by patterns:
- **Materials**: Roofing supplies, equipment, parts
- **Labor**: Contractor payments, hourly work
- **Equipment**: Rentals, tools, machinery
- **Services**: Permits, inspections, consulting
- **Waste Management**: Dumpsters, disposal, cleanup

### File Integration
- **Receipt Tracking**: Links monetary amounts to supporting documents
- **Image Support**: Handles photo receipts and invoices
- **PDF Processing**: Manages formal invoices and contracts
- **Asset Management**: Tracks file versions and modifications

## Use Cases
- **Project Cost Analysis**: Total project expenses with breakdowns
- **Budget Monitoring**: Track spending against allocations
- **Vendor Management**: Analyze contractor and supplier costs
- **Tax Preparation**: Export expense data for accounting
- **Cash Flow Analysis**: Monitor payment timing and methods
- **Audit Preparation**: Complete expense documentation

## Output Formats

### Console Report
Formatted expense breakdown with summaries and totals

### JSON Export
Complete structured data for integration with accounting systems:
```json
{
  "generated_at": "2025-09-23T16:26:00.000Z",
  "board_id": "9767588982",
  "total_amount": 278872.33,
  "expenses": [
    {
      "name": "Payment 1",
      "amounts": {"Payment Amount": 9463.45},
      "service_description": "City Fee",
      "payment_date": "2025-08-16",
      "payment_method": "Wire",
      "files": [...]
    }
  ]
}
```

## Performance
- **Fast Processing**: Optimized for large expense datasets
- **Memory Efficient**: Handles boards with hundreds of transactions
- **Error Resilient**: Continues processing if individual items fail
- **Caching Support**: Reuses API calls for better performance

## Setup Required
Add your Monday.com API token to environment:
```bash
export MONDAY_API_TOKEN="your_api_token_here"
```

## Integration Examples

### RSR Miami Roof Project
```bash
/monday_expense_report --board-id 9767588982 --group-ids group_mktvd2kr
```

### All Project Expenses
```bash
/monday_expense_report --board-id 9767588982
```

### Export for Accounting
```bash
/monday_expense_report --board-id 9767588982 --output-json monthly_expenses.json
```

This command transforms Monday.com data into actionable financial insights with real monetary values and comprehensive expense analysis.