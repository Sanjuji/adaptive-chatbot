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
                
                # Retrieval-first to prevent hallucinations; fallback to generator
                response = None
                try:
                    # Choose threshold (per-domain override)
                    th = getattr(chatbot.config, 'retrieval_similarity_threshold', 0.65)
                    per = getattr(chatbot.config, 'retrieval_similarity_thresholds', {}) or {}
                    if domain in per:
                        th = per[domain]
                    from .retrieval import hybrid_search  # lazy import
                    rows = hybrid_search(chatbot.knowledge_store, user_input, domain=domain, top_k=1, min_semantic_similarity=th)
                    if rows:
                        response = rows[0].get('response')
                except Exception:
                    pass
                if not response:
                    # Fallback to generator if retrieval didn’t return a confident match
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
            'phrase_time_limit': chatbot.config.phrase_time_limit,
            'mic_device_name': getattr(chatbot.config, 'mic_device_name', None),
            'use_vad': getattr(chatbot.config, 'use_vad', False)
        }
        
        voice_interface = VoiceInterface(voice_config)
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
            'phrase_time_limit': chatbot.config.phrase_time_limit,
            'mic_device_name': getattr(chatbot.config, 'mic_device_name', None),
            'use_vad': getattr(chatbot.config, 'use_vad', False)
        }
        
        voice_interface = VoiceInterface(voice_config)
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


@app.command(name="build-index")
def build_index(
    domain: Optional[str] = typer.Option(None, "--domain", "-d", help="Domain to build (all if not provided)"),
    config: Optional[str] = typer.Option(None, "--config", help="Path to configuration file")
):
    """Build or rebuild the semantic index (hnswlib) for one or all domains."""
    try:
        console.print(Panel.fit("🧱 Building Semantic Index", style="bold cyan"))
        chatbot = AdaptiveChatbot(config)
        # optional import (graceful if user hasn't installed extras)
        try:
            from .semantic_index import SemanticIndex  # type: ignore
        except Exception:
            console.print("Semantic index not available (install hnswlib and sentence-transformers)", style="red")
            raise typer.Exit(1)
        si = SemanticIndex(model_name=chatbot.config.sentence_model_name)
        ks = chatbot.knowledge_store
        domains = [domain] if domain else chatbot.config.available_domains
        total = 0
        for d in domains:
            console.print(f"Indexing domain: [yellow]{d}[/yellow]")
            items = ks.get_inputs_for_domain(d)
            if not items:
                console.print(f"No items in domain '{d}'", style="yellow")
                continue
            ok = si.build(items, d)
            if ok:
                console.print(f"✅ Built index for '{d}' with {len(items)} items", style="green")
                total += len(items)
            else:
                console.print(f"❌ Failed to build index for '{d}'", style="red")
        if total == 0:
            raise typer.Exit(1)
    except Exception as e:
        console.print(f"Error building index: {e}", style="red")
        raise typer.Exit(1)


