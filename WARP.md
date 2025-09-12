# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

The Adaptive Chatbot is a bilingual (Hindi-English) conversational AI that can learn and remember information from user interactions. It's designed primarily for domain-specific use cases, with pre-built support for electrical/electronics shops, while being extensible to other domains.

### Core Architecture

The system follows a modular design with clear separation of concerns:

- **`AdaptiveChatbot`** - Main orchestrator that processes messages and generates responses
- **`KnowledgeStore`** - SQLite-based persistent storage with semantic search capabilities  
- **`LearningManager`** - Handles knowledge import, teaching, and interactive learning
- **`Config`** - YAML-based configuration management with domain-specific settings

### Knowledge System

The chatbot uses a dual-approach knowledge retrieval system:
1. **Primary**: Sentence transformer embeddings (all-MiniLM-L6-v2) with cosine similarity
2. **Fallback**: Keyword-based search with relevance scoring

Knowledge entries support:
- Domain segregation (shop, general, tech, personal)
- Category organization within domains
- Usage tracking and confidence scoring
- Metadata storage for extensibility

## Development Commands

### Environment Setup
```pwsh
# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Initial setup (creates directories and loads sample data)
python -m src.cli setup
```

### Running the Chatbot
```pwsh
# Start interactive chat (general domain)
python -m src.cli chat

# Start with specific domain
python -m src.cli chat --domain shop
```

### Knowledge Management
```pwsh
# Teach single knowledge entry
python -m src.cli teach "switch ki price" "Switch 15-25 rupees mein milta hai" --domain shop

# Import knowledge from JSON file
python -m src.cli import-knowledge data/my_knowledge.json --domain general

# Export knowledge to JSON
python -m src.cli export-knowledge exported.json --domain shop

# View statistics
python -m src.cli stats
```

### Testing and Code Quality
```pwsh
# Run tests (when test suite exists)
python -m pytest tests/

# Code formatting
black src/

# Linting
flake8 src/

# Type checking
mypy src/
```

## Interactive Chat Commands

During chat sessions, users can use these special commands:
- `teach: <question> | <answer>` - Teach new knowledge inline
- `domain: <domain_name>` - Switch conversation domain
- `stats` - Display knowledge statistics
- `help` - Show available commands

## Architecture Deep Dive

### Message Processing Flow

1. **Input Cleaning**: Text normalization and preprocessing
2. **Context Management**: Conversation history maintenance (max 5 exchanges)
3. **Knowledge Retrieval**: Semantic search followed by keyword fallback
4. **Response Generation**: Template-based with confidence scoring
5. **Learning Integration**: Usage tracking and feedback processing

### Domain System

Domains are completely isolated knowledge spaces with their own:
- Greeting messages and response templates
- Category hierarchies for organization
- Default fallback responses
- Confidence thresholds and learning parameters

Pre-configured domains:
- **shop**: Electrical/electronics retail (Hindi-English mixed)
- **general**: Open-ended conversations
- **tech**: Technology and programming topics

### Database Schema

SQLite database with two main tables:
- **knowledge**: Stores input-response pairs with metadata
- **conversations**: Logs chat sessions for analytics

Key indexes on domain, category, and input fields for performance.

## Configuration Management

Configuration is managed through `config/config.yaml` with these key sections:

### Model Settings
- `sentence_model_name`: Transformer model for embeddings
- `confidence_threshold`: Minimum similarity for knowledge matching
- `max_context_length`: Conversation history window

### Learning Settings
- `auto_learn_enabled`: Automatic learning from high-confidence interactions
- `max_knowledge_entries`: Database size limits
- `min_confidence_for_auto_learn`: Threshold for automatic knowledge capture

### Domain Settings
- `available_domains`: List of supported domains
- `default_domain`: Fallback domain for new sessions

## Development Guidelines

### Adding New Domains

1. Add domain to `available_domains` in config
2. Create domain-specific knowledge files in JSON format
3. Add greeting and response templates in `config.py`
4. Import initial knowledge: `python -m src.cli import-knowledge data/domain.json --domain new_domain`

### Knowledge File Format

```json
[
  {
    "input": "user question or input pattern",
    "response": "bot response template", 
    "category": "organizational category",
    "domain": "target domain",
    "confidence": 1.0,
    "metadata": {"tags": ["tag1", "tag2"]}
  }
]
```

### Extending Learning Capabilities

The `LearningManager` class supports:
- **Batch learning**: Import multiple knowledge entries
- **Interactive learning**: Learn from user feedback during conversations
- **Knowledge validation**: Mark entries as correct/incorrect
- **Usage analytics**: Track which knowledge is most/least used

### Adding New CLI Commands

Use the Typer framework pattern in `cli.py`:

```python
@app.command()
def new_command(
    param: str = typer.Argument(..., help="Description"),
    option: str = typer.Option("default", help="Option description")
):
    """Command description."""
    # Implementation
```

## File Structure Context

```
src/
├── chatbot.py          # Main AdaptiveChatbot class with message processing
├── knowledge_store.py  # SQLite database operations and search
├── learning.py         # LearningManager for training and feedback
├── config.py           # Configuration management and domain settings
└── cli.py              # Command-line interface with Typer

data/
├── shop_knowledge.json # Pre-built electrical shop knowledge base
└── knowledge.db        # SQLite database (auto-created)

config/
└── config.yaml         # Main configuration file (auto-created)
```

## Bilingual Language Support

The system is designed for Hindi-English code-mixed conversations:
- Response templates use natural Hindi-English mixing
- Keyword extraction handles both languages
- Stop words include common Hindi words
- Default responses are culturally appropriate

When adding new knowledge or domains, maintain this bilingual approach for consistency with existing patterns.

## Performance Considerations

- **Embedding Model**: all-MiniLM-L6-v2 balances accuracy with speed
- **Knowledge Retrieval**: Cached embeddings recommended for production
- **Database**: SQLite suitable for single-user applications; consider PostgreSQL for multi-user
- **Memory Usage**: Sentence transformer model requires ~100MB RAM
- **First Run**: Initial model download may take several minutes

## Extension Points

The codebase is designed for extensibility:

1. **Custom Knowledge Sources**: Extend `KnowledgeStore` for different databases
2. **Advanced NLP**: Replace/enhance sentence transformer with custom models  
3. **Web Interface**: FastAPI dependencies already included in requirements
4. **Multi-user Support**: Add user authentication and session management
5. **Voice Interface**: Integrate speech recognition/synthesis
6. **Analytics Dashboard**: Build on existing conversation logging

<citations>
<document>
    <document_type>WARP_DOCUMENTATION</document_type>
    <document_id>getting-started/quickstart-guide/coding-in-warp</document_id>
</document>
</citations>
