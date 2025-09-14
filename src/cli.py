"""
Command-line interface for the Adaptive Chatbot
"""

import typer
import logging
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.text import Text
from rich import print as rprint
from pathlib import Path
import uuid
from typing import Optional

from .chatbot import AdaptiveChatbot
from .learning import LearningManager
from .voice_interface import VoiceInterface, VoiceChatSession


app = typer.Typer(
    name="adaptive-chatbot",
    help="An adaptive chatbot that can learn and remember what you teach it."
)
console = Console()


@app.command()
def chat(
    domain: str = typer.Option("general", "--domain", "-d", help="Set the domain for conversation"),
    config: Optional[str] = typer.Option(None, "--config", "-c", help="Path to configuration file")
):
    """Start an interactive chat session with the chatbot."""
    try:
        console.print(Panel.fit("🤖 Adaptive Chatbot", style="bold blue"))
        console.print("Loading chatbot... Please wait.")
        
        # Initialize chatbot
        chatbot = AdaptiveChatbot(config)
        chatbot.set_domain(domain)
        learning_manager = LearningManager(chatbot.knowledge_store)
        
        # Load shop knowledge if in shop domain
        if domain == "shop":
            shop_knowledge_path = "data/shop_knowledge.json"
            if Path(shop_knowledge_path).exists():
                success, total = learning_manager.import_knowledge_file(shop_knowledge_path, "shop")
                console.print(f"Loaded {success}/{total} shop knowledge entries", style="green")
        
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Get domain config for greeting
        domain_config = chatbot.config.get_domain_config(domain)
        greeting = domain_config.get('greeting', "Hello! How can I help you today?")
        
        console.print(f"\n{greeting}")
        console.print(f"Domain: {domain.title()}")
        console.print("Type 'help' for commands, 'quit' to exit.\n", style="dim")
        
        while True:
            try:
                # Get user input
                user_input = Prompt.ask("\n[bold blue]You[/bold blue]")
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    console.print("Goodbye! 👋", style="green")
                    break
                elif user_input.lower() == 'help':
                    show_help()
                    continue
                elif user_input.lower().startswith('teach:'):
                    # Teaching mode
                    handle_teach_command(user_input, learning_manager, domain)
                    continue
                elif user_input.lower() == 'stats':
                    show_stats(chatbot, learning_manager)
                    continue
                elif user_input.lower().startswith('domain:'):
                    # Change domain
                    new_domain = user_input.split(':', 1)[1].strip()
                    chatbot.set_domain(new_domain)
                    domain_config = chatbot.config.get_domain_config(new_domain)
                    greeting = domain_config.get('greeting', f"Switched to {new_domain} domain")
                    console.print(greeting, style="cyan")
                    continue
                
                # Get chatbot response
                response = chatbot.process_message(user_input)
                console.print(f"\n[bold green]Bot[/bold green]: {response}")
                
                # Ask for feedback occasionally (every 5 messages)
                if len(chatbot.conversation_history) % 10 == 0:
                    get_feedback(user_input, response, learning_manager)
                
            except KeyboardInterrupt:
                console.print("\n\nGoodbye! 👋", style="green")
                break
            except Exception as e:
                console.print(f"Error: {e}", style="red")
                
    except Exception as e:
        console.print(f"Failed to initialize chatbot: {e}", style="red")
        raise typer.Exit(1)


@app.command()
def teach(
    input_text: str = typer.Argument(..., help="The input/question to teach"),
    response_text: str = typer.Argument(..., help="The expected response"),
    domain: str = typer.Option("general", "--domain", "-d", help="Domain for the knowledge"),
    category: str = typer.Option("learned", "--category", "-c", help="Category for organization"),
    config: Optional[str] = typer.Option(None, "--config", help="Path to configuration file")
):
    """Teach the chatbot a new input-response pair."""
    try:
        chatbot = AdaptiveChatbot(config)
        learning_manager = LearningManager(chatbot.knowledge_store)
        
        success = learning_manager.teach_chatbot(
            input_text, response_text, category, domain
        )
        
        if success:
            console.print(f"✅ Successfully taught the chatbot!", style="green")
            console.print(f"Input: {input_text}")
            console.print(f"Response: {response_text}")
            console.print(f"Domain: {domain}, Category: {category}")
        else:
            console.print("❌ Failed to teach the chatbot", style="red")
            
    except Exception as e:
        console.print(f"Error: {e}", style="red")
        raise typer.Exit(1)


