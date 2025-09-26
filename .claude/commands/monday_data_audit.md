# Monday.com Data Quality Auditor

Comprehensive analysis of data completeness, consistency, and quality across all Monday.com boards. Identifies gaps, inconsistencies, and determines readiness for workflow automation.

## Usage
```bash
/monday_data_audit                    # Audit all boards
/monday_data_audit --detailed         # Detailed per-board analysis
/monday_data_audit --board-ids ID1,ID2  # Audit specific boards only
```

**Implementation:** Uses `uv run .claude/hooks/monday_data_auditor_impl.py`

## What it analyzes

### Data Completeness
- **Overall Score**: Percentage of fields populated across all items
- **Critical Fields Score**: Completion rate for essential fields (status, dates, assignments)
- **Column-Specific Scores**: Completion rates for each field type
- **Empty vs Well-Populated Items**: Identifies items needing attention

### Date Quality Analysis
- **Date Field Population**: How many date fields are actually filled
- **Date Format Consistency**: Identifies mixed date formats causing issues
- **Timeline Validity**: Future vs past dates, parsing errors
- **Critical Issues**: Unparseable dates that break workflows

### Financial Data Quality
- **Budget/Cost Field Analysis**: Completeness of financial tracking
- **Currency Consistency**: Mixed currency formats and symbols
- **Numeric Validation**: Invalid amounts and formatting issues
- **Amount Ranges**: Min/max/total financial data analysis

### Status Consistency
- **Status Standardization**: Too many different status values
- **Group-Specific Patterns**: Status usage by project phase/group
- **Stale Items**: Items not updated in 30+ days
- **Workflow Readiness**: Status field reliability for automation

## Automation Readiness Assessment

The auditor provides specific guidance on what level of automation your data supports:

| Data Quality Score | Automation Readiness | Recommended Scripts |
|-------------------|---------------------|-------------------|
| **80%+** | 🚀 **Advanced Automation Ready** | Predictive analytics, cash flow forecasting, resource optimization |
| **60-79%** | ✅ **Basic Automation Ready** | Simple tracking, basic reporting, overdue alerts |
| **40-59%** | ⚠️ **Limited Automation** | Data aggregation only, manual validation required |
| **<40%** | 🚫 **Not Ready** | Focus on data entry improvement first |

## Sample Output

```
📊 Audit Summary
┌─────────────────┬─────────┐
│ Boards Analyzed │ 25      │
│ Items Analyzed  │ 387     │
│ Columns Analyzed│ 156     │
└─────────────────┴─────────┘

📈 Data Completeness by Board
┌──────────────────────────────────────┬──────────────┬───────────────┬───────┬─────────────┐
│ Board Name                           │ Overall Score│ Critical Fields│ Items │ Status      │
├──────────────────────────────────────┼──────────────┼───────────────┼───────┼─────────────┤
│ 2025 - 145 Jefferson AVE - Millwork │ 72.3%        │ 85.1%         │ 23    │ 🟡 Good     │
│ Accounts Payable - Payment Log       │ 45.2%        │ 62.8%         │ 45    │ 🟠 Fair     │
│ Task Planner                         │ 89.1%        │ 95.2%         │ 18    │ 🟢 Excellent│
└──────────────────────────────────────┴──────────────┴───────────────┴───────┴─────────────┘

🎯 Global Recommendations
1. ✅ READY FOR BASIC AUTOMATION: Simple tracking and reporting scripts will work well.
2. 📅 Many date fields are empty across boards. Timeline tracking will be unreliable.
3. 💰 Financial data is incomplete in payment boards. Budget tracking needs improvement.
4. ⏰ Found 23 items not updated in 30+ days across all boards.
5. 📋 Consider enforcing template compliance across 6 active projects.
```

## Key Benefits

### Honest Assessment
- **No False Promises**: Tells you exactly what automation will and won't work
- **Realistic Expectations**: Based on actual data quality, not wishful thinking
- **Prioritized Improvements**: Focus on fixing the most impactful data gaps first

### Actionable Insights
- **Board-Specific Recommendations**: Targeted advice for each project board
- **Workflow Readiness**: Which processes are ready for automation
- **Data Collection Gaps**: Specific fields and patterns that need attention

### Business Value
- **ROI Assessment**: Know before you build - will automation actually work?
- **Team Training Focus**: Identify where staff need better data entry habits
- **Template Compliance**: Ensure projects follow your established workflows

## Use Cases

### Before Building Automation
- **Feasibility Check**: Will sophisticated workflows actually work with your data?
- **Scope Definition**: What level of automation is realistic right now?
- **Priority Setting**: Which boards/processes are ready first?

### Ongoing Data Health
- **Monthly Health Checks**: Track data quality improvements over time
- **Team Performance**: Identify training needs and compliance issues
- **Process Optimization**: Find workflows that need better structure

### Project Onboarding
- **New Project Setup**: Ensure new projects follow data quality standards
- **Template Validation**: Verify project boards match your templates
- **Quality Gates**: Don't let projects proceed with incomplete critical data

## Setup Required
```bash
export MONDAY_API_TOKEN="your_api_token_here"
```

## Output Files
- **audit_results.json**: Complete audit data for further analysis
- **Rich terminal output**: Color-coded results with visual indicators
- **Recommendations**: Specific, actionable improvement suggestions

This auditor is designed to give you brutal honesty about your data quality so you can make informed decisions about automation investments and data improvement priorities.