#!/usr/bin/env -S uv run --quiet
# /// script
# dependencies = [
#     "gitpython",
# ]
# ///

"""
Productivity Metrics Status Line for Claude Code
Track developer productivity with code generation rate, problem resolution, commit streaks, and focus time
"""

import json
import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Optional, Tuple
import git

# ANSI color codes
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GRAY = "\033[90m"
    MAGENTA = "\033[95m"
    WHITE = "\033[97m"
    ORANGE = "\033[38;5;208m"

def get_git_metrics() -> Dict[str, Any]:
    """Get Git repository metrics."""
    metrics = {
        'commits_today': 0,
        'commits_week': 0,
        'lines_added': 0,
        'lines_removed': 0,
        'files_changed': 0,
        'commit_streak': 0,
        'last_commit_time': None,
        'branches_active': 0
    }

    try:
        repo = git.Repo('.')
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = now - timedelta(days=7)

        # Get commits for current branch
        commits = list(repo.iter_commits(max_count=100))

        # Track unique dates for streak
        commit_dates = set()

        for commit in commits:
            commit_time = datetime.fromtimestamp(commit.committed_date, tz=timezone.utc)

            # Track for streak calculation
            commit_dates.add(commit_time.date())

            if commit_time >= today_start:
                metrics['commits_today'] += 1

            if commit_time >= week_start:
                metrics['commits_week'] += 1

        # Calculate commit streak
        if commit_dates:
            sorted_dates = sorted(commit_dates, reverse=True)
            streak = 0
            expected_date = now.date()

            for date in sorted_dates:
                if date == expected_date or date == expected_date - timedelta(days=1):
                    streak += 1
                    expected_date = date - timedelta(days=1)
                else:
                    break

            metrics['commit_streak'] = streak

        # Get last commit time
        if commits:
            metrics['last_commit_time'] = datetime.fromtimestamp(
                commits[0].committed_date, tz=timezone.utc
            )

        # Get diff stats for today
        if metrics['commits_today'] > 0:
            try:
                # Get diff stats for commits made today
                today_commits = [c for c in commits if
                               datetime.fromtimestamp(c.committed_date, tz=timezone.utc) >= today_start]

                for commit in today_commits:
                    stats = commit.stats.total
                    metrics['lines_added'] += stats.get('insertions', 0)
                    metrics['lines_removed'] += stats.get('deletions', 0)
                    metrics['files_changed'] += len(commit.stats.files)
            except:
                pass

        # Count active branches (modified in last 7 days)
        for branch in repo.branches:
            try:
                last_commit = branch.commit
                commit_time = datetime.fromtimestamp(last_commit.committed_date, tz=timezone.utc)
                if commit_time >= week_start:
                    metrics['branches_active'] += 1
            except:
                pass

    except:
        pass

    return metrics