@app.command(name="search-knowledge")
def search_knowledge(
    query: str = typer.Argument(..., help="Query text to search"),
    domain: Optional[str] = typer.Option(None, "--domain", "-d", help="Limit search to a domain"),
    top_k: int = typer.Option(5, "--top-k", "-k", help="Number of results to return"),
    fts_only: bool = typer.Option(False, "--fts-only", help="Use only FTS/LIKE (skip semantic)"),
    config: Optional[str] = typer.Option(None, "--config", help="Path to configuration file")
):
    """Run a hybrid knowledge search (FTS/LIKE first, then semantic)."""
    try:
        from time import perf_counter
        chatbot = AdaptiveChatbot(config)
        ks = chatbot.knowledge_store
        console.print(Panel.fit(f"🔎 Search: {query}", style="bold blue"))
        # Pick similarity threshold (per-domain overrides default)
        th = chatbot.config.retrieval_similarity_threshold
        if domain and isinstance(chatbot.config.retrieval_similarity_thresholds, dict):
            th = chatbot.config.retrieval_similarity_thresholds.get(domain, th)
        t0 = perf_counter()
        results = []
        if fts_only:
            # FTS if available, otherwise LIKE fallback via keywords
            if hasattr(ks, 'search_fulltext'):
                results = ks.search_fulltext(query, domain=domain, limit=top_k)
                results = [{**r, '_source': 'fts', '_score': None} for r in results]
            else:
                words = [w for w in query.split() if len(w) > 1]
                results = ks.search_by_keywords(words, domain=domain)[:top_k]
                results = [{**r, '_source': 'like', '_score': None} for r in results]
        else:
            from .retrieval import hybrid_search  # type: ignore
            results = hybrid_search(ks, query, domain=domain, top_k=top_k, min_semantic_similarity=th)
        dt = (perf_counter() - t0) * 1000.0
        table = Table(title=f"Results (in {dt:.1f} ms)", style="blue")
        table.add_column("ID", justify="right", style="cyan")
        table.add_column("Input", style="green")
        table.add_column("Source", style="magenta")
        table.add_column("Score", style="yellow")
        for r in results:
            rid = str(r.get('id'))
            src = r.get('_source', '')
            score = f"{r.get('_score', 0):.3f}" if r.get('_score') is not None else ""
            inp = (r.get('input') or '')[:80]
            table.add_row(rid, inp, src, score)
        if not results:
            console.print("No results found.", style="yellow")
        else:
            console.print(table)
    except Exception as e:
        console.print(f"Error searching knowledge: {e}", style="red")
        raise typer.Exit(1)


@app.command(name="benchmark-retrieval")
def benchmark_retrieval(
    domain: Optional[str] = typer.Option(None, "--domain", "-d", help="Domain to benchmark (default: all)"),
    samples: int = typer.Option(100, "--samples", "-n", help="Number of queries to test"),
    top_k: int = typer.Option(5, "--top-k", "-k", help="Results to consider for accuracy"),
    config: Optional[str] = typer.Option(None, "--config", help="Path to configuration file")
):
    """Measure latency and top-1 accuracy for FTS/LIKE vs Hybrid (semantic)."""
    try:
        import random
        from statistics import median
        from time import perf_counter
        chatbot = AdaptiveChatbot(config)
        ks = chatbot.knowledge_store
        # Thresholds
        th = chatbot.config.retrieval_similarity_threshold
        domains = [domain] if domain else chatbot.config.available_domains
        # Collect items
        items = []
        for d in domains:
            items.extend(ks.get_inputs_for_domain(d))
        if not items:
            console.print("No knowledge available to benchmark.", style="yellow")
            raise typer.Exit(1)
        random.shuffle(items)
        items = items[:max(1, samples)]
        # Metrics
        fts_lat = []
        fts_hit = 0
        hyb_lat = []
        hyb_hit = 0
        # Loop
        from .retrieval import hybrid_search  # type: ignore
        for kid, text in items:
            # FTS-like
            t0 = perf_counter()
            if hasattr(ks, 'search_fulltext'):
                fres = ks.search_fulltext(text, limit=top_k)
            else:
                words = [w for w in text.split() if len(w) > 1]
                fres = ks.search_by_keywords(words)[:top_k]
            fts_lat.append((perf_counter() - t0) * 1000.0)
            if fres and (fres[0].get('id') == kid):
                fts_hit += 1
            # Hybrid
            t1 = perf_counter()
            hres = hybrid_search(ks, text, top_k=top_k, min_semantic_similarity=th)
            hyb_lat.append((perf_counter() - t1) * 1000.0)
            if hres and (hres[0].get('id') == kid):
                hyb_hit += 1
        # Summaries
        def p95(vals: list[float]) -> float:
            if not vals:
                return 0.0
            vs = sorted(vals)
            idx = int(0.95 * (len(vs) - 1))
            return vs[idx]
        result_panel = Panel.fit(
            f"""
Samples: {len(items)}

FTS/LIKE:  median={median(fts_lat):.1f} ms  p95={p95(fts_lat):.1f} ms  top1_acc={fts_hit/len(items):.2%}
Hybrid:    median={median(hyb_lat):.1f} ms  p95={p95(hyb_lat):.1f} ms  top1_acc={hyb_hit/len(items):.2%}
""",
            title="Retrieval Benchmark", style="bold green")
        console.print(result_panel)
    except Exception as e:
        console.print(f"Error benchmarking retrieval: {e}", style="red")
        raise typer.Exit(1)


