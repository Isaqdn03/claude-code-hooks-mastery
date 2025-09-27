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

def get_local_session_path() -> Path:
    """Get the local Claude session data path for this project instance."""
    return Path(".claude/data/sessions")

def get_current_session(session_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Load the current Claude Code session data."""
    session_dir = get_local_session_path()

    if not session_dir.exists():
        return None

    # If session_id provided, load that specific session
    if session_id:
        session_file = session_dir / f"{session_id}.json"
        if session_file.exists():
            try:
                with open(session_file, 'r') as f:
                    return json.load(f)
            except:
                pass

    # Fallback: Find the most recent session file
    session_files = list(session_dir.glob("*.json"))
    if not session_files:
        return None

    # Sort by modification time to get the most recent
    latest_session = max(session_files, key=lambda p: p.stat().st_mtime)

    try:
        with open(latest_session, 'r') as f:
            return json.load(f)
    except:
        return None

def get_model_context_limit(model: str = "claude-3-5-sonnet") -> int:
    """Get context window limit for the specified model."""
    model_limits = {
        # Current generation models
        'claude-sonnet-4': 200000,
        'claude-3-5-sonnet': 200000,
        'claude-3-5-haiku': 200000,
        # Legacy models
        'claude-3-haiku': 200000,
        'claude-3-opus': 200000,
        'claude-3-sonnet': 200000,
        # Shorthand names
        'sonnet-4': 200000,
        'sonnet': 200000,
        'haiku': 200000,
        'opus': 200000
    }

    # Normalize model name for matching
    model_lower = model.lower()

    # Check for exact matches first
    if model_lower in model_limits:
        return model_limits[model_lower]

    # Check for partial matches
    for known_model in model_limits:
        if known_model in model_lower:
            return model_limits[known_model]

    # Default to 200k for all Claude models
    return 200000

def parse_context_usage_from_transcript(session_id: Optional[str] = None, transcript_path: Optional[str] = None) -> Dict[str, Any]:
    """Parse actual context window usage from Claude's transcript file or chat.json."""
    context_stats = {
        'context_tokens': 0,  # Total active context window usage
        'total_api_calls': 0,
        'model': 'claude-3-5-sonnet'  # default
    }

    # First try the provided transcript_path
    if transcript_path:
        transcript_file = Path(transcript_path)
        if transcript_file.exists():
            try:
                with open(transcript_file, 'r') as f:
                    # Parse JSONL format - each line is a separate JSON object
                    for line in f:
                        try:
                            entry = json.loads(line.strip())

                            # Skip if session_id provided and doesn't match
                            if session_id and entry.get('sessionId') != session_id:
                                continue

                            # Look for assistant responses with usage data
                            if (entry.get('type') == 'assistant' and
                                'message' in entry and
                                isinstance(entry['message'], dict) and
                                'usage' in entry['message']):

                                usage = entry['message']['usage']
                                context_stats['total_api_calls'] += 1

                                # Calculate total context window usage
                                input_tokens = usage.get('input_tokens', 0)
                                cache_read = usage.get('cache_read_input_tokens', 0)

                                # Total context = input_tokens + cache_read_input_tokens
                                # This matches what /context shows as total context usage
                                if input_tokens > 0 or cache_read > 0:
                                    context_stats['context_tokens'] = input_tokens + cache_read

                                # Extract model information
                                if 'model' in entry['message']:
                                    context_stats['model'] = entry['message']['model']

                        except json.JSONDecodeError:
                            continue
            except:
                pass

    # Fallback to chat.json if no transcript_path or if it failed
    if context_stats['context_tokens'] == 0:
        logs_dir = Path("logs")
        chat_log = logs_dir / "chat.json"

        if chat_log.exists():
            try:
                with open(chat_log, 'r') as f:
                    content = f.read()
                    try:
                        # Try to parse as JSON array
                        entries = json.loads(content)
                        if isinstance(entries, list):
                            for entry in entries:
                                # Skip if session_id provided and doesn't match
                                if session_id and entry.get('sessionId') != session_id:
                                    continue

                                # Look for assistant responses with usage data
                                if (entry.get('type') == 'assistant' and
                                    'message' in entry and
                                    isinstance(entry['message'], dict) and
                                    'usage' in entry['message']):

                                    usage = entry['message']['usage']
                                    context_stats['total_api_calls'] += 1

                                    # Calculate total context window usage
                                    input_tokens = usage.get('input_tokens', 0)
                                    cache_read = usage.get('cache_read_input_tokens', 0)

                                    # Total context = input_tokens + cache_read_input_tokens
                                    # This matches what /context shows as total context usage
                                    if input_tokens > 0 or cache_read > 0:
                                        context_stats['context_tokens'] = input_tokens + cache_read

                                    # Extract model information
                                    if 'model' in entry['message']:
                                        context_stats['model'] = entry['message']['model']

                    except json.JSONDecodeError:
                        pass
            except:
                pass

    return context_stats

def parse_real_token_usage(session_id: Optional[str] = None) -> Dict[str, Any]:
    """Parse actual token usage from Claude API responses in chat.json."""
    token_stats = {
        'total_input_tokens': 0,
        'total_output_tokens': 0,
        'total_cache_creation_tokens': 0,
        'total_cache_read_tokens': 0,
        'ephemeral_5m_tokens': 0,
        'ephemeral_1h_tokens': 0,
        'total_api_calls': 0,
        'model': 'claude-3-5-sonnet'  # default
    }

    # Check chat.json for actual API token usage
    logs_dir = Path("logs")
    chat_log = logs_dir / "chat.json"

    if not chat_log.exists():
        return token_stats

    try:
        with open(chat_log, 'r') as f:
            content = f.read()
            try:
                # Try to parse as JSON array
                entries = json.loads(content)
                if isinstance(entries, list):
                    for entry in entries:
                        # Skip if session_id provided and doesn't match
                        if session_id and entry.get('sessionId') != session_id:
                            continue

                        # Look for assistant responses with usage data
                        if (entry.get('type') == 'assistant' and
                            'message' in entry and
                            isinstance(entry['message'], dict) and
                            'usage' in entry['message']):

                            usage = entry['message']['usage']
                            token_stats['total_api_calls'] += 1

                            # Extract token counts
                            token_stats['total_input_tokens'] += usage.get('input_tokens', 0)
                            token_stats['total_output_tokens'] += usage.get('output_tokens', 0)
                            token_stats['total_cache_creation_tokens'] += usage.get('cache_creation_input_tokens', 0)
                            token_stats['total_cache_read_tokens'] += usage.get('cache_read_input_tokens', 0)

                            # Cache creation details
                            cache_creation = usage.get('cache_creation', {})
                            token_stats['ephemeral_5m_tokens'] += cache_creation.get('ephemeral_5m_input_tokens', 0)
                            token_stats['ephemeral_1h_tokens'] += cache_creation.get('ephemeral_1h_input_tokens', 0)

                        # Extract model information if available
                        if 'message' in entry and isinstance(entry['message'], dict) and 'model' in entry['message']:
                            token_stats['model'] = entry['message']['model']

            except json.JSONDecodeError:
                # Fallback to line-by-line parsing for JSONL format
                for line in content.strip().split('\n'):
                    try:
                        entry = json.loads(line.strip())
                        # Skip if session_id provided and doesn't match
                        if session_id and entry.get('sessionId') != session_id:
                            continue

                        # Look for assistant responses with usage data
                        if (entry.get('type') == 'assistant' and
                            'message' in entry and
                            isinstance(entry['message'], dict) and
                            'usage' in entry['message']):

                            usage = entry['message']['usage']
                            token_stats['total_api_calls'] += 1

                            # Extract token counts
                            token_stats['total_input_tokens'] += usage.get('input_tokens', 0)
                            token_stats['total_output_tokens'] += usage.get('output_tokens', 0)
                            token_stats['total_cache_creation_tokens'] += usage.get('cache_creation_input_tokens', 0)
                            token_stats['total_cache_read_tokens'] += usage.get('cache_read_input_tokens', 0)

                            # Cache creation details
                            cache_creation = usage.get('cache_creation', {})
                            token_stats['ephemeral_5m_tokens'] += cache_creation.get('ephemeral_5m_input_tokens', 0)
                            token_stats['ephemeral_1h_tokens'] += cache_creation.get('ephemeral_1h_input_tokens', 0)

                        # Extract model information if available
                        if 'message' in entry and isinstance(entry['message'], dict) and 'model' in entry['message']:
                            token_stats['model'] = entry['message']['model']
                    except:
                        pass
    except:
        pass

    return token_stats

def analyze_conversation_logs(session_id: Optional[str] = None) -> Dict[str, Any]:
    """Analyze conversation logs for metrics, optionally filtered by session."""
    stats = {
        'tool_calls': {},
        'total_tool_calls': 0,
        'agent_calls': 0,
        'errors': 0,
        'files_read': 0,
        'files_written': 0,
        'bash_commands': 0,
        'web_searches': 0,
        'conversation_turns': 0
    }

    # Get real token usage data
    token_data = parse_real_token_usage(session_id)
    stats.update(token_data)

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
                                # Skip if session_id provided and doesn't match
                                if session_id and entry.get('session_id') != session_id:
                                    continue
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
                                # Skip if session_id provided and doesn't match
                                if session_id and entry.get('session_id') != session_id:
                                    continue
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
                                # Skip if session_id provided and doesn't match
                                if session_id and entry.get('session_id') != session_id:
                                    continue
                                if entry.get('error') or 'error' in str(entry.get('result', '')).lower():
                                    stats['errors'] += 1
                    except json.JSONDecodeError:
                        # Fallback to line-by-line parsing
                        for line in content.strip().split('\n'):
                            try:
                                entry = json.loads(line.strip())
                                # Skip if session_id provided and doesn't match
                                if session_id and entry.get('session_id') != session_id:
                                    continue
                                if entry.get('error') or 'error' in str(entry.get('result', '')).lower():
                                    stats['errors'] += 1
                            except:
                                pass
            except:
                pass

        # Count conversation turns from chat.json (without token estimation)
        chat_log = logs_dir / "chat.json"
        if chat_log.exists():
            try:
                with open(chat_log, 'r') as f:
                    content = f.read()
                    try:
                        entries = json.loads(content)
                        if isinstance(entries, list):
                            for entry in entries:
                                # Skip if session_id provided and doesn't match
                                if session_id and entry.get('sessionId') != session_id:
                                    continue
                                if entry.get('role') == 'user':
                                    stats['conversation_turns'] += 1
                    except json.JSONDecodeError:
                        # Fallback to line-by-line parsing
                        for line in content.strip().split('\n'):
                            try:
                                entry = json.loads(line.strip())
                                if session_id and entry.get('sessionId') != session_id:
                                    continue
                                if entry.get('role') == 'user':
                                    stats['conversation_turns'] += 1
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

def get_session_duration(session_id: Optional[str] = None) -> Optional[str]:
    """Calculate session duration from logs for a specific session."""
    logs_dir = Path("logs")
    if not logs_dir.exists():
        return None

    # Find earliest and latest timestamps for this session
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
                            # Skip if session_id provided and doesn't match
                            # Different logs use different field names
                            entry_session = entry.get('session_id') or entry.get('sessionId')
                            if session_id and entry_session != session_id:
                                continue
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
                            # Skip if session_id provided and doesn't match
                            entry_session = entry.get('session_id') or entry.get('sessionId')
                            if session_id and entry_session != session_id:
                                continue
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
        # Try to read session_id and transcript_path from stdin (provided by Claude Code)
        session_id = None
        transcript_path = None
        try:
            if not sys.stdin.isatty():
                input_data = json.loads(sys.stdin.read())
                session_id = input_data.get('session_id')
                transcript_path = input_data.get('transcript_path')
        except:
            pass

        # Load session data
        session = get_current_session(session_id)

        # Get real context window usage from transcript
        context_stats = parse_context_usage_from_transcript(session_id, transcript_path)

        # Analyze conversation logs for this specific session (tool usage, etc.)
        stats = analyze_conversation_logs(session_id)

        # Merge context stats into main stats
        stats.update(context_stats)

        # Get session duration for this specific session
        duration = get_session_duration(session_id)

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

        # Real context window usage from transcript
        context_tokens = stats.get('context_tokens', 0)
        if context_tokens > 0:
            # Calculate context window percentage using REAL context data
            model = stats.get('model', 'claude-3-5-sonnet')
            context_limit = get_model_context_limit(model)
            context_percentage = (context_tokens / context_limit) * 100

            # Color coding based on ACTUAL context usage
            if context_percentage > 80:
                token_color = Colors.RED
                context_indicator = f"🚨 {context_percentage:.0f}%"
            elif context_percentage > 60:
                token_color = Colors.YELLOW
                context_indicator = f"⚠ {context_percentage:.0f}%"
            elif context_percentage > 40:
                token_color = Colors.YELLOW
                context_indicator = f"{context_percentage:.0f}%"
            else:
                token_color = Colors.GREEN
                context_indicator = f"{context_percentage:.0f}%"

            # Show real context window usage (should match /context command)
            status_parts.append(f"{token_color}{format_tokens(context_tokens)} ctx ({context_indicator}){Colors.RESET}")

        # Optionally show API cost tracking (commented out to focus on context)
        # total_api_tokens = stats.get('total_input_tokens', 0) + stats.get('total_output_tokens', 0) + stats.get('total_cache_creation_tokens', 0)
        # if total_api_tokens > 0:
        #     input_tokens = stats.get('total_input_tokens', 0) + stats.get('total_cache_creation_tokens', 0)
        #     output_tokens = stats.get('total_output_tokens', 0)
        #     status_parts.append(f"{Colors.GRAY}API: {format_tokens(total_api_tokens)} ↑{format_tokens(input_tokens)}/↓{format_tokens(output_tokens)}{Colors.RESET}")

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

        # Add alerts for high context usage
        context_tokens = stats.get('context_tokens', 0)
        if context_tokens > 0:
            model = stats.get('model', 'claude-3-5-sonnet')
            context_limit = get_model_context_limit(model)
            context_percentage = (context_tokens / context_limit) * 100

            if context_percentage > 80:
                status_line = f"{Colors.RED}🚨 CONTEXT LIMIT WARNING{Colors.RESET} │ " + status_line
            elif context_percentage > 60:
                status_line = f"{Colors.YELLOW}⚠  HIGH CONTEXT USAGE{Colors.RESET} │ " + status_line

        if stats['errors'] > 5:
            status_line = f"{Colors.YELLOW}⚠ ERRORS DETECTED{Colors.RESET} │ " + status_line

        print(status_line)

    except Exception as e:
        # Fallback status
        print(f"{Colors.CYAN}🤖 Claude{Colors.RESET} │ {Colors.GRAY}Session data unavailable{Colors.RESET}")

if __name__ == "__main__":
    main()