def analyze_claude_productivity() -> Dict[str, Any]:
    """Analyze Claude Code productivity metrics from logs."""
    metrics = {
        'code_generated': 0,  # Lines of code generated
        'problems_solved': 0,  # Completed tasks
        'tools_per_turn': 0,  # Average tools per conversation turn
        'error_rate': 0,  # Percentage of operations with errors
        'file_operations': 0,  # Total file read/write operations
        'focus_sessions': 0,  # Number of distinct work sessions
        'avg_response_time': 0,  # Estimated based on timestamps
    }

    logs_dir = Path("logs")
    if not logs_dir.exists():
        return metrics

    # Analyze tool usage for code generation
    tool_log = logs_dir / "pre_tool_use.json"
    if tool_log.exists():
        try:
            total_operations = 0
            error_count = 0
            code_tools = 0
            file_ops = 0

            with open(tool_log, 'r') as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())
                        total_operations += 1
                        tool_name = entry.get('tool_name', '')

                        if tool_name in ['Write', 'Edit', 'MultiEdit']:
                            code_tools += 1
                            # Estimate lines from content size
                            params = entry.get('tool_input', {})
                            if 'content' in params:
                                metrics['code_generated'] += len(params['content'].split('\n'))
                            elif 'new_string' in params:
                                metrics['code_generated'] += len(params['new_string'].split('\n'))

                        if tool_name in ['Read', 'Write', 'Edit', 'MultiEdit']:
                            file_ops += 1
                    except:
                        pass

            metrics['file_operations'] = file_ops

        except:
            pass

    # Analyze completed tasks from todo operations
    todo_operations = []
    if tool_log.exists():
        try:
            with open(tool_log, 'r') as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())
                        if entry.get('tool_name') == 'TodoWrite':
                            params = entry.get('tool_input', {})
                            todos = params.get('todos', [])
                            completed = sum(1 for t in todos if t.get('status') == 'completed')
                            if completed > 0:
                                metrics['problems_solved'] += completed
                    except:
                        pass
        except:
            pass

    # Analyze session patterns for focus time
    chat_log = logs_dir / "chat.json"
    if chat_log.exists():
        try:
            timestamps = []
            conversation_turns = 0

            with open(chat_log, 'r') as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())
                        if 'timestamp' in entry:
                            timestamp = datetime.fromisoformat(
                                entry['timestamp'].replace('Z', '+00:00')
                            )
                            timestamps.append(timestamp)

                        if entry.get('role') == 'user':
                            conversation_turns += 1
                    except:
                        pass

            # Identify focus sessions (gaps > 30 minutes = new session)
            if timestamps:
                timestamps.sort()
                sessions = 1
                for i in range(1, len(timestamps)):
                    gap = (timestamps[i] - timestamps[i-1]).total_seconds() / 60
                    if gap > 30:  # 30 minute gap = new session
                        sessions += 1

                metrics['focus_sessions'] = sessions

            # Calculate tools per turn
            if conversation_turns > 0 and total_operations > 0:
                metrics['tools_per_turn'] = round(total_operations / conversation_turns, 1)

        except:
            pass

    # Calculate error rate
    post_log = logs_dir / "post_tool_use.json"
    if post_log.exists():
        try:
            error_count = 0
            total_results = 0

            with open(post_log, 'r') as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())
                        total_results += 1
                        if entry.get('error') or 'error' in str(entry.get('result', '')).lower():
                            error_count += 1
                    except:
                        pass

            if total_results > 0:
                metrics['error_rate'] = round((error_count / total_results) * 100, 1)
        except:
            pass

    return metrics

def format_time_ago(dt: Optional[datetime]) -> str:
    """Format datetime as time ago string."""
    if not dt:
        return ""

    now = datetime.now(timezone.utc)
    diff = now - dt

    if diff.total_seconds() < 60:
        return "now"
    elif diff.total_seconds() < 3600:
        minutes = int(diff.total_seconds() / 60)
        return f"{minutes}m ago"
    elif diff.total_seconds() < 86400:
        hours = int(diff.total_seconds() / 3600)
        return f"{hours}h ago"
    else:
        days = int(diff.total_seconds() / 86400)
        return f"{days}d ago"

