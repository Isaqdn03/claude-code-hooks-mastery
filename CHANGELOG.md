# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Productivity Metrics Status Line**: Advanced developer productivity tracking (`productivity_metrics_status.py`) with:
  - Git activity monitoring (commits, streaks, lines added/removed)
  - Claude Code productivity analysis (code generation, problems solved, tool usage)
  - Focus time tracking and session analysis
  - Comprehensive productivity scoring with visual indicators and motivational messages
- **Resource Monitor Status Line**: Real-time system monitoring (`resource_monitor_status.py`) featuring:
  - CPU, memory, and disk usage tracking with color-coded alerts
  - Network and disk I/O speed monitoring
  - Top process identification and system temperature monitoring
  - Warning indicators for high resource usage (>90% thresholds)
- **Enhanced Status Line Suite**: Additional monitoring capabilities with:
  - Claude conversation context tracking (`claude_conversation_status.py`)
  - Monday.com integration status monitoring (`monday_integration_status.py`)
- **Visual Output Styles**: Two new professional output formats:
  - **Mermaid Diagram Style**: Convert explanations into Mermaid flowcharts, sequence diagrams, and architectural representations with rendering instructions
  - **Timeline Chronicle Style**: Chronological timeline format with ASCII art elements, milestone tracking, and visual progression indicators
- **Board Resolution Testing**: Test implementation for Monday.com board name resolution functionality (`test_board_resolution.py`)
- **Documentation Organization**: Enhanced project structure with CHEATSHEET.md moved to dedicated `ai_docs/` directory for better organization
- **Monday.com Integration Suite**: Enterprise-grade Monday.com workspace management with 6 specialized commands:
  - `/monday_boards` - Board and group listing with filtering options
  - `/monday_daily_report` - Daily status reports with overdue task analysis
  - `/monday_priorities` - Smart priority scoring system with urgency calculations
  - `/monday_workload` - Team workload analysis with effort point tracking
  - `/monday_complete_data` - Full data export for external analysis
  - `/monday_expense_report` - Financial tracking and expense reporting
- **Production-Ready Monday.com API Client**: Modern API client (`utils/monday_api.py`) with:
  - Complexity budget management and exponential backoff retry logic
  - Comprehensive error handling and graceful degradation
  - Type-safe date parsing with robust error recovery
  - Tested with $278K+ in real project data across 25+ boards and 392 items
- **CHEATSHEET.md**: Complete quick reference guide covering all hooks, commands, agents, and Monday.com integration features
- **Quality Gates Script**: Automated validation and testing integration script (`quality_gates.py`)
- **Enterprise Documentation**: Complete README.md rewrite with:
  - Documentation of all 8 hooks, 18 agents, 18+ commands, and 8 output styles
  - Architecture diagrams, security features, and troubleshooting guides
  - Professional presentation suitable for enterprise deployment

### Fixed
- **Critical Date Parsing Issues**: Resolved date parsing failures across all Monday.com slash commands
  - Implemented consistent `parse_date_string()` function with type safety
  - Fixed date comparison errors in `/monday_priorities` and `/monday_workload`
  - Added robust handling for mixed date formats without system crashes
  - Enhanced reliability with fallback options and comprehensive logging
- **Production Stability**: Enhanced error handling and graceful degradation for enterprise use

### Changed
- **Monday.com Commands**: Enhanced all 6 commands with production-tested reliability improvements
- **LLM AI Research Agent**: Enhanced with improved research capabilities and updated documentation
- **Claude Settings**: Updated configuration to support new Monday.com commands and quality gates
- **Command Organization**: Improved structure and documentation for better discoverability

### Removed
- **Debug Scripts**: Removed temporary debug script (`debug_rsr_data.py`) after integrating functionality into production commands
- **Sample Applications**: Cleaned up demo files including `apps/hello.py`, `apps/hello.ts`, and various image assets
- **Environment Sample**: Removed `.env.sample` file as part of project cleanup
- **Legacy Image Assets**: Removed outdated demonstration images and GIFs

### Previous Releases

### Added (Earlier Updates)
- **Global Session Management**: Implemented global session data storage in `~/.claude/data/sessions/` for cross-project session persistence
- **Changelog Command**: New `/changelog_update` slash command for automated documentation updates using dedicated changelog-updater agent
- **GenUI Output Style**: Enhanced HTML generation output style with embedded modern styling, professional themes, and browser auto-opening
- **Cryptocurrency Research Agents**: Comprehensive suite of crypto analysis agents including:
  - Crypto coin analyzer (Haiku, Opus, Sonnet variants)
  - Crypto investment plays analyzer
  - Crypto market agent
  - Crypto movers tracker
  - Macro crypto correlation scanner
- **Changelog-Updater Agent**: Specialized sub-agent for maintaining project documentation following Keep a Changelog standards
- **Enhanced Status Lines**: Updated status line scripts to use global session paths and improved metadata support
- **Agent Prompt Templates**: Dedicated prompt templates for crypto research agents in `.claude/commands/agent_prompts/`

### Changed (Earlier Updates)
- **Session Start Hook**: Enhanced to support global session data management and improved development context loading
- **Status Line Architecture**: Migrated from local to global session data storage for better persistence across projects
- **Agent Organization**: Improved sub-agent structure with better categorization and model-specific variants

### Fixed (Earlier Updates)
- **Session Persistence**: Resolved issues with session data not persisting across Claude Code interactions
- **Status Line Data Access**: Fixed status lines to properly access global session information

## [Initial Release] - 2024-09-15

### Added
- Complete Claude Code hook lifecycle implementation (8 hooks)
- UV single-file script architecture for hook management
- Intelligent TTS system with multiple provider support (ElevenLabs, OpenAI, pyttsx3)
- Security enhancements for dangerous command blocking
- Sub-agent system with meta-agent capabilities
- Custom output styles collection
- Enhanced status lines with real-time conversation context
- Comprehensive documentation and examples
- LLM utility scripts for OpenAI, Anthropic, and Ollama integration
- Project-specific context loading and development environment setup