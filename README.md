# Claude Code Advanced Workflows

**Production-Ready Claude Code Customization Suite with Enterprise Integrations**

A comprehensive system extending Claude Code with 8 lifecycle hooks, 18 specialized agents, 18+ custom commands, and a complete Monday.com project management integration. Features intelligent TTS systems, automated documentation generation, security enhancements, and visual HTML output generation.

> **🚀 Quick Reference:** See [CHEATSHEET.md](CHEATSHEET.md) for complete command, hook, and agent documentation

## ✨ Key Features

- 🪝 **8 Complete Hook System** - Full Claude Code lifecycle control with security features
- 🤖 **5 Specialized Agents** - Including meta-agent, documentation generators, research tools, and work completion summaries
- 💼 **Monday.com Integration** - Enterprise-grade project management with $278K+ real data tested
- 🎨 **10+ Output Styles** - Including interactive HTML generation, Mermaid diagrams, and timeline chronicles
- 🔊 **Intelligent TTS System** - Multi-provider audio feedback (ElevenLabs, OpenAI, pyttsx3)
- 🛡️ **Security Features** - Dangerous command prevention and audit logging
- 📊 **Financial Analytics** - Complete expense tracking and reporting
- ⚙️ **UV Architecture** - Isolated Python dependencies with lightning-fast execution

## 📋 Prerequisites

