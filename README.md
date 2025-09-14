# 🤖 Adaptive Chatbot - Complete Multilingual AI Experience

An advanced conversational AI system with multilingual support, adaptive voice personalities, real-time voice visualization, and intelligent conversation management.

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![Platform](https://img.shields.io/badge/platform-windows%20|%20linux%20|%20macos-lightgrey.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 🌟 Features

### 🌐 **Multilingual Support**
- **Real-time language detection** with confidence scoring
- **Seamless language switching** mid-conversation
- Support for **12+ languages**: English, Hindi, Spanish, French, German, Italian, Portuguese, Chinese, Japanese, Korean, Arabic, Russian
- **Cultural adaptations** for natural conversation flow

### 🎭 **Adaptive Voice Personalities**
- **Dynamic personality selection** based on conversation context
- **12 distinct personalities**: Professional, Friendly, Enthusiastic, Calm, Empathetic, Confident, Warm, Authoritative, Cheerful, Patient, Energetic, Sophisticated
- **Context-aware voice adaptation** for different business scenarios
- **User preference learning** from feedback

### 🤖 **Free AI Models Integration**
- Integration with **Hugging Face transformers**
- Support for **conversational AI, question-answering, and text generation**
- **Microsoft DialoGPT**, **Facebook BlenderBot**, and other free models
- **Sentiment analysis** and **intent recognition**
- **Asynchronous model loading** for optimal performance

### 💬 **Advanced Conversation Management**
- **Persistent conversation memory** with SQLite storage
- **Topic tracking** and **conversation flow optimization**
- **User profiling** with conversation history
- **Session management** with analytics
- **Context-aware responses**

### 🎨 **Enhanced UI & Experience**
- **Real-time voice activity visualization**
- **Interactive conversation display** with rich formatting
- **Language indicators** with confidence scores
- **Voice control buttons** and settings panel
- **Conversation analytics** and export capabilities
- **Theme customization** support

### 🔊 **Natural Text-to-Speech**
- **Microsoft Edge TTS** integration for high-quality voices
- **Language-appropriate voice selection**
- **SSML support** for advanced speech control
- **Volume and speed controls**
- **Real-time audio visualization**

### 🛍️ Shop-Specific Features
- Pre-loaded knowledge about electrical and electronics items
- Price information for common products
- Service and warranty details
- Installation and delivery information

### 🔧 Technical Features
- CLI interface with rich formatting
- Configuration management
- Knowledge import/export
- Statistics and analytics
- Interactive teaching mode

## 📝 Requirements

- **Python 3.8+**
- **Windows/Linux/macOS**
- **4GB+ RAM** (for AI models)
- **Internet connection** (for TTS and model downloads)
- **Audio output device**
- **Microphone** (optional, for voice input)

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/adaptive-chatbot.git
cd adaptive-chatbot
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS  
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
python main_adaptive_chatbot.py
```

## Usage

### Interactive Chat

Start a chat session:
```bash
python -m src.cli chat
```

Start with a specific domain:
```bash
python -m src.cli chat --domain shop
```

### Teaching the Chatbot

Teach directly via command line:
```bash
python -m src.cli teach "switch ki price" "Switch 15-25 rupees mein milta hai" --domain shop
```

Teach during conversation:
```
You: hello
Bot: Hello! Main aapki kaise madad kar sakta hun?
You: teach: LED bulb kitne watt ka hai | LED bulb 9W, 12W, 15W mein available hai
Bot: ✅ Successfully learned!
```

### Knowledge Management

Import knowledge from JSON file:
```bash
python -m src.cli import-knowledge data/my_knowledge.json --domain shop
```

Export knowledge:
```bash
python -m src.cli export-knowledge exported_knowledge.json --domain shop
```

View statistics:
```bash
python -m src.cli stats
```

## Interactive Commands

While chatting, you can use these commands:

- `help` - Show available commands
- `stats` - Display chatbot statistics
- `teach: <question> | <answer>` - Teach new knowledge
- `domain: <domain_name>` - Switch domain
- `quit` / `exit` / `bye` - Exit chat

## Configuration

The chatbot uses `config/config.yaml` for configuration:

```yaml
# Database settings
database_path: data/knowledge.db

# Model settings
sentence_model_name: all-MiniLM-L6-v2
confidence_threshold: 0.7
max_context_length: 5

# Domain settings
default_domain: general
available_domains:
  - general
  - shop
  - tech
  - personal

# Learning settings
auto_learn_enabled: false
min_confidence_for_auto_learn: 0.9
max_knowledge_entries: 10000
```

## Domain-Specific Usage

### Electrical/Electronics Shop

The chatbot comes pre-loaded with knowledge for:

- **Products**: Switches, wires, bulbs, fans, MCBs, sockets
- **Pricing**: Current market rates for electrical items
- **Services**: Installation, warranty, delivery information
- **Brands**: Information about popular electrical brands

Example conversations:
```
You: switch ki price kitni hai
Bot: Switch ki price type ke hisaab se alag hoti hai. Normal 2-pin switch 15-25 rupees, 3-pin switch 20-30 rupees, modular switch 40-80 rupees mein milta hai.

You: wire ka rate
Bot: Wire ka rate size aur brand ke according hai. 1.5mm house wire 35-40 rupees per meter, 2.5mm wire 55-60 rupees per meter.
```

### General Domain

For general conversations and learning new topics:
```
You: teach: Python kya hai | Python ek programming language hai
Bot: ✅ Successfully learned!

You: Python kya hai
Bot: Python ek programming language hai
```

## Knowledge File Format

Knowledge can be imported from JSON files with this format:

```json
[
  {
    "input": "User question or input",
    "response": "Bot's response",
    "category": "Category name",
    "domain": "Domain name",
    "confidence": 1.0
  }
]
```

## Project Structure

```
adaptive-chatbot/
├── src/
│   ├── __init__.py
│   ├── chatbot.py          # Main chatbot class
│   ├── knowledge_store.py  # SQLite knowledge storage
│   ├── learning.py         # Learning mechanisms
│   ├── config.py           # Configuration management
│   └── cli.py              # Command-line interface
├── data/
│   ├── shop_knowledge.json # Pre-built shop knowledge
│   └── knowledge.db        # SQLite database (created automatically)
├── config/
│   └── config.yaml         # Configuration file
├── logs/
│   └── chatbot.log         # Log files
├── tests/                  # Unit tests (optional)
├── requirements.txt        # Python dependencies
├── .gitignore             # Git ignore rules
└── README.md              # This file
```

## Advanced Features

### Custom Domains

Create custom domains by:

1. Adding domain to `config.yaml`
2. Creating domain-specific knowledge files
3. Importing knowledge for the new domain

### Batch Learning

Prepare a JSON file with multiple knowledge entries and import:
```bash
python -m src.cli import-knowledge my_domain_knowledge.json --domain custom
```

### Conversation Analytics

View detailed statistics:
- Total knowledge entries
- Most used knowledge
- Domain-wise distribution
- Usage patterns

## Development

### Adding New Features

The chatbot is modular and extensible:

- **New domains**: Add to configuration and create knowledge files
- **New learning methods**: Extend the `LearningManager` class
- **New interfaces**: Create additional CLI commands or web interface
- **Custom storage**: Extend `KnowledgeStore` for different databases

### Testing

(Optional) Create tests in the `tests/` directory:
```bash
python -m pytest tests/
```

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure virtual environment is activated
2. **Model download**: First run may take time to download sentence transformer model
3. **Database issues**: Delete `data/knowledge.db` to reset database
4. **Configuration**: Check `config/config.yaml` for correct settings

### Logging

Check logs in `logs/chatbot.log` for detailed error information.

## Future Enhancements

### Planned Features
- Web interface
- Voice interaction
- Multi-language support
- Advanced NLP features
- Cloud deployment
- API endpoints
- Mobile app integration

### Contribution Areas
- More domain knowledge
- Better Hindi language support
- Improved learning algorithms
- Performance optimizations
- User interface enhancements

## Support

For support or questions:
1. Check the logs for error details
2. Review configuration settings
3. Try the troubleshooting steps above

## License

This project is open source. Feel free to use, modify, and distribute according to your needs.

---

## Quick Start Example

```bash
# Setup
pip install -r requirements.txt
python -m src.cli setup

# Start chatting
python -m src.cli chat --domain shop

# In chat:
You: fan ki price
Bot: Ceiling fan ki price 2000 se 5000 rupees tak...

You: teach: inverter ki battery | Inverter battery 150AH 8000-12000 rupees mein milti hai
Bot: ✅ Successfully learned!

You: inverter ki battery
Bot: Inverter battery 150AH 8000-12000 rupees mein milti hai
```

यह chatbot आपके business को बेहतर बनाने के लिए बनाया गया है। आप जो भी सिखाएंगे, वो याद रखेगा और customers को बेहतर service दे सकेगा।
