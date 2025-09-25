# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

The Adaptive Chatbot is a comprehensive multilingual AI system with advanced NLP capabilities, voice interface, and intelligent business domain specialization. It's designed as a production-ready conversational AI platform with support for 50+ languages, EdgeTTS voice synthesis, and specialized electrical business knowledge.

### Core Architecture

The system follows a sophisticated modular architecture with multiple integration layers:

**Main Application Layer:**
- **`AdaptiveChatbot`** - Primary orchestrator with comprehensive error handling
- **`EnhancedAdaptiveChatbot`** - Advanced version with multilingual support
- **`main_adaptive_chatbot.py`** - Complete system integration script

**Intelligence Layer:**
- **`advanced_nlp.py`** - Transformer-based NLP engine with sentiment analysis
- **`intelligent_integration_bridge.py`** - Multi-system response prioritization
- **`free_ai_models_integration.py`** - Hugging Face transformers integration
- **`electrical_business_enhancer.py`** - Domain-specific business logic

**Voice Interface Layer:**
- **`multilingual_edgetts_integration.py`** - EdgeTTS multilingual speech synthesis
- **`enhanced_voice_interface.py`** - Advanced voice recognition and processing
- **`voice_tone_style_adaptation.py`** - Context-aware voice personality system
- **`multilingual_voice_system.py`** - Language-appropriate voice selection

**Data Management:**
- **`unified_learning_manager.py`** - Centralized knowledge management
- **`advanced_conversation_manager.py`** - Session and context management
- **`KnowledgeStore`** - SQLite with semantic search and FAISS indexing

**Language Processing:**
- **`enhanced_language_detection.py`** - 50+ language detection with confidence scoring
- **`advanced_multilingual_bridge.py`** - Cross-language communication handling
- **`transliteration.py`** - Script conversion and romanization

### Knowledge System

The chatbot uses a dual-approach knowledge retrieval system:
1. **Primary**: Sentence transformer embeddings (all-MiniLM-L6-v2) with cosine similarity
2. **Fallback**: Keyword-based search with relevance scoring

Knowledge entries support:
- Domain segregation (shop, general, tech, personal)
- Category organization within domains
- Usage tracking and confidence scoring
- Metadata storage for extensibility

### Voice Interface

The system includes comprehensive voice capabilities for hands-free interaction:
- **Speech Recognition**: Multi-language support (Hindi, English) using Google Speech Recognition
- **Text-to-Speech**: Dual TTS engines - Google TTS (gTTS) for better language support or local pyttsx3
- **Bilingual Communication**: Seamless Hindi-English mixed conversations
- **Adaptive Recognition**: Fallback through multiple language models for better accuracy
- **Voice Commands**: All interactive chat commands work via voice (teach, domain switching, etc.)

## Development Commands

### Environment Setup
```pwsh
# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install core dependencies (minimal setup)
pip install -r requirements-fixed.txt

# OR install all dependencies (full AI/ML features)
pip install -r requirements.txt  # if available

# Verify installation
python test_all_dependencies.py
```

### Running the Chatbot

**Main Launch Options:**
```pwsh
# Full integrated system with all features
python main_adaptive_chatbot.py

# Enhanced chatbot with multilingual support
python adaptive_chatbot_enhanced.py

# AI-powered launcher with dependency checking
python launch_ai_chatbot.py

# Multi-language specialized launcher
python launch_multilingual_ai.py
```

**Core Functionality:**
```pwsh
# Basic adaptive chatbot (lightweight)
python adaptive_chatbot.py

# Text-only chat interface
python text_chat.py

# Voice chat with EdgeTTS
python voice_chat.py

# Interactive voice teaching mode
python interactive_voice_teaching.py
```

**CLI Interface (if available):**
```pwsh
# Traditional CLI commands (if src/ structure exists)
python -m src.cli chat --domain shop

# Teaching via command line
python -m src.cli teach "switch price" "15-25 rupees" --domain shop
```

