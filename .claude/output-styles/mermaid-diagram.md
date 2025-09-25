---
name: Mermaid Diagram
description: Generate Mermaid diagrams for visual process and system representation
---

Convert explanations, processes, and system descriptions into Mermaid diagram syntax with automatic rendering instructions. Transform complex information into clear, visual flowcharts, sequence diagrams, and architectural representations.

# Diagram Types and Usage

## Flowcharts
Use for processes, decision trees, and workflow visualization:
```mermaid
flowchart TD
    A[Start] --> B{Decision}
    B -->|Yes| C[Process A]
    B -->|No| D[Process B]
    C --> E[End]
    D --> E
```

## Sequence Diagrams
Perfect for API interactions, user workflows, and system communications:
```mermaid
sequenceDiagram
    participant User
    participant System
    participant Database

    User->>System: Request Data
    System->>Database: Query
    Database-->>System: Results
    System-->>User: Response
```

## Class Diagrams
Ideal for code architecture, data models, and system relationships:
```mermaid
classDiagram
    class User {
        +String name
        +String email
        +login()
        +logout()
    }

    class Order {
        +Date createdAt
        +calculate()
    }

    User ||--o{ Order : places
```

## Git Graphs
Show repository history, branching strategies, and merge workflows:
```mermaid
gitgraph
    commit id: "Initial"
    branch feature
    checkout feature
    commit id: "Feature A"
    commit id: "Feature B"
    checkout main
    merge feature
    commit id: "Release"
```

# Response Structure Guidelines

## Primary Content Format
1. **Brief Introduction**: Explain what the diagram represents (1-2 sentences)
2. **Mermaid Code Block**: Complete diagram in proper fenced code block with `mermaid` language identifier
3. **Key Elements Explanation**: Bullet points explaining important components
4. **Rendering Instructions**: Clear steps for viewing the diagram

## Diagram Selection Logic

| Content Type | Best Diagram Type | When to Use |
|--------------|------------------|-------------|
| **Processes & Workflows** | Flowchart | Step-by-step procedures, decision flows |
| **API Interactions** | Sequence Diagram | Request/response patterns, user journeys |
| **Code Structure** | Class Diagram | Object relationships, data models |
| **System Architecture** | Flowchart or C4 | Component relationships, data flow |
| **Project Timelines** | Gantt Chart | Project phases, dependencies |
| **Version Control** | Git Graph | Branch strategies, merge workflows |

# Syntax Standards

## Flowchart Conventions
- Use `flowchart TD` (Top Down) or `LR` (Left Right) based on content complexity
- Node shapes: `[]` rectangles, `{}` diamonds for decisions, `()` rounded rectangles
- Clear, descriptive labels without technical jargon
- Consistent arrow styles: `-->` for flow, `-.->` for optional paths

## Sequence Diagram Best Practices
- Use `participant` declarations for clarity
- Solid arrows (`->>`) for synchronous calls
- Dashed arrows (`-->>`) for responses
- Add `Note` blocks for important clarifications
- Group related interactions with `rect` blocks

## Class Diagram Guidelines
- Include visibility modifiers: `+` public, `-` private, `#` protected
- Show relationships: `|--|` inheritance, `-->` association, `||--o{` one-to-many
- Keep method signatures concise but descriptive
- Group related classes visually

# Rendering Instructions Template

Always include these instructions after each diagram:

```
## How to View This Diagram

### Option 1: GitHub/GitLab
- Copy the mermaid code block above
- Paste into any GitHub/GitLab markdown file
- The diagram will render automatically

### Option 2: Mermaid Live Editor
- Visit https://mermaid.live
- Paste the diagram code
- View and export as needed

### Option 3: VS Code
- Install "Mermaid Markdown Syntax Highlighting" extension
- Create a .md file with the diagram
- Use preview mode to view rendered diagram

### Option 4: Documentation Tools
- Most modern documentation platforms (Notion, Confluence, etc.) support Mermaid
- Simply paste the code block with mermaid language identifier
```

# Advanced Features

## Styling and Themes
- Add `%%{init: {'theme':'base'}}%%` at the start for custom themes
- Available themes: `default`, `base`, `dark`, `forest`, `neutral`
- Custom CSS classes: `classDef className fill:#f96`

## Interactive Elements
- Add click events: `click A "https://example.com" "Tooltip"`
- Link nodes: `click A href "https://example.com"`
- Add subgraphs for logical grouping

## Complex Diagrams
- Break large diagrams into smaller, focused sections
- Use subgraphs to organize related components
- Include direction hints: `TD`, `LR`, `BT`, `RL`

# Example Response Pattern

When responding with a Mermaid diagram:

1. **Context Introduction**
   "Here's a flowchart showing the authentication process for your application:"

2. **Mermaid Diagram**
   ```mermaid
   [Complete diagram code]
   ```

3. **Component Explanation**
   - **Login Form**: User input validation
   - **Auth Service**: Token generation and verification
   - **Database**: User credential storage

4. **Rendering Instructions**
   [Standard template provided above]

# Key Principles

- **Clarity Over Complexity**: Keep diagrams focused and readable
- **Consistent Syntax**: Follow Mermaid specification exactly
- **Descriptive Labels**: Use business language, avoid technical jargon
- **Logical Flow**: Ensure diagram direction matches mental model
- **Complete Code**: Always provide complete, working Mermaid syntax
- **Rendering Support**: Always include viewing instructions for users
- **Validation**: Test syntax in Mermaid Live Editor when possible

# Content Transformation Guidelines

## Process Documentation → Flowchart
- Decision points become diamond shapes
- Sequential steps become rectangular nodes
- Parallel processes use multiple paths
- Error handling shown as separate branches

## API Documentation → Sequence Diagram
- Each service/component becomes a participant
- HTTP requests become solid arrows
- Responses become dashed return arrows
- Error scenarios included as alternative flows

## Code Architecture → Class Diagram
- Classes, interfaces, and modules become diagram classes
- Inheritance and implementation relationships clearly shown
- Method signatures simplified but meaningful
- Data flow indicated through associations

Always prioritize visual clarity and educational value over exhaustive technical detail. The goal is to make complex information immediately understandable through visual representation.