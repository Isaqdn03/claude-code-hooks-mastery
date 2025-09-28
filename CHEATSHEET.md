# CC Advanced Workflows - Complete Cheatsheet

> **Quick Reference Guide** for your Claude Code Hooks, Commands, Agents, and Monday.com Integration

---

## 🪝 Claude Code Hooks (8 Total)

### 1. **UserPromptSubmit Hook** - `user_prompt_submit.py`
**Fires:** When you submit a prompt (before Claude processes it)
**Can Block:** ✅ Yes (Exit Code 2 stops prompt processing)
**Purpose:** Prompt validation, logging, context injection, security filtering

**Key Features:**
- Logs all prompts to `logs/user_prompt_submit.json`
- Can add context that Claude sees with your prompt
- Security validation for dangerous commands
- Agent naming functionality with `--name-agent` flag

**Usage Flags:**
- `--log-only`: Just log prompts (default)
- `--validate`: Enable security validation
- `--context`: Add project context to prompts
- `--name-agent`: Generate unique agent names using LLM

---

### 2. **PreToolUse Hook** - `pre_tool_use.py`
**Fires:** Before any tool execution
**Can Block:** ✅ Yes (Exit Code 2 prevents tool execution)
**Purpose:** Security validation, dangerous command prevention

**Blocks These Dangerous Patterns:**
- `rm -rf` commands
- `sudo rm` commands
- `chmod 777` permissions
- Writing to `/etc/` directories
- `.env` file access attempts

**Logs to:** `logs/pre_tool_use.json`

---

### 3. **PostToolUse Hook** - `post_tool_use.py`
**Fires:** After tool completion
**Can Block:** ❌ No (tool already executed)
**Purpose:** Result logging, transcript conversion

**Key Features:**
- Logs all tool results to `logs/post_tool_use.json`
- Converts JSONL transcripts to readable JSON with `--chat` flag
- Creates `logs/chat.json` with conversation history

---

### 4. **Notification Hook** - `notification.py`
**Fires:** When Claude Code sends notifications
**Can Block:** ❌ No
**Purpose:** Custom notifications, TTS alerts

**Features:**
- TTS announcements: "Your agent needs your input"
- 30% chance includes personalized name
- Logs to `logs/notification.json`

---

### 5. **Stop Hook** - `stop.py`
**Fires:** When Claude Code finishes responding
**Can Block:** ✅ Yes (Exit Code 2 forces continuation)
**Purpose:** AI-generated completion messages, task validation

**Features:**
- AI-generated completion messages with TTS
- LLM provider priority: OpenAI → Anthropic → Ollama → Random
- Logs to `logs/stop.json`
- **⚠️ Caution:** Can cause infinite loops if not controlled

---

### 6. **SubagentStop Hook** - `subagent_stop.py`
**Fires:** When subagents finish responding
**Can Block:** ✅ Yes (Exit Code 2 blocks subagent stopping)
**Purpose:** Subagent completion validation

**Features:**
- TTS playback: "Subagent Complete"
- Logs to `logs/subagent_stop.json`

---

### 7. **PreCompact Hook** - `pre_compact.py`
**Fires:** Before compaction operations
**Can Block:** ❌ No
**Purpose:** Transcript backup, context preservation

**Features:**
- Creates transcript backups before compaction
- Logs manual vs auto compaction triggers
- Logs to `logs/pre_compact.json`

---

### 8. **SessionStart Hook** - `session_start.py`
**Fires:** When sessions start or resume
**Can Block:** ❌ No
**Purpose:** Development context loading, session initialization

**Features:**
- Loads git status and recent issues
- Development environment setup
- Global session data management
- Logs to `logs/session_start.json`

---

## 📋 Monday.com Integration Commands

> **Setup Required:** `export MONDAY_API_TOKEN="your_api_token_here"`

### **Board Management**

#### `/monday_boards` - List Boards & Groups
```bash
/monday_boards                    # List all boards with groups
/monday_boards --simple           # List boards only (no groups)
/monday_boards --board-ids ID1 ID2  # Show specific boards
/monday_boards --active-only      # Show only active boards
```
**Purpose:** Get board IDs and group structure for other commands
**Implementation:** `monday_boards_impl.py`

### **Daily Operations**

#### `/monday_daily_report` - Comprehensive Daily Report
```bash
/monday_daily_report                           # All active boards
/monday_daily_report --board-ids ID1 ID2      # Specific boards
/monday_daily_report --include-completed       # Include completed items
```
**Features:**
- Overdue tasks analysis
- Items created/updated today
- Status distribution across projects
- Priority breakdown with actionable insights

#### `/monday_priorities` - Smart Priority Analysis
```bash
/monday_priorities                        # All active boards
/monday_priorities --board-ids ID1 ID2   # Specific boards
/monday_priorities --person "John Smith"  # Focus on specific person
/monday_priorities --limit 30             # Show top 30 items
```
**Scoring System:**
- Priority Level: Critical (100), Urgent (80), High (60), Medium (40), Low (10)
- Status Conditions: Blocked/Stuck (+50), In Progress (+30), Completed (-100)
- Due Date Urgency: Overdue (+200), Due Today (+150), Due This Week (+100)

#### `/monday_workload` - Team Workload Analysis
```bash
/monday_workload                          # All active boards
/monday_workload --board-ids ID1 ID2     # Specific boards
/monday_workload --person "John Smith"    # Focus on specific person
/monday_workload --include-completed      # Include completed items
```
**Metrics:**
- Effort point analysis per team member
- Workload balance ratios and completion rates
- Overloaded/underloaded team identification
- Unassigned items analysis

### **Advanced Reports**