### Required
- **[Claude Code](https://docs.anthropic.com/en/docs/claude-code)** - Anthropic's official CLI
- **[Astral UV](https://docs.astral.sh/uv/getting-started/installation/)** - Fast Python package manager

### Optional Integrations
- **[Monday.com API Token](https://developer.monday.com/api-reference/docs/authentication)** - Project management integration
- **[ElevenLabs Account](https://elevenlabs.io/)** - Professional text-to-speech
- **[OpenAI API Key](https://openai.com/)** - Language model and TTS provider
- **[Anthropic API Key](https://www.anthropic.com/)** - Primary language model provider
- **[Ollama](https://ollama.com/)** - Local language model support

## 🚀 Quick Start

### 1. Clone and Setup
```bash
git clone <your-repo-url>
cd cc-advanced-workflows
```

### 2. Configure Monday.com (Optional but Recommended)
```bash
# Get your API token from https://developer.monday.com/
export MONDAY_API_TOKEN="your_api_token_here"
```

### 3. Test the System
```bash
# List your Monday.com boards
/monday_boards

# Generate a daily operations report
/monday_daily_report

# Analyze project priorities
/monday_priorities --limit 10
```

### 4. Explore Features
```bash
# Generate interactive HTML documentation
/prime  # Then switch to genui output style

# Create new agents automatically
"Create an agent that reviews code for security vulnerabilities"

# Use TTS for audio feedback
"Generate an audio summary of completed work"
```

## 🪝 Hook System (8 Hooks)

Complete Claude Code lifecycle control with enterprise security features.

### Core Security Hooks

| Hook | Fires | Can Block | Primary Function |
|------|-------|-----------|------------------|
| **UserPromptSubmit** | Before Claude processes prompts | ✅ Yes | Security validation, context injection, audit logging |
| **PreToolUse** | Before tool execution | ✅ Yes | Dangerous command prevention, permission control |
| **PostToolUse** | After tool completion | ❌ No | Result logging, transcript conversion |

### Workflow Control Hooks

| Hook | Fires | Can Block | Primary Function |
|------|-------|-----------|------------------|
| **Stop** | When Claude finishes | ✅ Yes | Task validation, AI completion messages |
| **SubagentStop** | When agents finish | ✅ Yes | Agent validation, completion announcements |
| **Notification** | On Claude notifications | ❌ No | TTS alerts, custom notifications |

### Session Management Hooks

| Hook | Fires | Can Block | Primary Function |
|------|-------|-----------|------------------|
| **PreCompact** | Before compaction | ❌ No | Transcript backup, context preservation |
| **SessionStart** | On session start/resume | ❌ No | Development context loading, environment setup |

### Security Features
- **Dangerous Command Blocking**: `rm -rf`, `sudo rm`, `chmod 777`, `/etc/` writes
- **Environment Protection**: `.env` file access prevention
- **Audit Logging**: All interactions logged to `logs/` directory
- **Exit Code Control**: Precise flow control with structured JSON responses

## 🤖 Agent Ecosystem (5 Agents)

### Core Utility Agents
- **meta-agent** - Generates new agents from descriptions
- **changelog-updater** - Automated documentation maintenance
- **work-completion-summary** - Audio task summaries with TTS
- **hello-world-agent** - Simple greeting and testing
- **llm-ai-agents-and-eng-research** - Latest AI/ML research updates

*Note: All cryptocurrency-related agents have been removed to focus on core productivity and project management features.*


## 💼 Monday.com Integration

Enterprise-grade project management integration with production-ready reliability.

### Available Commands

| Command | Purpose | Key Features |
|---------|---------|--------------|
| `/monday_boards` | Board & Group Discovery | Visual indicators, complete structure mapping |
| `/monday_daily_report` | Daily Operations Overview | Overdue analysis, status distribution, activity tracking |
| `/monday_priorities` | Intelligent Task Ranking | Multi-criteria scoring, urgency calculations |
| `/monday_workload` | Team Capacity Analysis | Effort tracking, balance ratios, capacity planning |
| `/monday_complete_data` | Full Data Export | All column types, complete audit trail |
| `/monday_expense_report` | Financial Analytics | Monetary parsing, receipt tracking, category analysis |

### Enterprise Features
- **Modern API Client**: Complexity budget management, exponential backoff retry
- **Production-Ready Reliability**: Type-safe date parsing with robust error recovery
- **Financial Processing**: Decimal precision, multi-currency support, audit trails
- **Error Recovery**: Graceful handling of API failures and mixed data formats
- **Performance**: Pagination, caching, efficient complexity management
- **Real-World Tested**: Managing $278K+ project data across 25+ boards and 392 items

### Priority Scoring Algorithm
Objective task ranking using multi-criteria analysis:
- **Priority Levels**: Critical (100), Urgent (80), High (60), Medium (40), Low (10)
- **Status Modifiers**: Blocked/Stuck (+50), In Progress (+30), Completed (-100)
- **Due Date Urgency**: Overdue (+200), Due Today (+150), Due This Week (+100)

## 🎨 Output Styles (10+ Styles)

Transform Claude's responses with professional formatting options.

### Interactive Styles

| Style | Description | Best For |
|-------|-------------|----------|
| **genui** ⭐ | **Interactive HTML with embedded styling, auto-opens in browser** | **Visual documentation, instant preview, professional reports** |
| **tts-summary** | Audio announcements via ElevenLabs TTS | Accessibility, hands-free operation |

### Data Organization Styles

| Style | Description | Best For |
|-------|-------------|----------|
| **table-based** | Structured markdown tables | Comparisons, status reports, data analysis |
| **yaml-structured** | YAML configuration format | Settings, hierarchical data, API configs |
| **bullet-points** | Clean nested lists | Action items, task tracking, documentation |

### Content Presentation Styles

| Style | Description | Best For |
|-------|-------------|----------|
| **ultra-concise** | Minimal words, maximum speed | Experienced developers, rapid prototyping |
| **html-structured** | Semantic HTML5 with data attributes | Web integration, rich formatting |
| **markdown-focused** | Full markdown feature utilization | Complex documentation, mixed content |

### Visual Documentation Styles
| Style | Description | Best For |
|-------|-------------|----------|
| **mermaid-diagram** ⭐ | **Convert explanations into Mermaid flowcharts, sequence diagrams, and architectural representations** | **Process documentation, API workflows, system architecture** |
| **timeline-chronicle** ⭐ | **Chronological timeline format with ASCII art elements and milestone tracking** | **Project histories, incident timelines, process flows** |

### Usage
```bash
# Activate any style
/output-style genui
/output-style table-based

# GenUI creates instant browser-ready documentation
/prime  # After setting genui style
```

## 📊 Commands Reference (18+ Commands)

### Project Management
```bash
# Monday.com Operations
/monday_boards                    # List all boards and groups
/monday_daily_report             # Comprehensive daily overview
/monday_priorities --limit 20    # Top priority items with scoring
/monday_workload --person "Name" # Individual workload analysis
/monday_expense_report --board-id ID  # Financial reporting

# Documentation Management
/changelog_update               # Update CHANGELOG.md automatically
/prime                         # Project analysis and understanding
/question "How does X work?"   # Project-specific Q&A
```

### Development Tools
```bash
# Status and Context
/git_status                    # Enhanced git repository status
/update_status_line           # Dynamic terminal status updates

# Agent Management
"Create a new agent that..."   # Meta-agent automatically creates agents
/ai_research                  # Latest AI/ML research and trends
```


## 🔧 Advanced Features

### Status Lines (Enhanced Suite)
Real-time terminal status with comprehensive monitoring:

#### Core Status Lines
- **v1**: Basic git and directory info
- **v2**: Smart prompts with color-coded task types
- **v3**: Agent sessions with prompt history
- **v4**: Extended metadata and custom key-value pairs

#### Specialized Monitoring ⭐
- **Productivity Metrics**: Developer productivity tracking with git activity, code generation metrics, and focus time analysis
- **Resource Monitor**: Real-time system monitoring (CPU, memory, disk, network) with warning indicators
- **Claude Conversation**: **Enhanced real-time context window tracking with session-specific accuracy**
  - **Precise token counting** aligned with Claude's internal tracking (matches `/context` command)
  - **Context usage warnings** with visual indicators (🚨 >80%, ⚠ >60%)
  - **Session isolation** preventing cross-session data contamination
  - **API token insights** with cache efficiency and model detection
- **Monday.com Integration**: Live status of project management integrations and API health

### Global Session Management
Cross-project session persistence with automatic agent naming and metadata tracking.

### Quality Gates
Automated validation and testing integration for maintaining code quality.

### UV Single-File Architecture
- **Isolation**: Each hook declares its own dependencies
- **Performance**: Lightning-fast dependency resolution
- **Portability**: Works across different environments
- **Maintainability**: Self-contained, independently modifiable scripts

## 🏗️ Architecture

### Project Structure
```
.claude/
├── hooks/                    # 8 lifecycle hooks with UV dependencies
│   ├── utils/               # Shared utilities (TTS, LLM, Monday API)
│   └── monday_*_impl.py     # Monday.com integration implementations
├── agents/                  # 5 specialized sub-agents
├── commands/                # 18+ custom slash commands
├── output-styles/           # 10+ response formatting styles
└── status_lines/           # Enhanced status line suite with specialized monitoring
```

### Security Architecture
- **Multi-Layer Protection**: UserPromptSubmit → PreToolUse → PostToolUse validation
- **Permission System**: Granular tool access control
- **Audit Trail**: Complete JSON logging of all interactions
- **Environment Protection**: Sensitive file and directory access prevention

### Data Flow
```
User Input → UserPromptSubmit Hook → Claude Processing →
PreToolUse Hook → Tool Execution → PostToolUse Hook →
Response Generation → Stop Hook → User Output
```

## 🔒 Security Features

### Dangerous Command Prevention
Automatically blocks hazardous operations:
- File system destruction: `rm -rf`, `sudo rm`
- Permission vulnerabilities: `chmod 777`
- System directory access: `/etc/` writes
- Environment exposure: `.env` file access

### Audit Logging
Complete interaction history stored in `logs/`:
- `user_prompt_submit.json` - All user inputs
- `pre_tool_use.json` - Tool execution attempts
- `post_tool_use.json` - Tool results and outputs
- `stop.json` - Session completion events
- `chat.json` - Readable conversation transcripts

## 📈 Performance & Reliability

### Monday.com Integration Performance
- **50+ API Calls**: Zero failures in production testing
- **387 Items**: Successfully processed across 25 boards
- **$278K+ Data**: Real financial project management
- **Type Safety**: Robust date parsing and error recovery

### System Performance
- **UV Dependencies**: Sub-second script startup
- **Complexity Management**: GraphQL budget optimization
- **Error Recovery**: Graceful degradation with fallback options
- **Date Parsing Reliability**: Type-safe date handling with comprehensive error recovery
- **Memory Efficiency**: Streaming large datasets

## 🎯 Use Cases

### Project Management
- **Daily Standups**: Automated status reports with overdue analysis
- **Sprint Planning**: Priority scoring and workload balancing
- **Financial Tracking**: Expense categorization and budget monitoring
- **Team Coordination**: Workload distribution and capacity planning

### Development Workflows
- **Documentation**: Automated changelog generation and project analysis
- **Code Review**: Security vulnerability scanning and quality gates
- **Research**: AI/ML trends and industry analysis
- **Agent Development**: Meta-agent for rapid custom agent creation

### Content Creation
- **Interactive Documentation**: GenUI HTML generation with professional styling
- **Audio Summaries**: TTS-powered task completion announcements
- **Visual Reports**: Table-based and structured data presentation
- **Multi-Format Output**: Flexible response formatting for different audiences

## 🛠️ Troubleshooting

### Common Issues

**Monday.com Connection**
```bash
# Verify API token
echo $MONDAY_API_TOKEN

# Test basic connectivity
/monday_boards --simple

# Test date parsing reliability
/monday_priorities --limit 5
/monday_workload --days 7
```

**Hook Execution Errors**
```bash
# Check logs for details
cat logs/pre_tool_use.json | jq '.'

# Verify UV dependencies
uv run .claude/hooks/session_start.py
```

**Agent Creation Issues**
```bash
# Test meta-agent functionality
"Create a simple test agent"

# Check agent file structure
ls .claude/agents/
```

## 📚 Documentation Links

- **[Claude Code Documentation](https://docs.anthropic.com/en/docs/claude-code)** - Official Claude Code docs
- **[Hooks Reference](https://docs.anthropic.com/en/docs/claude-code/hooks)** - Hook system documentation
- **[Sub-Agents Guide](https://docs.anthropic.com/en/docs/claude-code/sub-agents)** - Agent creation and management
- **[Output Styles](https://docs.anthropic.com/en/docs/claude-code/output-styles)** - Response formatting options
- **[Monday.com API](https://developer.monday.com/api-reference/docs/authentication)** - API documentation and token setup

## 🤝 Contributing

This system demonstrates enterprise-level Claude Code customization with production-ready integrations. The architecture supports:

- **Easy Extension**: UV single-file scripts for rapid development
- **Modular Design**: Independent hooks, agents, and commands
- **Professional Integration**: Enterprise APIs and financial data handling
- **Comprehensive Testing**: Real-world data validation and error recovery

## 📄 License

This project extends Claude Code capabilities while maintaining compatibility with Anthropic's terms of service. All integrations use official APIs and documented extension points.

---

**Built with ❤️ for the Claude Code community**

*Demonstrating the power of AI-assisted development workflows with enterprise-grade reliability and security.*