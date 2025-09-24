# Monday.com Complete Data Extractor

Extract ALL data from Monday.com boards and groups exactly as-is, without any filtering or interpretation. Gets complete raw data structure including all column types, metadata, and relationships.

## Usage
```bash
/monday_complete_data --board-id BOARD_ID                           # Extract all data from board
/monday_complete_data --board-id BOARD_ID --group-ids GROUP1 GROUP2 # Extract specific groups
/monday_complete_data --board-id BOARD_ID --output-format json      # Raw JSON output
/monday_complete_data --board-id BOARD_ID --output-format detailed  # Full breakdown
/monday_complete_data --board-id BOARD_ID --save-json data.json     # Save to file
```

**Implementation:** Uses `uv run .claude/hooks/monday_complete_data_impl.py`

## What it does
- **NO FILTERING:** Extracts every piece of data exactly as it exists in Monday.com
- **All Column Types:** numbers, text, dates, dropdowns, files, board relations, mirrors
- **Complete Metadata:** Board info, groups, column settings, user information
- **Raw + Parsed Values:** Both original Monday.com data and parsed JSON structures
- **Full Audit Trail:** Creation dates, update timestamps, change tracking
- **Relationship Data:** Board connections, linked items, vendor relationships
- **File Assets:** Complete file information with asset IDs and URLs

## Output Formats

### Summary (Default)
```
📊 DATA SUMMARY:
📁 RSR Miami Roof - RSR: 30 items
📋 Column Types Found:
   numbers: 1 columns
   long_text: 1 columns
   date: 1 columns
   dropdown: 1 columns
   file: 1 columns
   board_relation: 2 columns
   mirror: 1 columns
```

### Detailed
Shows complete breakdown of every item with all column data, raw values, and parsed structures.

### JSON
Complete raw data export in structured JSON format for unlimited analysis and processing.

## Key Features

### Complete Data Structure
```json
{
  "extraction_info": {
    "timestamp": "2025-09-23T16:30:16.598770",
    "board_id": "9767588982",
    "total_items": 30
  },
  "board_info": {...},
  "columns": [...],
  "items": [
    {
      "columns": {
        "numeric_mktka24y": {
          "column_title": "Payment Amount",
          "column_type": "numbers",
          "text_value": "9463.45",
          "raw_value": "\"9463.45\"",
          "column_settings": "{\"function\":\"sum\"}"
        }
      }
    }
  ]
}
```

### All Column Types Supported
- **numbers**: Financial data, quantities, calculations
- **long_text**: Descriptions, notes, detailed information
- **date**: Payment dates, deadlines, milestones
- **dropdown**: Categories, payment methods, status values
- **file**: Receipts, documents, images with full metadata
- **board_relation**: Links to vendors, projects, phases
- **mirror**: Reflected data from connected boards

### Relationship Tracking
- **Vendor Links**: Connected to vendor/subcontractor boards
- **Project Phases**: Links to project management boards
- **Change History**: Full audit trail with timestamps
- **Asset Management**: File attachments with creation dates

## Use Cases
- **Financial Analysis**: Extract complete payment and expense data
- **Audit Compliance**: Full data export with change tracking
- **Data Migration**: Complete board export for system transfers
- **Custom Reporting**: Raw data for specialized analysis tools
- **API Integration**: Feed data to external systems
- **Backup & Archive**: Complete data preservation

## Advanced Features
- **Pagination Handling**: Retrieves all items regardless of board size
- **Error Recovery**: Robust retry logic for large datasets
- **Memory Efficient**: Streams large datasets without memory issues
- **Type Preservation**: Maintains original data types and formats
- **Metadata Rich**: Includes all Monday.com internal identifiers

## Examples

### Extract RSR Project Data
```bash
/monday_complete_data --board-id 9767588982 --group-ids group_mktvd2kr --save-json rsr_data.json
```

### View All Board Structure
```bash
/monday_complete_data --board-id 9767588982 --output-format detailed
```

### Quick Summary
```bash
/monday_complete_data --board-id 9767588982
```

## Setup Required
Add your Monday.com API token to environment:
```bash
export MONDAY_API_TOKEN="your_api_token_here"
```

## Performance Notes
- Large boards (1000+ items) may take 30-60 seconds
- JSON output can be substantial for complex boards
- Use specific group filtering for faster extraction
- Save to file for large datasets to avoid terminal limits

This command gives you **everything** - no interpretation, no filtering, just pure Monday.com data exactly as it exists.