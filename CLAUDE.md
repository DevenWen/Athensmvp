# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Athens MVP (思辨广场MVP) is an AI-powered debate platform featuring dual AI agents - a Logician (逻辑者) and a Skeptic (怀疑者) - that engage in structured debates on user-provided topics.

### Architecture Components

The system consists of 5 main layers:

1. **Foundation Layer** (`src/core/`, `src/config/`)
   - OpenRouter AI client wrapper (`ai_client.py`) 
   - Environment configuration management (`settings.py`)
   - Base infrastructure and error handling

2. **Agent Layer** (`src/agents/`)
   - `BaseAgent`: Abstract base class for all AI agents
   - `Logician`: Logic-focused agent that builds supportive arguments
   - `Skeptic`: Critical thinking agent that challenges and questions
   - Role-specific prompts and personality definitions (`src/config/prompts.py`)

3. **Communication Layer** (`src/core/`)
   - `Message`: Structured message format with metadata and references
   - `Conversation`: Dialog history management and context tracking
   - `Communication`: Message routing and agent-to-agent messaging
   - `ContextManager`: Intelligent context window management for AI models

4. **Debate Management** (`src/core/`)
   - `DebateManager`: Core debate flow control and orchestration
   - Turn-based conversation management between agents
   - Support for both observation mode (automated) and participation mode (user interactive)
   - Intelligent debate termination conditions

5. **User Interface** (`src/ui/`)
   - Rich CLI interface with colored output and real-time updates
   - `CommandProcessor`: Handles user commands (`/pause`, `/end`, `@agent message`)
   - Support for user participation during debates via @mentions
   - Real-time debate progress visualization

### Key Dependencies (requirements.txt)

- `openai>=1.0.0` - OpenRouter compatible client
- `python-dotenv` - Environment variable management  
- `rich` - Enhanced CLI output formatting
- `pydantic>=2.0.0` - Data validation and serialization
- `pytest` - Testing framework

### Development Commands

Since this is a Python project without implemented code yet, common commands will be:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python src/main.py

# Run tests  
pytest

# Run linting (once implemented)
ruff check src/
flake8 src/

# Type checking (once implemented)
mypy src/
```

### Project Structure

```
athens_mvp/
├── src/
│   ├── agents/          # AI agent implementations
│   ├── core/           # Core systems (AI client, messaging, debate management)
│   ├── ui/             # User interface components
│   ├── config/         # Configuration and prompts
│   └── main.py         # Application entry point
├── docs/
│   ├── tasks/          # Implementation task specifications
│   └── work_logs/      # Development work logs (YYYY_MM_DD_*.md format)
├── reports/            # Generated debate reports
└── tests/              # Test files
```

### Message Types and Flow

The system uses structured messages with types:
- `ARGUMENT`: Logical arguments and supporting evidence
- `COUNTER`: Counter-arguments and rebuttals  
- `CLARIFICATION`: Clarifying questions or explanations
- `SUMMARY`: Summary statements
- `USER_INPUT`: User contributions to the debate

### Development Notes

- All work logs must be created in `docs/work_logs/` using format `YYYY_MM_DD_{title}.md`
- The system supports both Chinese and English interfaces
- Focus on defensive security - this is an educational debate tool, not for malicious use
- Agent personalities are defined through carefully crafted system prompts
- Context management is crucial for maintaining coherent long-form debates
- The CLI interface uses Rich library for enhanced visual presentation

### Testing Strategy

- Unit tests for individual components (agents, messaging, debate management)
- Integration tests for agent-to-agent communication
- End-to-end tests for complete debate scenarios  
- 使用 `python3` 作为 bash 命令 


## Stage
[x] 01_foundation
[x] 02_agents
[x] 03_messaging
[x] 04_debate_manager
[ ] 05_user_interface