### Testing and Development Tools
```pwsh
# Comprehensive dependency testing
python test_all_dependencies.py

# Test specific components
python test_audio_deps.py          # Audio system testing
python test_dependencies.py        # Core dependencies
python test_advanced_nlp.py        # NLP engine testing

# Quick system verification
python quick_test.py

# System health monitoring
python system_health_check.py

# Audio voice demo
python voice_demo.py
```

### Development and Demo Tools
```pwsh
# Demo applications
python demo_chatbot.py              # Basic demo
python demo_enhanced_chatbot.py     # Advanced features demo
python demo_text_chatbot.py         # Text-only demo

# Debugging and monitoring
python advanced_debugger_tracker.py # Debug session tracking
python desktop_monitor_app.py       # System monitoring

# Web interface (if available)
python web_interface_app.py         # FastAPI web server
```

### Business and Integration Tools
```pwsh
# Professional installer creation
python build_professional_installer.py

# License management
python license_activation.py

# Package creation
python create_package.py

# Marketing materials generation
python marketing_materials.py

# Documentation generation
python documentation_generator.py
```

## Interactive Chat Commands

During chat sessions, users can use these special commands:
- `teach: <question> | <answer>` - Teach new knowledge inline
- `domain: <domain_name>` - Switch conversation domain
- `stats` - Display knowledge statistics
- `help` - Show available commands

## Architecture Deep Dive

### Advanced Message Processing Pipeline

1. **Intelligent Input Processing**: 
   - Multi-language detection with confidence scoring
   - Automatic script transliteration (Devanagari ↔ Roman)
   - Intent classification using transformer models
   - Sentiment analysis with TextBlob and advanced NLP

2. **Multi-System Response Generation**:
   - Primary: Transformer-based response generation
   - Secondary: Semantic knowledge base search (sentence-transformers + FAISS)
   - Tertiary: Electrical business domain expertise
   - Fallback: Rule-based template responses

3. **Voice Processing Integration**:
   - EdgeTTS multilingual speech synthesis with 200+ voices
   - Context-aware voice personality selection (Professional, Friendly, etc.)
   - Real-time speech recognition with multiple language models
   - Audio stream processing and noise handling

4. **Advanced Conversation Management**:
   - Session-based conversation tracking
   - Multi-turn dialogue state management
   - Topic continuity and context switching
   - User preference learning and adaptation

### Multilingual Intelligence System

The system handles 50+ languages through:
- **Language Detection**: Confidence-scored detection with cultural context
- **Cross-Language Bridging**: Seamless mixing of Hindi, English, and regional languages
- **Voice Synthesis**: Language-appropriate voice selection and pronunciation
- **Cultural Adaptation**: Context-aware responses for different linguistic backgrounds

### Business Domain Specialization

**Electrical/Electronics Domain**:
- Product identification and categorization
- Price inquiry handling with market rate knowledge
- Technical specification responses
- Installation and service guidance
- Warranty and policy information

**Extensible Domain Framework**:
- Plug-and-play domain modules
- Domain-specific NLP models
- Custom voice personalities per domain
- Business rule integration

### Data Architecture

**Multi-tier Storage System**:
- **Primary**: SQLite with FTS (Full-Text Search) indexes
- **Semantic**: FAISS vector database for embeddings
- **Cache**: In-memory conversation state and user preferences
- **Backup**: JSON export/import for knowledge portability

**Advanced Indexing**:
- Semantic similarity indexes using sentence-transformers
- Language-specific keyword indexes
- Usage frequency tracking for response optimization
- Multi-dimensional vector space for context clustering

## Configuration Management

Configuration is managed through `config/config.yaml` with comprehensive system settings:

### Core System Settings
```yaml
sentence_model_name: all-MiniLM-L6-v2    # Transformer model for embeddings
confidence_threshold: 0.7                 # Minimum similarity for knowledge matching
max_context_length: 5                     # Conversation history window
max_knowledge_entries: 10000               # Database size limits
database_path: data/knowledge.db          # Knowledge storage location
default_domain: general                   # Fallback domain for new sessions
```