@app.command()
def setup():
    """List available microphone devices and indices"""
    try:
        from speech_recognition import Microphone
        names = Microphone.list_microphone_names()
        table = Table(title="Available Microphones", style="blue")
        table.add_column("Index", style="cyan")
        table.add_column("Name", style="green")
        for idx, nm in enumerate(names):
            table.add_row(str(idx), nm or f"Device {idx}")
        console.print(table)
        console.print("\nSet mic_device_name in config (regex) to auto-select by name.", style="dim")
    except Exception as e:
        console.print(f"Error listing microphones: {e}", style="red")

@app.command(name="build-index")
def build_index(
    domain: Optional[str] = typer.Option(None, "--domain", "-d", help="Domain to build (all if not provided)"),
    config: Optional[str] = typer.Option(None, "--config", help="Path to configuration file")
):
    """Build or rebuild the semantic index (hnswlib) for one or all domains."""
    try:
        console.print(Panel.fit("🧱 Building Semantic Index", style="bold cyan"))
        chatbot = AdaptiveChatbot(config)
        from .semantic_index import SemanticIndex  # optional import
        si = SemanticIndex(model_name=chatbot.config.sentence_model_name)
        if not si.available():
            console.print("Semantic index not available (install hnswlib and sentence-transformers)", style="red")
            raise typer.Exit(1)
        ks = chatbot.knowledge_store
        domains = [domain] if domain else chatbot.config.available_domains
        total = 0
        for d in domains:
            console.print(f"Indexing domain: [yellow]{d}[/yellow]")
            items = ks.get_inputs_for_domain(d)
            if not items:
                console.print(f"No items in domain '{d}'", style="yellow")
                continue
            ok = si.build(items, d)
            if ok:
                console.print(f"✅ Built index for '{d}' with {len(items)} items", style="green")
                total += len(items)
            else:
                console.print(f"❌ Failed to build index for '{d}'", style="red")
        if total == 0:
            raise typer.Exit(1)
    except Exception as e:
        console.print(f"Error building index: {e}", style="red")
        raise typer.Exit(1)

@app.command(name="search-knowledge")
def search_knowledge(
    query: str = typer.Argument(..., help="Query text to search"),
    domain: Optional[str] = typer.Option(None, "--domain", "-d", help="Limit search to a domain"),
    top_k: int = typer.Option(5, "--top-k", "-k", help="Number of results to return"),
    fts_only: bool = typer.Option(False, "--fts-only", help="Use only FTS (skip semantic)") ,
    config: Optional[str] = typer.Option(None, "--config", help="Path to configuration file")
):
    """Run a hybrid knowledge search (FTS then semantic)."""
    try:
        from time import perf_counter
        chatbot = AdaptiveChatbot(config)
        ks = chatbot.knowledge_store
        console.print(Panel.fit(f"🔎 Search: {query}", style="bold blue"))
        t0 = perf_counter()
        results = []
        if fts_only:
            results = ks.search_fulltext(query, domain=domain, limit=top_k)
            results = [{**r, '_source': 'fts', '_score': None} for r in results]
        else:
            from .retrieval import hybrid_search
            results = hybrid_search(ks, query, domain=domain, top_k=top_k)
        dt = (perf_counter() - t0) * 1000.0
        table = Table(title=f"Results (in {dt:.1f} ms)", style="blue")
        table.add_column("ID", justify="right", style="cyan")
        table.add_column("Input", style="green")
        table.add_column("Source", style="magenta")
        table.add_column("Score", style="yellow")
        for r in results:
            rid = str(r.get('id'))
            src = r.get('_source', '')
            score = f"{r.get('_score', 0):.3f}" if r.get('_score') is not None else ""
            inp = (r.get('input') or '')[:60]
            table.add_row(rid, inp, src, score)
        if not results:
            console.print("No results found.", style="yellow")
        else:
            console.print(table)
    except Exception as e:
        console.print(f"Error searching knowledge: {e}", style="red")
        raise typer.Exit(1)


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