@app.command()
def import_knowledge(
    file_path: str = typer.Argument(..., help="Path to the JSON knowledge file"),
    domain: str = typer.Option("general", "--domain", "-d", help="Domain to assign to imported knowledge"),
    config: Optional[str] = typer.Option(None, "--config", help="Path to configuration file")
):
    """Import knowledge from a JSON file."""
    try:
        chatbot = AdaptiveChatbot(config)
        learning_manager = LearningManager(chatbot.knowledge_store)
        
        if not Path(file_path).exists():
            console.print(f"File not found: {file_path}", style="red")
            raise typer.Exit(1)
        
        success, total = learning_manager.import_knowledge_file(file_path, domain)
        
        if success > 0:
            console.print(f"✅ Successfully imported {success}/{total} knowledge entries!", style="green")
        else:
            console.print("❌ Failed to import knowledge", style="red")
            
    except Exception as e:
        console.print(f"Error: {e}", style="red")
        raise typer.Exit(1)


@app.command()
def export_knowledge(
    file_path: str = typer.Argument(..., help="Path to save the exported knowledge"),
    domain: Optional[str] = typer.Option(None, "--domain", "-d", help="Domain to export (all if not specified)"),
    config: Optional[str] = typer.Option(None, "--config", help="Path to configuration file")
):
    """Export knowledge to a JSON file."""
    try:
        chatbot = AdaptiveChatbot(config)
        learning_manager = LearningManager(chatbot.knowledge_store)
        
        success = learning_manager.export_training_data(file_path, domain)
        
        if success:
            console.print(f"✅ Successfully exported knowledge to {file_path}!", style="green")
        else:
            console.print("❌ Failed to export knowledge", style="red")
            
    except Exception as e:
        console.print(f"Error: {e}", style="red")
        raise typer.Exit(1)


@app.command()
def stats(
    config: Optional[str] = typer.Option(None, "--config", help="Path to configuration file")
):
    """Show chatbot statistics."""
    try:
        chatbot = AdaptiveChatbot(config)
        learning_manager = LearningManager(chatbot.knowledge_store)
        
        show_stats(chatbot, learning_manager)
        
    except Exception as e:
        console.print(f"Error: {e}", style="red")
        raise typer.Exit(1)


@app.command(name="voice-chat")
def voice_chat(
    domain: str = typer.Option("general", "--domain", "-d", help="Set the domain for voice conversation"),
    config: Optional[str] = typer.Option(None, "--config", "-c", help="Path to configuration file"),
    test_first: bool = typer.Option(False, "--test", help="Test voice interface before starting chat")
):
    """Start a voice-enabled chat session with the chatbot."""
    try:
        console.print(Panel.fit("🎤 Voice Chat - Adaptive Chatbot", style="bold blue"))
        console.print("Initializing voice interface... Please wait.")
        
        # Initialize chatbot
        chatbot = AdaptiveChatbot(config)
        chatbot.set_domain(domain)
        learning_manager = LearningManager(chatbot.knowledge_store)
        
        # Load shop knowledge if in shop domain
        if domain == "shop":
            shop_knowledge_path = "data/shop_knowledge.json"
            if Path(shop_knowledge_path).exists():
                success, total = learning_manager.import_knowledge_file(shop_knowledge_path, "shop")
                console.print(f"Loaded {success}/{total} shop knowledge entries", style="green")
        
        # Initialize voice interface
        voice_config = {
            'use_gtts': chatbot.config.use_gtts,
            'language': chatbot.config.voice_language,
            'tts_language': chatbot.config.tts_language,
            'speech_rate': chatbot.config.speech_rate,
            'voice_id': chatbot.config.voice_id,
            'energy_threshold': chatbot.config.energy_threshold,
            'pause_threshold': chatbot.config.pause_threshold,
            'timeout': chatbot.config.timeout,
            'phrase_time_limit': chatbot.config.phrase_time_limit
        }
        
        voice_interface = VoiceInterface(voice_config)
        
        # Test voice interface if requested
        if test_first:
            console.print("Testing voice interface...")
            if not voice_interface.test_voice_interface():
                console.print("❌ Voice interface test failed. Please check your microphone and speakers.", style="red")
                raise typer.Exit(1)
            console.print("✅ Voice interface test passed!", style="green")
        
        # Start voice chat session
        console.print(f"\n🎤 Voice Chat Mode Activated - Domain: {domain.title()}")
        console.print("Press Ctrl+C to exit voice chat\n", style="dim")
        
        voice_chat_session = VoiceChatSession(voice_interface, chatbot)
        voice_chat_session.start_session(learning_manager)
        
    except KeyboardInterrupt:
        console.print("\n\nVoice chat stopped.", style="yellow")
    except Exception as e:
        console.print(f"Failed to start voice chat: {e}", style="red")
        raise typer.Exit(1)
    finally:
        try:
            voice_interface.cleanup()
        except:
            pass