def get_productivity_score(git_metrics: Dict, claude_metrics: Dict) -> Tuple[int, str]:
    """Calculate overall productivity score and emoji."""
    score = 0

    # Git activity scoring
    score += min(git_metrics['commits_today'] * 10, 30)  # Max 30 points
    score += min(git_metrics['commit_streak'] * 5, 25)  # Max 25 points
    score += min(git_metrics['lines_added'] // 50, 20)  # Max 20 points

    # Claude activity scoring
    score += min(claude_metrics['problems_solved'] * 5, 15)  # Max 15 points
    score += min(claude_metrics['code_generated'] // 100, 10)  # Max 10 points

    # Penalty for errors
    if claude_metrics['error_rate'] > 10:
        score -= 5

    # Determine emoji and color
    if score >= 80:
        emoji = "🔥"
        color = Colors.RED  # Fire!
    elif score >= 60:
        emoji = "⚡"
        color = Colors.YELLOW
    elif score >= 40:
        emoji = "💪"
        color = Colors.GREEN
    elif score >= 20:
        emoji = "📈"
        color = Colors.CYAN
    else:
        emoji = "💤"
        color = Colors.GRAY

    return score, f"{color}{emoji}{Colors.RESET}"

def main():
    """Generate productivity metrics status line."""
    try:
        # Get metrics
        git_metrics = get_git_metrics()
        claude_metrics = analyze_claude_productivity()

        # Calculate productivity score
        score, emoji = get_productivity_score(git_metrics, claude_metrics)

        # Build status line components
        status_parts = []

        # Productivity indicator
        status_parts.append(f"{emoji} Productivity")

        # Commit activity
        if git_metrics['commits_today'] > 0:
            status_parts.append(f"{Colors.GREEN}📝 {git_metrics['commits_today']} commits{Colors.RESET}")
        elif git_metrics['last_commit_time']:
            time_ago = format_time_ago(git_metrics['last_commit_time'])
            status_parts.append(f"{Colors.GRAY}Last: {time_ago}{Colors.RESET}")

        # Commit streak
        if git_metrics['commit_streak'] > 0:
            streak_color = Colors.ORANGE if git_metrics['commit_streak'] >= 7 else Colors.YELLOW if git_metrics['commit_streak'] >= 3 else Colors.CYAN
            status_parts.append(f"{streak_color}🔥 {git_metrics['commit_streak']}d streak{Colors.RESET}")

        # Code generation
        if claude_metrics['code_generated'] > 0:
            if claude_metrics['code_generated'] >= 1000:
                gen_str = f"{claude_metrics['code_generated']/1000:.1f}K"
            else:
                gen_str = str(claude_metrics['code_generated'])
            status_parts.append(f"{Colors.BLUE}⚙️ {gen_str} lines{Colors.RESET}")

        # Problem solving
        if claude_metrics['problems_solved'] > 0:
            status_parts.append(f"{Colors.GREEN}✅ {claude_metrics['problems_solved']} solved{Colors.RESET}")

        # Git changes today
        if git_metrics['lines_added'] > 0 or git_metrics['lines_removed'] > 0:
            changes_str = f"{Colors.GREEN}+{git_metrics['lines_added']}{Colors.RESET}"
            if git_metrics['lines_removed'] > 0:
                changes_str += f" {Colors.RED}-{git_metrics['lines_removed']}{Colors.RESET}"
            status_parts.append(changes_str)

        # File operations
        if claude_metrics['file_operations'] > 0:
            status_parts.append(f"{Colors.CYAN}📁 {claude_metrics['file_operations']} ops{Colors.RESET}")

        # Focus sessions
        if claude_metrics['focus_sessions'] > 0:
            focus_color = Colors.MAGENTA if claude_metrics['focus_sessions'] >= 3 else Colors.BLUE
            status_parts.append(f"{focus_color}🎯 {claude_metrics['focus_sessions']} sessions{Colors.RESET}")

        # Tools efficiency
        if claude_metrics['tools_per_turn'] > 0:
            eff_color = Colors.GREEN if claude_metrics['tools_per_turn'] > 3 else Colors.YELLOW
            status_parts.append(f"{eff_color}⚡ {claude_metrics['tools_per_turn']} t/turn{Colors.RESET}")

        # Error rate warning
        if claude_metrics['error_rate'] > 5:
            status_parts.append(f"{Colors.RED}⚠ {claude_metrics['error_rate']}% errors{Colors.RESET}")

        # Score indicator
        score_color = Colors.GREEN if score >= 60 else Colors.YELLOW if score >= 30 else Colors.GRAY
        status_parts.append(f"{score_color}[{score}/100]{Colors.RESET}")

        # Join all parts
        status_line = " │ ".join(status_parts)

        # Add motivational message based on productivity
        if score >= 80:
            status_line = f"{Colors.RED}🚀 ON FIRE!{Colors.RESET} │ " + status_line
        elif score >= 60:
            status_line = f"{Colors.GREEN}💪 Great pace!{Colors.RESET} │ " + status_line
        elif git_metrics['commits_today'] == 0 and claude_metrics['code_generated'] < 50:
            status_line = f"{Colors.YELLOW}☕ Time to code?{Colors.RESET} │ " + status_line

        print(status_line)

    except Exception as e:
        # Fallback status
        print(f"{Colors.CYAN}📊 Productivity{Colors.RESET} │ {Colors.GRAY}Metrics unavailable{Colors.RESET}")

if __name__ == "__main__":
    main()