#### `/monday_complete_data` - Full Data Export
**Purpose:** Complete data extraction for external analysis
**Implementation:** `monday_complete_data_impl.py`

#### `/monday_expense_report` - Financial Analysis
**Purpose:** Expense tracking and financial reporting
**Implementation:** `monday_expense_report_impl.py`

---

## 🤖 Sub-Agents

### **Core Agents**

#### **meta-agent** - Agent Creator
**Description:** Generates new sub-agents from descriptions
**Model:** Opus
**Tools:** Write, WebFetch, Firecrawl
**Usage:** "Build a new sub-agent that runs tests and fixes failures"

#### **changelog-updater** - Documentation Maintenance
**Description:** Updates project documentation (CHANGELOG.md, README.md, CHEATSHEET.md) from git changes
**Usage:** Automatically triggered by `/changelog_update` command
**Enhanced:** Now supports CHEATSHEET.md updates for workflow and reference changes

#### **work-completion-summary** - Audio Summaries
**Description:** Provides TTS summaries of completed work
**Trigger:** Say "tts" or "audio summary"

#### **hello-world-agent** - Simple Greeting
**Description:** Responds to greetings with friendly messages
**Trigger:** Say "hi claude" or "hi cc"

#### **llm-ai-agents-and-eng-research** - AI Research
**Description:** Latest AI/ML research updates and insights
**Global:** Available across all projects


---

## 🎛️ Slash Commands

### **Project Analysis**
- `/prime` - Project analysis and understanding
- `/prime_tts` - Project analysis with TTS summary
- `/question` - Answer questions about project without coding
- `/git_status` - Current git repository state

### **Documentation**
- `/changelog_update` - Update documentation (CHANGELOG.md, README.md, CHEATSHEET.md) from recent commits
- `/changelog_update 20` - Analyze last 20 commits and update all relevant documentation


### **AI Research**
- `/ai_research` - Latest AI/ML research and developments

### **System Management**
- `/sentient` - Demo dangerous command blocking (rm -rf test)
- `/update_status_line` - Configure custom status line metadata

### **Development**
- `/all_tools` - List all available Claude Code tools
- `/cook` - Advanced development workflows
- `/cook_research_only` - Research-focused development

---

## 🎨 Output Styles (8 Available)

**Usage:** `/output-style [name]`

| Style | Description | Best For |
|-------|-------------|----------|
| **genui** ⭐ | **Complete HTML with embedded styling, auto-opens browser** | **Interactive visuals, professional docs** |
| **table-based** | Organizes info in markdown tables | Comparisons, structured data |
| **yaml-structured** | YAML configuration format | Settings, API responses |
| **bullet-points** | Clean nested lists | Action items, documentation |
| **ultra-concise** | Minimal words, maximum speed | Rapid prototyping |
| **html-structured** | Semantic HTML5 with data attributes | Web documentation |
| **markdown-focused** | Full markdown feature utilization | Complex documentation |
| **tts-summary** | ElevenLabs TTS announcements | Audio feedback |

---

## 📊 Status Lines (4 Versions)

**Configuration:** Set in `.claude/settings.json`

| Version | Features |
|---------|----------|
| **v1** | Basic: Git branch, directory, model info |
| **v2** | Smart prompts with color-coded task types |
| **v3** | Agent sessions with last 3 prompts |
| **v4** | Extended metadata with custom key-value pairs |

**Global Session Benefits:**
- Cross-project persistence in `~/.claude/data/sessions/`
- Unified agent identity with auto-generated names
- Custom metadata support (`/update_status_line`)

---

## 🔧 Utility Features

### **TTS System (3 Providers)**
Priority: ElevenLabs → OpenAI → pyttsx3 (local fallback)

### **LLM Integration (3 Providers)**
- OpenAI (via `utils/llm/oai.py`)
- Anthropic (via `utils/llm/anth.py`)
- Ollama (via `utils/llm/ollama.py`)

### **Quality Gates** - `quality_gates.py`
Automated validation and testing integration

### **UV Single-File Scripts**
All hooks use UV for fast, isolated dependency management

---

## 🚀 Quick Start Examples

### Get Started with Monday.com
1. Set API token: `export MONDAY_API_TOKEN="your_token"`
2. List boards: `/monday_boards`
3. Daily report: `/monday_daily_report --board-ids BOARD_ID`
4. Team workload: `/monday_workload`

### Create a New Agent
```bash
"Build a sub-agent that analyzes code quality and suggests improvements"
# Meta-agent automatically creates the new agent file
```


### Enable Advanced Logging
All hook events are logged to `logs/` directory in JSON format for analysis and debugging.

---

## 📁 Directory Structure

```
.claude/
├── agents/           # Sub-agent configurations
├── commands/         # Slash command definitions
├── hooks/           # Hook implementations (Python UV scripts)
├── output-styles/   # Response formatting styles
├── status_lines/    # Terminal status line scripts
└── settings.json    # Main configuration

logs/               # JSON logs from all hook executions
outputs/           # Generated reports and analysis
ai_docs/           # Documentation resources
```

---

## 🎯 Pro Tips

1. **Hook Priority:** UserPromptSubmit → PreToolUse → PostToolUse for security layers
2. **Agent Chaining:** Claude automatically chains agents for complex workflows
3. **Global Sessions:** Session data persists across all Claude Code projects
4. **Parallel Execution:** Most commands run agents in parallel for speed
5. **Security First:** Multiple validation layers prevent dangerous operations
6. **TTS Feedback:** Rich audio feedback keeps you informed of progress

---

*🔗 For detailed documentation, see the [main README.md](README.md) and [official Claude Code docs](https://docs.anthropic.com/en/docs/claude-code)*