@app.command(name="test-voice")
def test_voice(
    config: Optional[str] = typer.Option(None, "--config", help="Path to configuration file")
):
    """Test the voice interface (microphone and speakers)."""
    try:
        console.print(Panel.fit("🧪 Voice Interface Test", style="bold cyan"))
        
        # Initialize chatbot to get config
        chatbot = AdaptiveChatbot(config)
        
        # Initialize voice interface
        voice_config = {
            'use_gtts': chatbot.config.use_gtts,
            'language': chatbot.config.voice_language,
            'tts_language': chatbot.config.tts_language,
            'speech_rate': chatbot.config.speech_rate,
            'voice_id': chatbot.config.voice_id,
            'energy_threshold': chatbot.config.energy_threshold,
            'pause_threshold': chatbot.config.pause_threshold,
            'timeout': chatbot.config.timeout,
            'phrase_time_limit': chatbot.config.phrase_time_limit
        }
        
        voice_interface = VoiceInterface(voice_config)
        
        # Run voice test
        success = voice_interface.test_voice_interface()
        
        if success:
            console.print("\n✅ Voice interface is working correctly!", style="bold green")
        else:
            console.print("\n❌ Voice interface test failed. Please check your audio devices.", style="bold red")
            raise typer.Exit(1)
            
    except Exception as e:
        console.print(f"Error testing voice interface: {e}", style="red")
        raise typer.Exit(1)
    finally:
        try:
            voice_interface.cleanup()
        except:
            pass


@app.command(name="list-voices")
def list_voices(
    config: Optional[str] = typer.Option(None, "--config", help="Path to configuration file")
):
    """List available TTS voices on the system."""
    try:
        console.print(Panel.fit("🔊 Available TTS Voices", style="bold cyan"))
        
        # Initialize chatbot to get config
        chatbot = AdaptiveChatbot(config)
        
        # Initialize voice interface (without gTTS to get local voices)
        voice_config = {
            'use_gtts': False,  # Force local voices
            'speech_rate': chatbot.config.speech_rate,
        }
        
        voice_interface = VoiceInterface(voice_config)
        voices = voice_interface.get_available_voices()
        
        if voices:
            table = Table(title="Available TTS Voices", style="blue")
            table.add_column("ID", style="cyan")
            table.add_column("Name", style="green")
            table.add_column("Language", style="yellow")
            
            for voice in voices:
                languages = ', '.join(voice['language']) if isinstance(voice['language'], list) else str(voice['language'])
                table.add_row(str(voice['id']), voice['name'], languages)
            
            console.print(table)
            console.print(f"\nTo use a specific voice, update voice_id in your config file.", style="dim")
        else:
            console.print("No TTS voices found on this system.", style="yellow")
            
    except Exception as e:
        console.print(f"Error listing voices: {e}", style="red")
        raise typer.Exit(1)
    finally:
        try:
            voice_interface.cleanup()
        except:
            pass


