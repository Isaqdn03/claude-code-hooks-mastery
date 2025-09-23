# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Global Session Management**: Implemented global session data storage in `~/.claude/data/sessions/` for cross-project session persistence
- **Changelog Command**: New `/changelog` slash command for automated documentation updates using dedicated changelog-updater agent
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

### Changed
- **Session Start Hook**: Enhanced to support global session data management and improved development context loading
- **Status Line Architecture**: Migrated from local to global session data storage for better persistence across projects
- **Agent Organization**: Improved sub-agent structure with better categorization and model-specific variants

### Fixed
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