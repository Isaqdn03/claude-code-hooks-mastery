---
allowed-tools: Bash, Read, Edit, Write
description: Update project documentation to reflect recent code changes using the changelog-updater agent
---

# Changelog Update Command

This command uses the @agent-changelog-updater to analyze recent git commits and update project documentation (CHANGELOG.md and README.md) to reflect code changes.

## Variables

- `$ARGUMENTS` - Optional: Number of commits to analyze (default: recent commits)

## Instructions

1. **Analyze Recent Changes**
   - Run `git log --oneline -10` (or $ARGUMENTS number) to see recent commits
   - Run `git status` to check current repository state
   - Run `git diff HEAD~5..HEAD --name-only` to see modified files

2. **Delegate to Changelog-Updater Agent**
   - Use the @agent-changelog-updater to analyze the changes
   - Provide context about recent commits and modified files
   - Let the agent determine what documentation updates are needed

3. **Agent Instructions**
   Pass this context to the changelog-updater agent:
   - Recent git commits and their messages
   - List of modified files
   - Current repository status
   - Request to update CHANGELOG.md and README.md as appropriate

## Workflow

1. Gather git history and change information
2. Invoke the changelog-updater agent with the collected context
3. Let the agent analyze changes and update documentation
4. Review and confirm changes before finalizing

## Usage Examples

```bash
/changelog                    # Analyze last 10 commits
/changelog 20                # Analyze last 20 commits
/changelog                   # Update docs after feature completion
```

## Report

The changelog-updater agent will:
- Analyze recent commits and file changes
- Update or create CHANGELOG.md following Keep a Changelog format
- Update README.md if changes affect user-facing functionality
- Categorize changes appropriately (Added, Changed, Fixed, etc.)
- Present changes for review before finalizing