#!/usr/bin/env -S uv run --quiet
# /// script
# dependencies = []
# ///

"""
Claude Conversation Status Line for Claude Code
Track conversation analytics including token usage, tool calls, agent activity, and session metrics
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

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

def get_global_session_path() -> Path:
    """Get the global Claude session data path."""
    return Path.home() / ".claude" / "data" / "sessions"

def get_current_session() -> Optional[Dict[str, Any]]:
    """Load the current Claude Code session data."""
    session_dir = get_global_session_path()

    if not session_dir.exists():
        return None

    # Find the most recent session file
    session_files = list(session_dir.glob("session_*.json"))
    if not session_files:
        return None

    # Sort by modification time to get the most recent
    latest_session = max(session_files, key=lambda p: p.stat().st_mtime)

    try:
        with open(latest_session, 'r') as f:
            return json.load(f)
    except:
        return None

def analyze_conversation_logs() -> Dict[str, Any]:
    """Analyze conversation logs for metrics."""
    stats = {
        'tool_calls': {},
        'total_tool_calls': 0,
        'agent_calls': 0,
        'errors': 0,
        'files_read': 0,
        'files_written': 0,
        'bash_commands': 0,
        'web_searches': 0,
        'tokens_estimate': 0,
        'conversation_turns': 0
    }

    # Check local logs directory
    logs_dir = Path("logs")
    if logs_dir.exists():
        # Analyze pre_tool_use.json for tool usage
        tool_log = logs_dir / "pre_tool_use.json"
        if tool_log.exists():
            try:
                with open(tool_log, 'r') as f:
                    # Try to parse as JSON array first
                    content = f.read()
                    try:
                        entries = json.loads(content)
                        if isinstance(entries, list):
                            for entry in entries:
                                tool_name = entry.get('tool_name', 'Unknown')
                                stats['tool_calls'][tool_name] = stats['tool_calls'].get(tool_name, 0) + 1
                                stats['total_tool_calls'] += 1

                                # Categorize tools
                                if tool_name == 'Task':
                                    stats['agent_calls'] += 1
                                elif tool_name == 'Read':
                                    stats['files_read'] += 1
                                elif tool_name in ['Write', 'Edit', 'MultiEdit']:
                                    stats['files_written'] += 1
                                elif tool_name == 'Bash':
                                    stats['bash_commands'] += 1
                                elif tool_name in ['WebSearch', 'WebFetch']:
                                    stats['web_searches'] += 1
                    except json.JSONDecodeError:
                        # Fallback to line-by-line parsing
                        lines = content.strip().split('\n')
                        for line in lines:
                            try:
                                entry = json.loads(line.strip())
                                tool_name = entry.get('tool_name', 'Unknown')
                                stats['tool_calls'][tool_name] = stats['tool_calls'].get(tool_name, 0) + 1
                                stats['total_tool_calls'] += 1

                                # Categorize tools
                                if tool_name == 'Task':
                                    stats['agent_calls'] += 1
                                elif tool_name == 'Read':
                                    stats['files_read'] += 1
                                elif tool_name in ['Write', 'Edit', 'MultiEdit']:
                                    stats['files_written'] += 1
                                elif tool_name == 'Bash':
                                    stats['bash_commands'] += 1
                                elif tool_name in ['WebSearch', 'WebFetch']:
                                    stats['web_searches'] += 1
                            except:
                                pass
            except:
                pass

        # Check for errors in post_tool_use.json
        post_log = logs_dir / "post_tool_use.json"
        if post_log.exists():
            try:
                with open(post_log, 'r') as f:
                    content = f.read()
                    try:
                        entries = json.loads(content)
                        if isinstance(entries, list):
                            for entry in entries:
                                if entry.get('error') or 'error' in str(entry.get('result', '')).lower():
                                    stats['errors'] += 1
                    except json.JSONDecodeError:
                        # Fallback to line-by-line parsing
                        for line in content.strip().split('\n'):
                            try:
                                entry = json.loads(line.strip())
                                if entry.get('error') or 'error' in str(entry.get('result', '')).lower():
                                    stats['errors'] += 1
                            except:
                                pass
            except:
                pass

        # Analyze chat.json for conversation turns and estimate tokens
        chat_log = logs_dir / "chat.json"
        if chat_log.exists():
            try:
                with open(chat_log, 'r') as f:
                    content = f.read()
                    try:
                        entries = json.loads(content)
                        if isinstance(entries, list):
                            for entry in entries:
                                role = entry.get('role', '')
                                content_text = entry.get('content', '')

                                if role == 'user':
                                    stats['conversation_turns'] += 1

                                # Rough token estimate (4 chars = 1 token)
                                stats['tokens_estimate'] += len(content_text) // 4
                    except json.JSONDecodeError:
                        # Fallback to line-by-line parsing
                        for line in content.strip().split('\n'):
                            try:
                                entry = json.loads(line.strip())
                                role = entry.get('role', '')
                                content_text = entry.get('content', '')

                                if role == 'user':
                                    stats['conversation_turns'] += 1

                                # Rough token estimate (4 chars = 1 token)
                                stats['tokens_estimate'] += len(content_text) // 4
                            except:
                                pass
            except:
                pass

    return stats

def format_tool_distribution(tool_calls: Dict[str, int]) -> str:
    """Format tool call distribution."""
    if not tool_calls:
        return ""

    # Get top 3 most used tools
    sorted_tools = sorted(tool_calls.items(), key=lambda x: x[1], reverse=True)[:3]

    parts = []
    for tool, count in sorted_tools:
        # Shorten tool names
        short_name = tool[:4] if len(tool) > 4 else tool
        parts.append(f"{short_name}:{count}")

    return " ".join(parts)

def format_tokens(tokens: int) -> str:
    """Format token count with appropriate units."""
    if tokens < 1000:
        return f"{tokens}"
    elif tokens < 1000000:
        return f"{tokens/1000:.1f}K"
    else:
        return f"{tokens/1000000:.1f}M"

def get_session_duration() -> Optional[str]:
    """Calculate session duration from logs."""
    logs_dir = Path("logs")
    if not logs_dir.exists():
        return None

    # Find earliest and latest timestamps
    earliest = None
    latest = None

    for log_file in logs_dir.glob("*.json"):
        try:
            with open(log_file, 'r') as f:
                content = f.read()
                try:
                    # Try to parse as JSON array
                    entries = json.loads(content)
                    if isinstance(entries, list):
                        for entry in entries:
                            timestamp_str = entry.get('timestamp')
                            if timestamp_str:
                                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                                if earliest is None or timestamp < earliest:
                                    earliest = timestamp
                                if latest is None or timestamp > latest:
                                    latest = timestamp
                except json.JSONDecodeError:
                    # Fallback to line-by-line parsing
                    for line in content.strip().split('\n'):
                        try:
                            entry = json.loads(line.strip())
                            timestamp_str = entry.get('timestamp')
                            if timestamp_str:
                                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                                if earliest is None or timestamp < earliest:
                                    earliest = timestamp
                                if latest is None or timestamp > latest:
                                    latest = timestamp
                        except:
                            pass
        except:
            pass

    if earliest and latest:
        duration = latest - earliest
        hours = duration.total_seconds() / 3600
        if hours < 1:
            minutes = duration.total_seconds() / 60
            return f"{minutes:.0f}m"
        else:
            return f"{hours:.1f}h"

    return None

def main():
    """Generate Claude conversation analytics status line."""
    try:
        # Load session data
        session = get_current_session()

        # Analyze conversation logs
        stats = analyze_conversation_logs()

        # Get session duration
        duration = get_session_duration()

        # Build status line components
        status_parts = []

        # Session indicator
        if session:
            agent_name = session.get('agent_name', 'claude')
            status_parts.append(f"{Colors.CYAN}🤖 {agent_name}{Colors.RESET}")
        else:
            status_parts.append(f"{Colors.CYAN}🤖 Claude{Colors.RESET}")

        # Conversation metrics
        if stats['conversation_turns'] > 0:
            status_parts.append(f"{Colors.WHITE}{stats['conversation_turns']} turns{Colors.RESET}")

        # Token usage
        if stats['tokens_estimate'] > 0:
            token_color = Colors.RED if stats['tokens_estimate'] > 100000 else Colors.YELLOW if stats['tokens_estimate'] > 50000 else Colors.GREEN
            status_parts.append(f"{token_color}~{format_tokens(stats['tokens_estimate'])} tokens{Colors.RESET}")

        # Tool usage summary
        if stats['total_tool_calls'] > 0:
            status_parts.append(f"{Colors.BLUE}🔧 {stats['total_tool_calls']} tools{Colors.RESET}")

            # Specific tool highlights
            if stats['agent_calls'] > 0:
                status_parts.append(f"{Colors.MAGENTA}👥 {stats['agent_calls']} agents{Colors.RESET}")

            if stats['files_read'] > 0 or stats['files_written'] > 0:
                file_str = f"{Colors.GREEN}📄"
                if stats['files_read'] > 0:
                    file_str += f" R:{stats['files_read']}"
                if stats['files_written'] > 0:
                    file_str += f" W:{stats['files_written']}"
                file_str += Colors.RESET
                status_parts.append(file_str)

            if stats['bash_commands'] > 0:
                status_parts.append(f"{Colors.YELLOW}$ {stats['bash_commands']} cmds{Colors.RESET}")

            if stats['web_searches'] > 0:
                status_parts.append(f"{Colors.CYAN}🔍 {stats['web_searches']} web{Colors.RESET}")

        # Errors indicator
        if stats['errors'] > 0:
            status_parts.append(f"{Colors.RED}⚠ {stats['errors']} errors{Colors.RESET}")

        # Session duration
        if duration:
            status_parts.append(f"{Colors.GRAY}⏱ {duration}{Colors.RESET}")

        # Tool distribution (compact)
        tool_dist = format_tool_distribution(stats['tool_calls'])
        if tool_dist:
            status_parts.append(f"{Colors.GRAY}[{tool_dist}]{Colors.RESET}")

        # Efficiency indicators
        if stats['total_tool_calls'] > 0 and stats['conversation_turns'] > 0:
            efficiency = stats['total_tool_calls'] / stats['conversation_turns']
            if efficiency > 10:
                status_parts.insert(1, f"{Colors.GREEN}⚡ High activity{Colors.RESET}")
            elif efficiency < 2:
                status_parts.insert(1, f"{Colors.YELLOW}💭 Discussion mode{Colors.RESET}")

        # Join all parts
        status_line = " │ ".join(status_parts)

        # Add alerts for high resource usage
        if stats['tokens_estimate'] > 100000:
            status_line = f"{Colors.RED}📊 HIGH TOKEN USE{Colors.RESET} │ " + status_line
        elif stats['errors'] > 5:
            status_line = f"{Colors.YELLOW}⚠ ERRORS DETECTED{Colors.RESET} │ " + status_line

        print(status_line)

    except Exception as e:
        # Fallback status
        print(f"{Colors.CYAN}🤖 Claude{Colors.RESET} │ {Colors.GRAY}Session data unavailable{Colors.RESET}")

if __name__ == "__main__":
    main()