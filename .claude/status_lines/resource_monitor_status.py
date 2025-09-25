#!/usr/bin/env -S uv run --quiet
# /// script
# dependencies = [
#     "psutil",
#     "humanize",
# ]
# ///

"""
Resource Monitor Status Line for Claude Code
Real-time system resource usage monitoring with CPU, memory, disk, and network stats
"""

import json
import os
import sys
import time
import psutil
import humanize
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

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

def get_color_for_percentage(value: float) -> str:
    """Return color based on percentage threshold."""
    if value >= 90:
        return Colors.RED
    elif value >= 70:
        return Colors.YELLOW
    elif value >= 50:
        return Colors.CYAN
    else:
        return Colors.GREEN

def get_network_speed() -> Tuple[float, float]:
    """Get network upload/download speeds (bytes/sec)."""
    try:
        # Get initial snapshot
        net_io_1 = psutil.net_io_counters()
        time.sleep(0.1)  # Short interval for quick response
        net_io_2 = psutil.net_io_counters()

        # Calculate speeds
        download_speed = (net_io_2.bytes_recv - net_io_1.bytes_recv) * 10  # Scale to per second
        upload_speed = (net_io_2.bytes_sent - net_io_1.bytes_sent) * 10

        return download_speed, upload_speed
    except:
        return 0.0, 0.0

def get_disk_io_speed() -> Tuple[float, float]:
    """Get disk read/write speeds (bytes/sec)."""
    try:
        disk_io_1 = psutil.disk_io_counters()
        time.sleep(0.1)
        disk_io_2 = psutil.disk_io_counters()

        read_speed = (disk_io_2.read_bytes - disk_io_1.read_bytes) * 10
        write_speed = (disk_io_2.write_bytes - disk_io_1.write_bytes) * 10

        return read_speed, write_speed
    except:
        return 0.0, 0.0

def format_bytes_speed(bytes_per_sec: float) -> str:
    """Format bytes/sec to human-readable speed."""
    if bytes_per_sec < 1024:
        return f"{bytes_per_sec:.0f}B/s"
    elif bytes_per_sec < 1024 * 1024:
        return f"{bytes_per_sec/1024:.1f}KB/s"
    elif bytes_per_sec < 1024 * 1024 * 1024:
        return f"{bytes_per_sec/(1024*1024):.1f}MB/s"
    else:
        return f"{bytes_per_sec/(1024*1024*1024):.1f}GB/s"

def get_top_process() -> str:
    """Get the top CPU consuming process name."""
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        if processes:
            top_proc = max(processes, key=lambda x: x.get('cpu_percent', 0))
            if top_proc['cpu_percent'] > 10:  # Only show if significant
                name = top_proc['name'][:15]  # Truncate long names
                return f" [{name}: {top_proc['cpu_percent']:.0f}%]"
    except:
        pass
    return ""

def get_temperature() -> Optional[float]:
    """Get CPU temperature if available."""
    try:
        temps = psutil.sensors_temperatures()
        if temps:
            for name, entries in temps.items():
                for entry in entries:
                    if entry.label in ['Core 0', 'Package id 0', 'CPU']:
                        return entry.current
                # Fallback to first available
                if entries:
                    return entries[0].current
    except:
        pass
    return None

def main():
    """Generate resource monitoring status line."""
    try:
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=0.1)
        cpu_count = psutil.cpu_count()
        load_avg = os.getloadavg()
        cpu_color = get_color_for_percentage(cpu_percent)

        # Memory metrics
        mem = psutil.virtual_memory()
        mem_color = get_color_for_percentage(mem.percent)
        swap = psutil.swap_memory()

        # Disk metrics
        disk = psutil.disk_usage('/')
        disk_color = get_color_for_percentage(disk.percent)
        disk_read, disk_write = get_disk_io_speed()

        # Network metrics
        download, upload = get_network_speed()

        # Process metrics
        process_count = len(psutil.pids())
        top_process = get_top_process()

        # Temperature (if available)
        temp = get_temperature()
        temp_str = ""
        if temp:
            temp_color = Colors.RED if temp > 80 else Colors.YELLOW if temp > 60 else Colors.GREEN
            temp_str = f" {temp_color}{temp:.0f}°C{Colors.RESET}"

        # Build status line components
        status_parts = []

        # CPU section
        cpu_str = f"{cpu_color}▣ CPU:{cpu_percent:>5.1f}%{Colors.RESET}"
        cpu_str += f" {Colors.GRAY}[{load_avg[0]:.1f}]{Colors.RESET}"
        if temp_str:
            cpu_str += temp_str
        cpu_str += top_process
        status_parts.append(cpu_str)

        # Memory section
        mem_used = humanize.naturalsize(mem.used, binary=True, format="%.1f")
        mem_total = humanize.naturalsize(mem.total, binary=True, format="%.0f")
        mem_str = f"{mem_color}◉ MEM:{mem.percent:>5.1f}%{Colors.RESET}"
        mem_str += f" {Colors.GRAY}[{mem_used}/{mem_total}]{Colors.RESET}"
        if swap.percent > 0:
            swap_color = get_color_for_percentage(swap.percent)
            mem_str += f" {swap_color}SWAP:{swap.percent:.0f}%{Colors.RESET}"
        status_parts.append(mem_str)

        # Disk section
        disk_free = humanize.naturalsize(disk.free, binary=True, format="%.1f")
        disk_str = f"{disk_color}◈ DISK:{disk.percent:>5.1f}%{Colors.RESET}"
        disk_str += f" {Colors.GRAY}[{disk_free} free]{Colors.RESET}"

        # Add disk I/O if significant
        if disk_read > 1024 * 100 or disk_write > 1024 * 100:  # > 100KB/s
            disk_str += f" {Colors.CYAN}R:{format_bytes_speed(disk_read)}{Colors.RESET}"
            disk_str += f" {Colors.MAGENTA}W:{format_bytes_speed(disk_write)}{Colors.RESET}"
        status_parts.append(disk_str)

        # Network section (only show if active)
        if download > 1024 or upload > 1024:  # > 1KB/s
            net_str = f"{Colors.BLUE}⇊{format_bytes_speed(download)}{Colors.RESET}"
            net_str += f" {Colors.GREEN}⇈{format_bytes_speed(upload)}{Colors.RESET}"
            status_parts.append(net_str)

        # Process count
        status_parts.append(f"{Colors.GRAY}◦ {process_count} procs{Colors.RESET}")

        # Join all parts
        status_line = " ".join(status_parts)

        # Add warning indicators
        warnings = []
        if cpu_percent > 90:
            warnings.append(f"{Colors.RED}⚠ HIGH CPU{Colors.RESET}")
        if mem.percent > 90:
            warnings.append(f"{Colors.RED}⚠ HIGH MEM{Colors.RESET}")
        if disk.percent > 90:
            warnings.append(f"{Colors.RED}⚠ LOW DISK{Colors.RESET}")

        if warnings:
            status_line = " ".join(warnings) + " │ " + status_line

        print(status_line)

    except Exception as e:
        # Fallback to simple status
        print(f"{Colors.RED}Resource Monitor Error: {e}{Colors.RESET}")

if __name__ == "__main__":
    main()