#!/usr/bin/env python3
"""
Monday.com Data Quality Auditor

Comprehensive analysis of data completeness, consistency, and quality across all boards.
Identifies gaps, inconsistencies, and opportunities for workflow automation.

Usage: uv run .claude/hooks/monday_data_auditor_impl.py [--board-ids ID1,ID2] [--detailed]

/// script
requires-python = ">=3.11"
dependencies = [
    "requests>=2.31.0",
    "rich>=13.0.0"
]
///
"""

import os
import sys
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set, Tuple
from collections import defaultdict, Counter
import argparse
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, TaskID
from rich.text import Text
from rich import box

# Add utils directory to path
utils_path = Path(__file__).parent / "utils"
sys.path.insert(0, str(utils_path))

try:
    from monday_api import MondayAPIClient, MondayAPIError
except ImportError as e:
    print(f"❌ Error importing Monday API client: {e}")
    print("Please ensure monday_api.py is in the utils directory")
    sys.exit(1)

console = Console()

class MondayDataAuditor:
    def __init__(self):
        self.api = MondayAPIClient()

        # Data quality metrics
        self.audit_results = {
            'boards_analyzed': 0,
            'items_analyzed': 0,
            'columns_analyzed': 0,
            'data_completeness': {},
            'consistency_issues': [],
            'date_quality': {},
            'status_patterns': {},
            'financial_data': {},
            'timeline_analysis': {},
            'recommendations': []
        }

    def get_all_boards(self, board_ids: Optional[List[str]] = None) -> List[Dict]:
        """Get all boards or specific boards with complete metadata"""
        try:
            return self.api.get_boards(board_ids)
        except MondayAPIError as e:
            console.print(f"[red]Error fetching boards: {e}[/red]")
            return []

    def get_board_items(self, board_id: str) -> List[Dict]:
        """Get all items from a board with column values"""
        try:
            return self.api.get_board_items_paginated(board_id)
        except MondayAPIError as e:
            console.print(f"[red]Error fetching items for board {board_id}: {e}[/red]")
            return []

    def get_column_title(self, col: Dict, board_columns: List[Dict]) -> str:
        """Get column title from column value and board metadata"""
        # Try to get title directly from column
        if 'title' in col:
            return col['title']

        # Try to match by column id with board columns
        col_id = col.get('id', '')
        for board_col in board_columns:
            if board_col['id'] == col_id:
                return board_col['title']

        # Fallback to column id
        return col_id

    def analyze_date_quality(self, column_values: List[Dict], board_columns: List[Dict]) -> Dict:
        """Analyze date field quality and consistency"""
        date_analysis = {
            'total_date_fields': 0,
            'populated_dates': 0,
            'valid_dates': 0,
            'future_dates': 0,
            'past_dates': 0,
            'date_formats': Counter(),
            'date_issues': []
        }

        date_columns = ['date', 'due_date', 'timeline', 'creation_log']
        now = datetime.now()

        for col in column_values:
            col_title = self.get_column_title(col, board_columns)
            if col['type'] in date_columns or 'date' in col_title.lower():
                date_analysis['total_date_fields'] += 1

                if col['text'] and col['text'].strip():
                    date_analysis['populated_dates'] += 1

                    # Try to parse different date formats
                    date_formats = [
                        '%Y-%m-%d',
                        '%m/%d/%Y',
                        '%d/%m/%Y',
                        '%Y-%m-%d %H:%M:%S',
                        '%m/%d/%Y %H:%M:%S'
                    ]

                    parsed_date = None
                    for fmt in date_formats:
                        try:
                            parsed_date = datetime.strptime(col['text'].strip(), fmt)
                            date_analysis['date_formats'][fmt] += 1
                            date_analysis['valid_dates'] += 1

                            if parsed_date > now:
                                date_analysis['future_dates'] += 1
                            else:
                                date_analysis['past_dates'] += 1
                            break
                        except ValueError:
                            continue

                    if not parsed_date:
                        date_analysis['date_issues'].append({
                            'column': col_title,
                            'value': col['text'],
                            'issue': 'unparseable_format'
                        })

        return date_analysis

    def analyze_financial_data(self, column_values: List[Dict]) -> Dict:
        """Analyze financial/budget data quality"""
        financial_analysis = {
            'total_financial_fields': 0,
            'populated_financial': 0,
            'valid_amounts': 0,
            'currency_patterns': Counter(),
            'amount_ranges': {'min': float('inf'), 'max': 0, 'total': 0},
            'financial_issues': []
        }

        financial_keywords = ['budget', 'cost', 'price', 'amount', 'payment', 'invoice', 'expense']

        for col in column_values:
            if (col['type'] in ['numbers', 'currency'] or
                any(keyword in col['title'].lower() for keyword in financial_keywords)):

                financial_analysis['total_financial_fields'] += 1

                if col['text'] and col['text'].strip():
                    financial_analysis['populated_financial'] += 1

                    # Extract numeric value
                    amount_text = col['text'].strip()

                    # Find currency symbols and patterns
                    currency_match = re.search(r'[$€£¥]', amount_text)
                    if currency_match:
                        financial_analysis['currency_patterns'][currency_match.group()] += 1

                    # Extract numeric amount
                    numeric_match = re.search(r'[\d,]+\.?\d*', amount_text.replace(',', ''))
                    if numeric_match:
                        try:
                            amount = float(numeric_match.group().replace(',', ''))
                            financial_analysis['valid_amounts'] += 1
                            financial_analysis['amount_ranges']['total'] += amount

                            if amount < financial_analysis['amount_ranges']['min']:
                                financial_analysis['amount_ranges']['min'] = amount
                            if amount > financial_analysis['amount_ranges']['max']:
                                financial_analysis['amount_ranges']['max'] = amount

                        except ValueError:
                            financial_analysis['financial_issues'].append({
                                'column': col['title'],
                                'value': amount_text,
                                'issue': 'invalid_numeric_format'
                            })
                    else:
                        financial_analysis['financial_issues'].append({
                            'column': col['title'],
                            'value': amount_text,
                            'issue': 'no_numeric_value_found'
                        })

        return financial_analysis

    def analyze_status_consistency(self, items: List[Dict]) -> Dict:
        """Analyze status field consistency across items"""
        status_analysis = {
            'status_columns': set(),
            'status_values': Counter(),
            'status_by_group': defaultdict(Counter),
            'inconsistent_statuses': [],
            'stale_items': []
        }

        now = datetime.now()
        stale_threshold = timedelta(days=30)

        for item in items:
            item_updated = None
            try:
                item_updated = datetime.fromisoformat(item['updated_at'].replace('Z', '+00:00'))
            except:
                pass

            # Check for stale items
            if item_updated and (now - item_updated.replace(tzinfo=None)) > stale_threshold:
                status_analysis['stale_items'].append({
                    'name': item['name'],
                    'updated_at': item['updated_at'],
                    'group': item['group']['title'] if item['group'] else 'No Group'
                })

            group_title = item['group']['title'] if item['group'] else 'No Group'

            for col in item['column_values']:
                if 'status' in col['title'].lower() or col['type'] == 'color':
                    status_analysis['status_columns'].add(col['title'])

                    if col['text']:
                        status_value = col['text'].strip()
                        status_analysis['status_values'][status_value] += 1
                        status_analysis['status_by_group'][group_title][status_value] += 1

        return status_analysis

    def calculate_completeness_score(self, items: List[Dict], columns: List[Dict]) -> Dict:
        """Calculate data completeness scores"""
        completeness = {
            'overall_score': 0,
            'column_scores': {},
            'critical_fields_score': 0,
            'empty_items': [],
            'well_populated_items': []
        }

        if not items:
            return completeness

        critical_columns = {'name', 'status', 'timeline', 'person', 'date'}

        total_fields = 0
        populated_fields = 0
        critical_fields = 0
        critical_populated = 0

        for item in items:
            item_populated_count = 0
            item_total_count = len(item['column_values'])

            for col in item['column_values']:
                total_fields += 1

                # Check if field is populated
                is_populated = bool(col['text'] and col['text'].strip())
                if is_populated:
                    populated_fields += 1
                    item_populated_count += 1

                # Track column-specific completeness
                col_id = col['title']
                if col_id not in completeness['column_scores']:
                    completeness['column_scores'][col_id] = {'total': 0, 'populated': 0}

                completeness['column_scores'][col_id]['total'] += 1
                if is_populated:
                    completeness['column_scores'][col_id]['populated'] += 1

                # Check critical fields
                if any(keyword in col['title'].lower() for keyword in critical_columns):
                    critical_fields += 1
                    if is_populated:
                        critical_populated += 1

            # Identify poorly vs well populated items
            completion_rate = item_populated_count / item_total_count if item_total_count > 0 else 0

            if completion_rate < 0.3:
                completeness['empty_items'].append({
                    'name': item['name'],
                    'completion_rate': completion_rate,
                    'group': item['group']['title'] if item['group'] else 'No Group'
                })
            elif completion_rate > 0.8:
                completeness['well_populated_items'].append({
                    'name': item['name'],
                    'completion_rate': completion_rate,
                    'group': item['group']['title'] if item['group'] else 'No Group'
                })

        # Calculate scores
        completeness['overall_score'] = (populated_fields / total_fields * 100) if total_fields > 0 else 0
        completeness['critical_fields_score'] = (critical_populated / critical_fields * 100) if critical_fields > 0 else 0

        # Calculate per-column scores
        for col_id, data in completeness['column_scores'].items():
            data['score'] = (data['populated'] / data['total'] * 100) if data['total'] > 0 else 0

        return completeness

    def audit_board(self, board: Dict) -> Dict:
        """Comprehensive audit of a single board"""
        console.print(f"🔍 Auditing Board: [bold]{board['name']}[/bold] (ID: {board['id']})")

        board_audit = {
            'board_info': board,
            'items': [],
            'completeness': {},
            'date_quality': {},
            'financial_data': {},
            'status_consistency': {},
            'issues': [],
            'recommendations': []
        }

        # Get all items
        items = self.get_board_items(board['id'])
        board_audit['items'] = items

        if not items:
            board_audit['issues'].append("Board has no items")
            return board_audit

        # Analyze completeness
        board_audit['completeness'] = self.calculate_completeness_score(items, board['columns'])

        # Analyze all column values for various metrics
        all_column_values = []
        for item in items:
            all_column_values.extend(item['column_values'])
            # Include subitem columns too
            for subitem in item.get('subitems', []):
                all_column_values.extend(subitem['column_values'])

        board_audit['date_quality'] = self.analyze_date_quality(all_column_values)
        board_audit['financial_data'] = self.analyze_financial_data(all_column_values)
        board_audit['status_consistency'] = self.analyze_status_consistency(items)

        # Generate recommendations
        board_audit['recommendations'] = self.generate_board_recommendations(board_audit)

        return board_audit

    def generate_board_recommendations(self, board_audit: Dict) -> List[str]:
        """Generate specific recommendations for improving this board"""
        recommendations = []

        completeness = board_audit['completeness']
        date_quality = board_audit['date_quality']
        financial = board_audit['financial_data']
        status = board_audit['status_consistency']

        # Completeness recommendations
        if completeness['overall_score'] < 50:
            recommendations.append("🚨 CRITICAL: Overall data completeness is very low (<50%). Consider mandatory field requirements.")
        elif completeness['overall_score'] < 70:
            recommendations.append("⚠️ Data completeness needs improvement. Focus on training team on consistent data entry.")

        if completeness['critical_fields_score'] < 80:
            recommendations.append("🎯 Critical fields (status, dates, assignments) need more consistent population.")

        # Date quality recommendations
        if date_quality['total_date_fields'] > 0:
            date_completion_rate = (date_quality['populated_dates'] / date_quality['total_date_fields']) * 100
            if date_completion_rate < 60:
                recommendations.append("📅 Many date fields are empty. Timeline tracking will be unreliable.")

            if date_quality['date_issues']:
                recommendations.append(f"📅 Found {len(date_quality['date_issues'])} date format issues. Standardize date entry format.")

        # Financial data recommendations
        if financial['total_financial_fields'] > 0:
            financial_completion = (financial['populated_financial'] / financial['total_financial_fields']) * 100
            if financial_completion < 70:
                recommendations.append("💰 Financial data is incomplete. Budget tracking and cash flow analysis will be inaccurate.")

            if len(financial['currency_patterns']) > 1:
                recommendations.append("💱 Multiple currency formats detected. Standardize currency representation.")

        # Status consistency recommendations
        if len(status['stale_items']) > 0:
            recommendations.append(f"⏰ Found {len(status['stale_items'])} items not updated in 30+ days. Review and update stale items.")

        if len(status['status_values']) > 10:
            recommendations.append("📊 Too many different status values. Consider standardizing status options.")

        # Empty items recommendations
        if completeness['empty_items']:
            recommendations.append(f"📝 {len(completeness['empty_items'])} items have very little data. Clean up or populate these items.")

        return recommendations

    def generate_global_recommendations(self) -> List[str]:
        """Generate system-wide recommendations"""
        recommendations = []

        # Analyze patterns across all boards
        total_boards = self.audit_results['boards_analyzed']
        total_items = self.audit_results['items_analyzed']

        if total_items == 0:
            recommendations.append("🚨 No items found across boards. System appears to be empty or inaccessible.")
            return recommendations

        # Check for automation readiness
        avg_completeness = sum(board_data.get('completeness', {}).get('overall_score', 0)
                             for board_data in self.audit_results['data_completeness'].values()) / max(total_boards, 1)

        if avg_completeness < 40:
            recommendations.append("🚫 AUTOMATION NOT READY: Data quality too low for reliable automation. Focus on data entry improvement first.")
        elif avg_completeness < 60:
            recommendations.append("⚠️ LIMITED AUTOMATION: Only simple scripts will work reliably. Improve data quality before advanced workflows.")
        elif avg_completeness < 80:
            recommendations.append("✅ READY FOR BASIC AUTOMATION: Simple tracking and reporting scripts will work well.")
        else:
            recommendations.append("🚀 READY FOR ADVANCED AUTOMATION: Data quality supports sophisticated workflows and analytics.")

        # Template usage recommendations
        template_boards = [name for name in self.audit_results['data_completeness'].keys() if 'template' in name.lower()]
        active_projects = [name for name in self.audit_results['data_completeness'].keys() if '2025' in name]

        if template_boards and active_projects:
            recommendations.append(f"📋 Consider enforcing template compliance across {len(active_projects)} active projects using your {len(template_boards)} templates.")

        return recommendations

    def run_audit(self, board_ids: Optional[List[str]] = None) -> Dict:
        """Run comprehensive audit across specified boards"""
        console.print("\n🔍 [bold blue]Monday.com Data Quality Audit[/bold blue]")
        console.print("=" * 60)

        # Get boards to audit
        boards = self.get_all_boards(board_ids)

        if not boards:
            console.print("[red]No boards found to audit[/red]")
            return self.audit_results

        self.audit_results['boards_analyzed'] = len(boards)

        # Progress tracking
        with Progress() as progress:
            audit_task = progress.add_task("Auditing boards...", total=len(boards))

            for board in boards:
                board_audit = self.audit_board(board)

                # Store results
                board_name = board['name']
                self.audit_results['data_completeness'][board_name] = board_audit
                self.audit_results['items_analyzed'] += len(board_audit['items'])
                self.audit_results['columns_analyzed'] += len(board.get('columns', []))

                progress.advance(audit_task)

        # Generate global recommendations
        self.audit_results['recommendations'] = self.generate_global_recommendations()

        return self.audit_results

    def display_results(self, detailed: bool = False):
        """Display audit results in rich format"""
        results = self.audit_results

        # Summary statistics
        summary_table = Table(title="📊 Audit Summary", box=box.ROUNDED)
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="green")

        summary_table.add_row("Boards Analyzed", str(results['boards_analyzed']))
        summary_table.add_row("Items Analyzed", str(results['items_analyzed']))
        summary_table.add_row("Columns Analyzed", str(results['columns_analyzed']))

        console.print(summary_table)

        # Data completeness by board
        completeness_table = Table(title="📈 Data Completeness by Board", box=box.ROUNDED)
        completeness_table.add_column("Board Name", style="cyan", max_width=40)
        completeness_table.add_column("Overall Score", style="green")
        completeness_table.add_column("Critical Fields", style="yellow")
        completeness_table.add_column("Items", style="blue")
        completeness_table.add_column("Status", style="red")

        for board_name, board_data in results['data_completeness'].items():
            completeness = board_data.get('completeness', {})
            overall_score = completeness.get('overall_score', 0)
            critical_score = completeness.get('critical_fields_score', 0)
            item_count = len(board_data.get('items', []))

            # Status indicators
            if overall_score >= 80:
                status = "🟢 Excellent"
            elif overall_score >= 60:
                status = "🟡 Good"
            elif overall_score >= 40:
                status = "🟠 Fair"
            else:
                status = "🔴 Poor"

            completeness_table.add_row(
                board_name,
                f"{overall_score:.1f}%",
                f"{critical_score:.1f}%",
                str(item_count),
                status
            )

        console.print(completeness_table)

        # Global recommendations
        if results['recommendations']:
            console.print("\n🎯 [bold]Global Recommendations[/bold]")
            for i, rec in enumerate(results['recommendations'], 1):
                console.print(f"{i}. {rec}")

        # Detailed board analysis
        if detailed:
            console.print("\n📋 [bold]Detailed Board Analysis[/bold]")
            for board_name, board_data in results['data_completeness'].items():
                if board_data.get('recommendations'):
                    console.print(f"\n[bold cyan]{board_name}[/bold cyan]")
                    for rec in board_data['recommendations']:
                        console.print(f"  • {rec}")

def main():
    parser = argparse.ArgumentParser(description="Monday.com Data Quality Auditor")
    parser.add_argument('--board-ids', help='Comma-separated board IDs to audit (default: all boards)')
    parser.add_argument('--detailed', action='store_true', help='Show detailed per-board analysis')

    args = parser.parse_args()

    board_ids = None
    if args.board_ids:
        board_ids = [bid.strip() for bid in args.board_ids.split(',')]

    auditor = MondayDataAuditor()

    try:
        results = auditor.run_audit(board_ids)
        auditor.display_results(detailed=args.detailed)

        # Offer to save results
        console.print(f"\n💾 Results saved to audit_results.json")
        with open('audit_results.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)

    except KeyboardInterrupt:
        console.print("\n[yellow]Audit cancelled by user[/yellow]")
    except Exception as e:
        console.print(f"[red]Error during audit: {e}[/red]")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()