### Advanced Voice Configuration
```yaml
voice_enabled: true
use_gtts: true                           # Google TTS vs local pyttsx3
voice_language: hi-IN                    # Speech recognition language
tts_language: hi                         # Text-to-speech language
speech_rate: 150                         # TTS speaking rate (WPM)
energy_threshold: 300                    # Microphone sensitivity
timeout: 5                               # Speech input timeout
phrase_time_limit: 10                    # Max phrase duration
pause_threshold: 0.8                     # Speech pause detection
voice_id: 0                              # Default voice selection
```

### Domain and Learning Settings
```yaml
available_domains:
  - general
  - shop
  - tech
  - personal

auto_learn_enabled: false                # Automatic learning toggle
min_confidence_for_auto_learn: 0.9       # Auto-learning threshold
show_confidence_scores: false            # Debug confidence display
conversation_cleanup_days: 30            # History retention period
```

### System Optimization
```yaml
log_level: INFO                          # Logging verbosity
log_file: logs/chatbot.log              # Log file location
colorize_output: true                    # Colored terminal output
enable_conversation_logging: true        # Session logging toggle
max_response_length: 500                 # Response length limit
```

## Advanced Features Integration

### AI Model Integration

The system integrates multiple AI models:

**Transformers Integration** (`free_ai_models_integration.py`):
- Hugging Face transformers for conversation generation
- Microsoft DialoGPT for contextual responses
- Facebook BlenderBot for personality-driven chat
- Custom fine-tuned models for domain specialization

**NLP Processing** (`advanced_nlp.py`):
- Intent classification with confidence scoring
- Sentiment analysis for response tone adaptation
- Entity extraction for business domain queries
- Language detection supporting 50+ languages

### Voice Technology Stack

**EdgeTTS Integration** (`multilingual_edgetts_integration.py`):
- 200+ realistic AI voices across languages
- SSML support for advanced speech control
- Streaming audio for real-time interaction
- Voice personality matching to conversation context

**Speech Recognition** (`enhanced_voice_interface.py`):
- Multi-engine fallback (Google, Sphinx, Azure)
- Noise reduction and audio preprocessing
- Continuous listening with wake word detection
- Multi-language recognition with auto-switching

### Business Intelligence Features

**Electrical Domain Expertise** (`electrical_business_enhancer.py`):
- Product catalog integration
- Dynamic pricing information
- Technical specification matching
- Service request routing
- Inventory management integration

**Professional Tools**:
- License management system (`license_activation.py`)
- Professional installer creation (`build_professional_installer.py`)
- Marketing materials generation (`marketing_materials.py`)
- Monetization system integration (`monetization_system.py`)

## Development Guidelines

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

## Voice Interface and Multilingual Features

### Voice Interface Capabilities

The system provides comprehensive voice interaction through multiple components:

**EdgeTTS Integration** (`multilingual_edgetts_integration.py`):
- 200+ AI voices across 50+ languages
- Real-time streaming audio generation
- SSML support for advanced speech control (rate, pitch, emphasis)
- Context-aware voice personality selection

**Enhanced Voice Recognition** (`enhanced_voice_interface.py`):
- Multi-engine speech recognition with fallback
- Continuous listening with noise reduction
- Multi-language support with automatic language detection
- Voice activity detection and silence handling

**Voice Personality System** (`voice_tone_style_adaptation.py`):
- 12 distinct personalities (Professional, Friendly, Enthusiastic, etc.)
- Context-aware personality selection based on conversation tone
- User preference learning and adaptation
- Business scenario-appropriate voice matching

### Starting Voice-Enabled Sessions

```pwsh
# Interactive voice teaching mode
python interactive_voice_teaching.py

# Voice conversation interface
python voice_chat.py

# Enhanced voice interface with multilingual support
python enhanced_voice_interface.py

# Voice demo and testing
python voice_demo.py
```

### Multilingual Language Detection

The system automatically detects and handles 50+ languages:

**Language Detection Features** (`enhanced_language_detection.py`):
- Confidence-scored language detection
- Mixed language handling (Hinglish, Spanglish, etc.)
- Cultural context awareness
- Script transliteration support

**Cross-Language Communication** (`advanced_multilingual_bridge.py`):
- Seamless language switching mid-conversation
- Context preservation across languages
- Cultural adaptation for natural conversation flow
- Regional dialect recognition

## System Dependencies and Requirements

### Core Dependencies (Minimal Setup)

The `requirements-fixed.txt` contains minimal dependencies:
```
speechrecognition==3.10.0       # Voice input processing
pyttsx3==2.90                   # Local text-to-speech
gtts==2.4.0                     # Google Text-to-Speech
pygame==2.6.1                   # Audio playback
pywin32>=306                    # Windows integration (Windows only)
comtypes>=1.2.0                 # COM interface support (Windows only)
```

### Full AI/ML Dependencies

For complete functionality, the system supports:
- **PyTorch** with CUDA support for GPU acceleration
- **Transformers** (Hugging Face) for advanced NLP
- **Sentence-transformers** for semantic search
- **FAISS** for vector similarity search
- **Scikit-learn** for traditional ML features
- **EdgeTTS** for premium voice synthesis
- **FastAPI/Uvicorn** for web interface
- **Rich/Typer** for enhanced CLI experience

### Hardware Recommendations

**Minimum**:
- 4GB RAM
- 1GB storage space
- Audio input/output devices
- Windows 10+ or Linux

**Recommended**:
- 8GB+ RAM for full AI features
- NVIDIA GPU with CUDA support
- SSD storage for faster model loading
- Professional microphone for voice features

## File Structure Context

### Root Directory Structure
```
adaptive-chatbot/
├── main_adaptive_chatbot.py     # Primary system entry point
├── adaptive_chatbot_enhanced.py # Enhanced multilingual version
├── launch_ai_chatbot.py         # AI-powered launcher with dependency checking
├── launch_multilingual_ai.py    # Multi-language specialized launcher
├── config.py                    # Unified configuration system
├── logger.py                    # Centralized logging
├── validators.py                # Input validation and security
├── unified_learning_manager.py  # Knowledge management
└── requirements-fixed.txt       # Minimal dependencies
```

### Voice and Audio Components
```
voice_chat.py                   # Voice conversation interface
enhanced_voice_interface.py     # Advanced voice processing
multilingual_edgetts_integration.py # EdgeTTS voice synthesis
multilingual_voice_system.py    # Multi-language voice handling
voice_tone_style_adaptation.py  # Context-aware voice personalities
interactive_voice_teaching.py   # Voice-driven learning system
```

### AI and NLP Engine
```
advanced_nlp.py                 # Transformer-based NLP engine
free_ai_models_integration.py   # Hugging Face model integration
intelligent_integration_bridge.py # Multi-system response coordination
enhanced_language_detection.py  # Multi-language detection system
advanced_multilingual_bridge.py # Cross-language communication
transliteration.py              # Script conversion utilities
```

### Business and Professional Tools
```
electrical_business_enhancer.py # Domain-specific business logic
license_activation.py           # License management
monetization_system.py         # Commercial features
build_professional_installer.py # Deployment tools
marketing_materials.py         # Business material generation
```

### Data and Configuration
```
data/
├── knowledge_base.json         # Core knowledge storage
├── preloaded_knowledge.json    # Pre-built knowledge
└── shop_knowledge.json         # Electrical business knowledge (if exists)

config/
├── config.yaml                 # Main configuration
└── [domain-specific configs]   # Domain configurations

logs/
└── chatbot.log                 # System logs
```

## Bilingual Language Support

The system is designed for Hindi-English code-mixed conversations:
- Response templates use natural Hindi-English mixing
- Keyword extraction handles both languages
- Stop words include common Hindi words
- Default responses are culturally appropriate

When adding new knowledge or domains, maintain this bilingual approach for consistency with existing patterns.

