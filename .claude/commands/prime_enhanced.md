---
allowed-tools: Bash, Read, Glob
description: Enhanced project analysis with comprehensive codebase understanding including architecture, dependencies, and implementation patterns
---

# Prime Enhanced

Comprehensive project analysis that goes beyond documentation to understand technical architecture, dependencies, implementation patterns, and development workflows.

## Execute

### Repository Structure
- `git ls-files | head -50`
- `ls -la`
- `find . -type f -name "*.json" -o -name "*.toml" -o -name "*.yaml" -o -name "*.yml" | head -10`

### Dependency Analysis
- `find . -name "package.json" -o -name "requirements.txt" -o -name "Cargo.toml" -o -name "go.mod" -o -name "pyproject.toml"`
- `find . -name "*.py" -exec head -10 {} \; | grep -E "^# ///" | head -5`

### Entry Points & Configuration
- `find . -name "main.*" -o -name "index.*" -o -name "app.*" -o -name "__init__.py" | head -10`
- `find . -name "Makefile" -o -name "docker-compose.yml" -o -name ".env.example"`

### Code Patterns (Sample Analysis)
- `find . -name "*.py" | head -5`
- `find . -name "*.js" -o -name "*.ts" | head -5`
- `find . -name "*.go" -o -name "*.rs" -o -name "*.java" | head -5`

## Read

### Core Documentation
- README.md
- CHANGELOG.md
- CHEATSHEET.md (if exists)

### Configuration Files
- .claude/settings.json (if exists)
- package.json (if found)
- requirements.txt (if found)
- pyproject.toml (if found)
- Cargo.toml (if found)
- go.mod (if found)

### Key Implementation Files
- Any main/index/app entry point files found
- Top 2-3 Python files from different directories
- Any Makefile or docker-compose.yml found
- .env.example (if exists)

### Architecture Files
- Any files named *config*, *settings*, or *constants*
- Any API or schema definition files

## Report

Provide a comprehensive technical analysis including:

### Project Overview
- Primary purpose and domain
- Technology stack and frameworks
- Architecture type (monolith, microservices, library, etc.)

### Technical Architecture
- Programming languages used
- Key dependencies and their purposes
- Build system and package management
- Entry points and execution flow

### Development Workflow
- How to build/run the project
- Testing framework and approach
- Deployment method
- Development tools and utilities

### Code Organization
- Directory structure and conventions
- Module/package organization
- Configuration management approach
- Data flow and component interactions

### Key Insights
- Notable patterns or architectural decisions
- Potential areas for improvement
- Security considerations observed
- Performance characteristics