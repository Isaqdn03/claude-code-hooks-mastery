# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Monday.com Integration Suite**: Comprehensive Monday.com workspace management with 6 specialized commands:
  - `/monday_boards` - Board and group listing with filtering options
  - `/monday_daily_report` - Daily status reports with overdue task analysis
  - `/monday_priorities` - Smart priority scoring system with urgency calculations
  - `/monday_workload` - Team workload analysis with effort point tracking
  - `/monday_complete_data` - Full data export for external analysis
  - `/monday_expense_report` - Financial tracking and expense reporting
- **Monday.com API Client**: Modern API client (`utils/monday_api.py`) with complexity budget management, exponential backoff retry logic, and comprehensive error handling
- **CHEATSHEET.md**: Complete quick reference guide covering all hooks, commands, agents, and Monday.com integration features
- **Quality Gates Script**: Automated validation and testing integration script (`quality_gates.py`)
- **Enhanced Documentation**: Updated and expanded agent descriptions and command documentation

### Changed
- **LLM AI Research Agent**: Enhanced with improved research capabilities and updated documentation
- **Claude Settings**: Updated configuration to support new Monday.com commands and quality gates
- **Command Organization**: Improved structure and documentation for better discoverability

### Removed
- **Sample Applications**: Cleaned up demo files including `apps/hello.py`, `apps/hello.ts`, and various image assets
- **Environment Sample**: Removed `.env.sample` file as part of project cleanup

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