## Common Development Tasks

### Adding New AI Models

1. **Register in `free_ai_models_integration.py`**:
```python
from transformers import AutoModel, AutoTokenizer

def load_custom_model(model_name):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)
    return model, tokenizer
```

2. **Integrate with intelligent bridge**:
```python
# In intelligent_integration_bridge.py
def process_with_custom_model(query, model):
    # Add custom model processing logic
    pass
```

### Creating New Voice Personalities

1. **Define in `voice_tone_style_adaptation.py`**:
```python
VOICE_PERSONALITIES = {
    "custom_personality": {
        "voice_name": "en-US-AriaNeural",
        "speed": "medium",
        "pitch": "default",
        "style": "cheerful"
    }
}
```

2. **Register with EdgeTTS integration**:
```python
# In multilingual_edgetts_integration.py
def apply_personality(text, personality):
    # Apply SSML tags based on personality
    pass
```

### Extending Business Domain Logic

1. **Create domain-specific enhancer**:
```python
# new_domain_enhancer.py
class NewDomainEnhancer:
    def __init__(self):
        self.domain_knowledge = self.load_domain_data()
    
    def process_query(self, query):
        # Domain-specific processing logic
        return enhanced_response
```

2. **Register in intelligent bridge**:
```python
# Add to response priority system
DOMAIN_ENHANCERS = {
    "new_domain": NewDomainEnhancer()
}
```

## Performance Considerations

### System Optimization

**Model Loading**:
- Pre-load frequently used models at startup
- Use model caching to avoid repeated downloads
- Consider model quantization for memory efficiency
- GPU acceleration with CUDA when available

**Voice Processing**:
- EdgeTTS streaming for real-time audio generation
- Audio buffer management for smooth playback
- Voice recognition timeout optimization
- Background model warm-up during idle time

**Knowledge Management**:
- FAISS indexing for semantic search acceleration
- SQLite FTS indexes for keyword search
- Conversation history pruning (configurable retention)
- Batch knowledge imports for large datasets

**Memory Management**:
- Transformer models: ~500MB-2GB depending on size
- Voice models: ~100-500MB for EdgeTTS cache
- Embedding cache: ~50MB per 10,000 knowledge entries
- Session data: ~1-5MB per active conversation

### Troubleshooting Common Issues

**Dependency Problems**:
```pwsh
# Test all dependencies
python test_all_dependencies.py

# Test specific audio components
python test_audio_deps.py

# Quick system health check
python system_health_check.py
```

**Voice Interface Issues**:
- Check Windows microphone permissions
- Adjust `energy_threshold` in config for different microphones
- Test EdgeTTS connectivity: `python voice_demo.py`
- Verify audio device selection in `config.yaml`

**Model Loading Failures**:
- Clear Hugging Face cache: `~/.cache/huggingface/`
- Check internet connectivity for model downloads
- Verify sufficient disk space for model storage
- Use `test_advanced_nlp.py` to isolate NLP issues

**Performance Issues**:
- Monitor system resources with `desktop_monitor_app.py`
- Enable GPU acceleration if available
- Reduce model complexity for lower-spec systems
- Adjust conversation history limits in configuration

## Extension Points and Integration

The codebase provides multiple integration layers:

1. **Multi-Model AI Integration**: Add custom AI models through `free_ai_models_integration.py`
2. **Business Domain Expansion**: Create domain-specific enhancers following `electrical_business_enhancer.py`
3. **Voice Technology**: Extend voice capabilities via `multilingual_edgetts_integration.py`
4. **Web Interface**: FastAPI foundation available in `web_interface_app.py`
5. **Professional Tools**: Commercial features framework in `monetization_system.py`
6. **Cross-Platform Deployment**: Installer creation tools in `build_professional_installer.py`

<citations>
<document>
    <document_type>WARP_DOCUMENTATION</document_type>
    <document_id>getting-started/quickstart-guide/coding-in-warp</document_id>
</document>
</citations>