@app.command()
def setup():
    """Setup the chatbot for first use."""
    console.print(Panel.fit("🚀 Chatbot Setup", style="bold green"))
    
    # Create directories
    dirs = ["data", "config", "logs", "models"]
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)
        console.print(f"✅ Created {dir_name}/ directory")
    
    # Initialize with shop knowledge if wanted
    if Confirm.ask("Do you want to load pre-built shop knowledge?"):
        shop_knowledge_path = Path("data/shop_knowledge.json")
        if shop_knowledge_path.exists():
            try:
                chatbot = AdaptiveChatbot()
                learning_manager = LearningManager(chatbot.knowledge_store)
                success, total = learning_manager.import_knowledge_file(str(shop_knowledge_path), "shop")
                console.print(f"✅ Loaded {success}/{total} shop knowledge entries", style="green")
            except Exception as e:
                console.print(f"❌ Failed to load shop knowledge: {e}", style="red")
    
    console.print("\n🎉 Setup complete! You can now use the chatbot.", style="bold green")
    console.print("Try: python -m src.cli chat --domain shop", style="dim")


def show_help():
    """Show help information."""
    help_panel = Panel.fit("""
[bold]Available Commands:[/bold]

• [cyan]help[/cyan] - Show this help message
• [cyan]stats[/cyan] - Show chatbot statistics  
• [cyan]quit/exit/bye[/cyan] - Exit the chat

• [cyan]teach: <input> | <response>[/cyan] - Teach new knowledge
  Example: teach: What is your name? | My name is ChatBot

• [cyan]domain: <domain_name>[/cyan] - Switch domain
  Example: domain: shop

[bold]Chat Tips:[/bold]
• The bot learns from your conversations
• Use Hindi/English mix as needed
• Be specific in your questions for better responses
    """, title="Help", style="blue")
    
    console.print(help_panel)


def handle_teach_command(user_input: str, learning_manager: LearningManager, domain: str):
    """Handle the teach command."""
    try:
        # Parse teach command: teach: <input> | <response>
        teach_content = user_input.split(':', 1)[1].strip()
        
        if '|' in teach_content:
            input_part, response_part = teach_content.split('|', 1)
            input_part = input_part.strip()
            response_part = response_part.strip()
            
            if input_part and response_part:
                success = learning_manager.teach_chatbot(input_part, response_part, "manual", domain)
                if success:
                    console.print("✅ Successfully learned!", style="green")
                else:
                    console.print("❌ Failed to learn", style="red")
            else:
                console.print("❌ Invalid format. Use: teach: <input> | <response>", style="red")
        else:
            console.print("❌ Invalid format. Use: teach: <input> | <response>", style="red")
            
    except Exception as e:
        console.print(f"❌ Error in teaching: {e}", style="red")


def get_feedback(user_input: str, bot_response: str, learning_manager: LearningManager):
    """Get user feedback on bot response."""
    feedback = Prompt.ask("\n[dim]Was this response helpful? (good/bad/correct it)[/dim]", default="skip")
    
    if feedback.lower() != "skip":
        learning_manager.interactive_learning(user_input, bot_response, feedback)


def show_stats(chatbot: AdaptiveChatbot, learning_manager: LearningManager):
    """Show chatbot statistics."""
    try:
        stats = learning_manager.get_learning_stats()
        
        # Create stats table
        table = Table(title="Chatbot Statistics", style="blue")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Total Knowledge Entries", str(stats.get('total_knowledge_entries', 0)))
        
        # Domain stats
        domains = stats.get('domains', {})
        for domain, count in domains.items():
            table.add_row(f"  {domain.title()} Domain", str(count))
        
        # Most used knowledge
        most_used = stats.get('most_used_knowledge', [])
        if most_used:
            table.add_row("", "")  # Empty row
            table.add_row("Most Used Knowledge", "")
            for item in most_used[:3]:
                table.add_row(f"  {item['input'][:40]}...", f"{item['usage_count']} times")
        
        console.print(table)
        
        # Show suggestions
        suggestions = learning_manager.suggest_improvements()
        if suggestions:
            console.print("\n[bold yellow]Suggestions:[/bold yellow]")
            for suggestion in suggestions:
                console.print(f"• {suggestion['message']}", style="yellow")
                
    except Exception as e:
        console.print(f"Error getting stats: {e}", style="red")


if __name__ == "__main__":
    app()
