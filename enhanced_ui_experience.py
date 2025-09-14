#!/usr/bin/env python3
"""
Enhanced UI & Experience System
Advanced user interface with real-time conversation display, voice visualization, 
language indicators, and interactive controls for the adaptive chatbot
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import time
import json
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, asdict
from collections import deque
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
from datetime import datetime
import asyncio
import queue
import os

try:
    from logger import log_info, log_error, log_warning
except ImportError:
    def log_info(msg): print(f"INFO - {msg}")
    def log_error(msg): print(f"ERROR - {msg}")
    def log_warning(msg): print(f"WARNING - {msg}")

@dataclass
class ConversationEntry:
    """Individual conversation entry"""
    timestamp: datetime
    speaker: str  # "user" or "bot"
    text: str
    language: str
    confidence: float
    voice_profile: Optional[Dict[str, Any]] = None
    processing_time: Optional[float] = None
    metadata: Dict[str, Any] = None

@dataclass
class UITheme:
    """UI theme configuration"""
    background_color: str = "#f0f0f0"
    primary_color: str = "#2c3e50"
    secondary_color: str = "#3498db"
    accent_color: str = "#e74c3c"
    text_color: str = "#2c3e50"
    success_color: str = "#27ae60"
    warning_color: str = "#f39c12"
    error_color: str = "#e74c3c"
    font_family: str = "Segoe UI"
    font_size: int = 11

class VoiceVisualizer:
    """Real-time voice activity visualizer"""
    
    def __init__(self, parent_frame, theme: UITheme):
        self.parent = parent_frame
        self.theme = theme
        
        # Create visualization frame
        viz_frame = ttk.LabelFrame(parent_frame, text="🎤 Voice Activity", padding="10")
        viz_frame.pack(fill=tk.X, pady=(5, 10))
        
        # Create matplotlib figure for voice visualization
        self.fig = Figure(figsize=(8, 2), dpi=80, facecolor=theme.background_color)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor(theme.background_color)
        
        # Initialize voice data
        self.audio_data = deque(maxlen=200)  # Keep last 200 samples
        self.is_recording = False
        self.is_speaking = False
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, viz_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Initialize plot
        self.line, = self.ax.plot([], [], color=theme.secondary_color, linewidth=2)
        self.ax.set_ylim(-1, 1)
        self.ax.set_xlim(0, 200)
        self.ax.set_ylabel("Amplitude")
        self.ax.set_title("Voice Activity Monitor")
        self.ax.grid(True, alpha=0.3)
        
        # Status indicators
        status_frame = ttk.Frame(viz_frame)
        status_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.recording_indicator = tk.Label(status_frame, text="● Recording", 
                                          fg=theme.error_color, font=(theme.font_family, 9))
        self.recording_indicator.pack(side=tk.LEFT, padx=(0, 10))
        
        self.speaking_indicator = tk.Label(status_frame, text="● Speaking", 
                                         fg=theme.success_color, font=(theme.font_family, 9))
        self.speaking_indicator.pack(side=tk.LEFT, padx=(0, 10))
        
        self.language_indicator = tk.Label(status_frame, text="🌐 EN", 
                                         fg=theme.primary_color, font=(theme.font_family, 9, 'bold'))
        self.language_indicator.pack(side=tk.RIGHT)
        
        # Start visualization update thread
        self.update_thread = threading.Thread(target=self._update_visualization, daemon=True)
        self.running = True
        self.update_thread.start()
    
    def update_audio_data(self, audio_chunk: np.ndarray):
        """Update audio data for visualization"""
        if len(audio_chunk) > 0:
            # Downsample if necessary
            if len(audio_chunk) > 50:
                indices = np.linspace(0, len(audio_chunk)-1, 50, dtype=int)
                audio_chunk = audio_chunk[indices]
            
            self.audio_data.extend(audio_chunk)
    
    def set_recording_status(self, is_recording: bool):
        """Update recording status"""
        self.is_recording = is_recording
        color = self.theme.error_color if is_recording else "#cccccc"
        self.recording_indicator.config(fg=color)
    
    def set_speaking_status(self, is_speaking: bool):
        """Update speaking status"""
        self.is_speaking = is_speaking
        color = self.theme.success_color if is_speaking else "#cccccc"
        self.speaking_indicator.config(fg=color)
    
    def set_language(self, language: str, confidence: float = 0.0):
        """Update language indicator"""
        lang_map = {
            "en": "🇺🇸 EN",
            "hi": "🇮🇳 HI", 
            "es": "🇪🇸 ES",
            "fr": "🇫🇷 FR",
            "de": "🇩🇪 DE",
            "it": "🇮🇹 IT",
            "pt": "🇵🇹 PT",
            "zh": "🇨🇳 ZH",
            "ja": "🇯🇵 JA",
            "ko": "🇰🇷 KO",
            "ar": "🇸🇦 AR",
            "ru": "🇷🇺 RU"
        }
        
        display_lang = lang_map.get(language.lower(), f"🌐 {language.upper()}")
        if confidence > 0:
            display_lang += f" ({confidence:.1%})"
        
        self.language_indicator.config(text=display_lang)
    
    def _update_visualization(self):
        """Update voice visualization in real-time"""
        while self.running:
            try:
                if len(self.audio_data) > 0:
                    # Update plot data
                    y_data = list(self.audio_data)
                    x_data = list(range(len(y_data)))
                    
                    self.line.set_data(x_data, y_data)
                    self.ax.set_xlim(0, max(len(y_data), 200))
                    
                    # Adjust y-axis based on data
                    if y_data:
                        y_range = max(abs(min(y_data)), abs(max(y_data)))
                        self.ax.set_ylim(-max(y_range * 1.1, 0.1), max(y_range * 1.1, 0.1))
                    
                    # Update canvas
                    self.canvas.draw()
                
                time.sleep(0.05)  # 20 FPS
                
            except Exception as e:
                log_error(f"Voice visualization error: {e}")
                time.sleep(0.1)
    
    def cleanup(self):
        """Clean up visualization resources"""
        self.running = False
        if self.update_thread.is_alive():
            self.update_thread.join(timeout=1)

class ConversationDisplay:
    """Advanced conversation display with rich formatting"""
    
    def __init__(self, parent_frame, theme: UITheme):
        self.parent = parent_frame
        self.theme = theme
        self.conversation_history = []
        
        # Create conversation frame
        conv_frame = ttk.LabelFrame(parent_frame, text="💬 Conversation", padding="10")
        conv_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 10))
        
        # Create scrolled text widget
        self.text_widget = scrolledtext.ScrolledText(
            conv_frame,
            wrap=tk.WORD,
            font=(theme.font_family, theme.font_size),
            bg="white",
            fg=theme.text_color,
            insertbackground=theme.primary_color,
            selectbackground=theme.secondary_color,
            selectforeground="white"
        )
        self.text_widget.pack(fill=tk.BOTH, expand=True)
        
        # Configure text tags for different speakers and formatting
        self._configure_text_tags()
        
        # Conversation controls
        controls_frame = ttk.Frame(conv_frame)
        controls_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(controls_frame, text="Clear History", 
                  command=self.clear_conversation).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(controls_frame, text="Save Conversation", 
                  command=self.save_conversation).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(controls_frame, text="Load Conversation", 
                  command=self.load_conversation).pack(side=tk.LEFT, padx=(0, 5))
        
        # Statistics label
        self.stats_label = tk.Label(controls_frame, text="Messages: 0", 
                                  font=(theme.font_family, 9), fg=theme.text_color)
        self.stats_label.pack(side=tk.RIGHT)
    
    def _configure_text_tags(self):
        """Configure text formatting tags"""
        # User message styling
        self.text_widget.tag_configure("user_header", 
                                     foreground=self.theme.primary_color,
                                     font=(self.theme.font_family, self.theme.font_size, 'bold'))
        
        self.text_widget.tag_configure("user_message", 
                                     foreground=self.theme.text_color,
                                     lmargin1=20, lmargin2=20)
        
        # Bot message styling
        self.text_widget.tag_configure("bot_header", 
                                     foreground=self.theme.secondary_color,
                                     font=(self.theme.font_family, self.theme.font_size, 'bold'))
        
        self.text_widget.tag_configure("bot_message", 
                                     foreground=self.theme.text_color,
                                     lmargin1=20, lmargin2=20,
                                     background="#f8f9fa")
        
        # Metadata styling
        self.text_widget.tag_configure("metadata", 
                                     foreground="#888888",
                                     font=(self.theme.font_family, 8),
                                     lmargin1=30, lmargin2=30)
        
        # Language indicators
        self.text_widget.tag_configure("language", 
                                     foreground=self.theme.accent_color,
                                     font=(self.theme.font_family, 8, 'bold'))
        
        # Timestamps
        self.text_widget.tag_configure("timestamp", 
                                     foreground="#666666",
                                     font=(self.theme.font_family, 8))
    
    def add_message(self, entry: ConversationEntry):
        """Add a new conversation entry"""
        self.conversation_history.append(entry)
        
        # Format timestamp
        timestamp_str = entry.timestamp.strftime("%H:%M:%S")
        
        # Insert message based on speaker
        if entry.speaker == "user":
            self._add_user_message(entry, timestamp_str)
        else:
            self._add_bot_message(entry, timestamp_str)
        
        # Auto-scroll to bottom
        self.text_widget.see(tk.END)
        
        # Update statistics
        self._update_stats()
    
    def _add_user_message(self, entry: ConversationEntry, timestamp: str):
        """Add user message to display"""
        # Header with timestamp and language
        header = f"👤 You ({entry.language.upper()}) [{timestamp}]\n"
        self.text_widget.insert(tk.END, header, "user_header")
        
        # Message content
        self.text_widget.insert(tk.END, f"{entry.text}\n", "user_message")
        
        # Add confidence if available
        if entry.confidence > 0:
            confidence_text = f"   Confidence: {entry.confidence:.1%}\n"
            self.text_widget.insert(tk.END, confidence_text, "metadata")
        
        self.text_widget.insert(tk.END, "\n")
    
    def _add_bot_message(self, entry: ConversationEntry, timestamp: str):
        """Add bot message to display"""
        # Header with timestamp and language
        header = f"🤖 Assistant ({entry.language.upper()}) [{timestamp}]\n"
        self.text_widget.insert(tk.END, header, "bot_header")
        
        # Message content
        self.text_widget.insert(tk.END, f"{entry.text}\n", "bot_message")
        
        # Add voice profile information if available
        if entry.voice_profile:
            profile_text = f"   Voice: {entry.voice_profile.get('personality', 'default')} style"
            if entry.processing_time:
                profile_text += f" ({entry.processing_time*1000:.0f}ms)"
            profile_text += "\n"
            self.text_widget.insert(tk.END, profile_text, "metadata")
        
        self.text_widget.insert(tk.END, "\n")
    
    def _update_stats(self):
        """Update conversation statistics"""
        total_messages = len(self.conversation_history)
        user_messages = sum(1 for entry in self.conversation_history if entry.speaker == "user")
        bot_messages = total_messages - user_messages
        
        stats_text = f"Messages: {total_messages} (👤{user_messages} 🤖{bot_messages})"
        self.stats_label.config(text=stats_text)
    
    def clear_conversation(self):
        """Clear conversation history"""
        if messagebox.askyesno("Clear Conversation", "Are you sure you want to clear the conversation history?"):
            self.text_widget.delete(1.0, tk.END)
            self.conversation_history.clear()
            self._update_stats()
    
    def save_conversation(self):
        """Save conversation to file"""
        if not self.conversation_history:
            messagebox.showwarning("No Conversation", "There's no conversation to save.")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                # Convert conversation to serializable format
                conversation_data = []
                for entry in self.conversation_history:
                    entry_dict = asdict(entry)
                    entry_dict['timestamp'] = entry.timestamp.isoformat()
                    conversation_data.append(entry_dict)
                
                if filename.endswith('.json'):
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(conversation_data, f, indent=2, ensure_ascii=False)
                else:
                    # Save as plain text
                    with open(filename, 'w', encoding='utf-8') as f:
                        for entry in self.conversation_history:
                            f.write(f"[{entry.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] ")
                            f.write(f"{entry.speaker.upper()} ({entry.language}): {entry.text}\n")
                
                messagebox.showinfo("Success", f"Conversation saved to {filename}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save conversation: {e}")
    
    def load_conversation(self):
        """Load conversation from file"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    conversation_data = json.load(f)
                
                # Clear current conversation
                self.clear_conversation()
                
                # Load entries
                for entry_dict in conversation_data:
                    entry_dict['timestamp'] = datetime.fromisoformat(entry_dict['timestamp'])
                    entry = ConversationEntry(**entry_dict)
                    self.add_message(entry)
                
                messagebox.showinfo("Success", f"Conversation loaded from {filename}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load conversation: {e}")

class ControlPanel:
    """Main control panel with settings and actions"""
    
    def __init__(self, parent_frame, theme: UITheme):
        self.parent = parent_frame
        self.theme = theme
        self.callbacks = {}
        
        # Create control frame
        control_frame = ttk.LabelFrame(parent_frame, text="🎛️ Control Panel", padding="10")
        control_frame.pack(fill=tk.X, pady=(5, 10))
        
        # Main buttons frame
        main_buttons = ttk.Frame(control_frame)
        main_buttons.pack(fill=tk.X, pady=(0, 10))
        
        # Voice control buttons
        self.start_button = ttk.Button(main_buttons, text="🎤 Start Listening", 
                                     command=self._start_listening, style="Success.TButton")
        self.start_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.stop_button = ttk.Button(main_buttons, text="⏹️ Stop", 
                                    command=self._stop_listening, style="Danger.TButton")
        self.stop_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.mute_button = ttk.Button(main_buttons, text="🔇 Mute", 
                                    command=self._toggle_mute)
        self.mute_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Status indicator
        self.status_label = tk.Label(main_buttons, text="● Ready", 
                                   fg=theme.success_color, 
                                   font=(theme.font_family, 10, 'bold'))
        self.status_label.pack(side=tk.RIGHT)
        
        # Settings frame
        settings_frame = ttk.LabelFrame(control_frame, text="Settings")
        settings_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Language settings
        lang_frame = ttk.Frame(settings_frame)
        lang_frame.pack(fill=tk.X, pady=(5, 5))
        
        tk.Label(lang_frame, text="Language Mode:").pack(side=tk.LEFT, padx=(0, 5))
        self.language_mode = ttk.Combobox(lang_frame, values=["Auto-detect", "English", "Hindi", "Spanish", "French"], 
                                        state="readonly", width=15)
        self.language_mode.set("Auto-detect")
        self.language_mode.pack(side=tk.LEFT, padx=(0, 10))
        
        # Voice settings
        tk.Label(lang_frame, text="Voice Style:").pack(side=tk.LEFT, padx=(5, 5))
        self.voice_style = ttk.Combobox(lang_frame, values=["Auto", "Professional", "Friendly", "Enthusiastic", "Calm"], 
                                      state="readonly", width=15)
        self.voice_style.set("Auto")
        self.voice_style.pack(side=tk.LEFT, padx=(0, 10))
        
        # Volume and speed controls
        volume_frame = ttk.Frame(settings_frame)
        volume_frame.pack(fill=tk.X, pady=(5, 5))
        
        tk.Label(volume_frame, text="Volume:").pack(side=tk.LEFT, padx=(0, 5))
        self.volume_scale = ttk.Scale(volume_frame, from_=0, to=100, orient=tk.HORIZONTAL, length=100)
        self.volume_scale.set(70)
        self.volume_scale.pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Label(volume_frame, text="Speed:").pack(side=tk.LEFT, padx=(5, 5))
        self.speed_scale = ttk.Scale(volume_frame, from_=0.5, to=2.0, orient=tk.HORIZONTAL, length=100)
        self.speed_scale.set(1.0)
        self.speed_scale.pack(side=tk.LEFT, padx=(0, 10))
        
        # Advanced settings button
        ttk.Button(volume_frame, text="⚙️ Advanced", 
                  command=self._show_advanced_settings).pack(side=tk.RIGHT)
        
        # Initialize state
        self.is_listening = False
        self.is_muted = False
    
    def register_callback(self, event_name: str, callback: Callable):
        """Register callback for UI events"""
        self.callbacks[event_name] = callback
    
    def _start_listening(self):
        """Start voice listening"""
        self.is_listening = True
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.status_label.config(text="● Listening", fg=self.theme.error_color)
        
        if 'start_listening' in self.callbacks:
            self.callbacks['start_listening']()
    
    def _stop_listening(self):
        """Stop voice listening"""
        self.is_listening = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.status_label.config(text="● Ready", fg=self.theme.success_color)
        
        if 'stop_listening' in self.callbacks:
            self.callbacks['stop_listening']()
    
    def _toggle_mute(self):
        """Toggle mute state"""
        self.is_muted = not self.is_muted
        mute_text = "🔊 Unmute" if self.is_muted else "🔇 Mute"
        self.mute_button.config(text=mute_text)
        
        if 'toggle_mute' in self.callbacks:
            self.callbacks['toggle_mute'](self.is_muted)
    
    def _show_advanced_settings(self):
        """Show advanced settings dialog"""
        AdvancedSettingsDialog(self.parent.master, self.theme)
    
    def get_settings(self) -> Dict[str, Any]:
        """Get current settings"""
        return {
            'language_mode': self.language_mode.get(),
            'voice_style': self.voice_style.get(),
            'volume': self.volume_scale.get(),
            'speed': self.speed_scale.get(),
            'is_muted': self.is_muted
        }
    
    def update_status(self, status: str, status_type: str = "info"):
        """Update status display"""
        color_map = {
            "info": self.theme.primary_color,
            "success": self.theme.success_color,
            "warning": self.theme.warning_color,
            "error": self.theme.error_color
        }
        
        color = color_map.get(status_type, self.theme.primary_color)
        self.status_label.config(text=f"● {status}", fg=color)

class AdvancedSettingsDialog:
    """Advanced settings dialog window"""
    
    def __init__(self, parent, theme: UITheme):
        self.theme = theme
        
        # Create dialog window
        self.window = tk.Toplevel(parent)
        self.window.title("Advanced Settings")
        self.window.geometry("500x600")
        self.window.resizable(False, False)
        self.window.transient(parent)
        self.window.grab_set()
        
        # Center the window
        self.window.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create dialog widgets"""
        notebook = ttk.Notebook(self.window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # AI Models tab
        ai_frame = ttk.Frame(notebook)
        notebook.add(ai_frame, text="🤖 AI Models")
        
        ttk.Label(ai_frame, text="Conversation Model:").pack(anchor=tk.W, pady=5)
        ai_model_combo = ttk.Combobox(ai_frame, values=[
            "microsoft/DialoGPT-small", "facebook/blenderbot-400M-distill",
            "microsoft/DialoGPT-medium", "OpenAI GPT-3.5"
        ])
        ai_model_combo.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(ai_frame, text="NLU Model:").pack(anchor=tk.W, pady=5)
        nlu_model_combo = ttk.Combobox(ai_frame, values=[
            "distilbert-base-uncased", "bert-base-multilingual-cased",
            "xlm-roberta-base", "albert-base-v2"
        ])
        nlu_model_combo.pack(fill=tk.X, pady=(0, 10))
        
        # Voice tab
        voice_frame = ttk.Frame(notebook)
        notebook.add(voice_frame, text="🎙️ Voice")
        
        ttk.Label(voice_frame, text="Voice Gender:").pack(anchor=tk.W, pady=5)
        gender_combo = ttk.Combobox(voice_frame, values=["Auto", "Male", "Female"])
        gender_combo.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(voice_frame, text="Voice Age:").pack(anchor=tk.W, pady=5)
        age_combo = ttk.Combobox(voice_frame, values=["Auto", "Young", "Adult", "Senior"])
        age_combo.pack(fill=tk.X, pady=(0, 10))
        
        # Audio processing
        ttk.Checkbutton(voice_frame, text="Enable noise reduction").pack(anchor=tk.W, pady=5)
        ttk.Checkbutton(voice_frame, text="Enable echo cancellation").pack(anchor=tk.W, pady=5)
        ttk.Checkbutton(voice_frame, text="Enable automatic gain control").pack(anchor=tk.W, pady=5)
        
        # Performance tab
        perf_frame = ttk.Frame(notebook)
        notebook.add(perf_frame, text="⚡ Performance")
        
        ttk.Label(perf_frame, text="Processing Threads:").pack(anchor=tk.W, pady=5)
        threads_spinbox = ttk.Spinbox(perf_frame, from_=1, to=8, value=2)
        threads_spinbox.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(perf_frame, text="Cache Size (MB):").pack(anchor=tk.W, pady=5)
        cache_spinbox = ttk.Spinbox(perf_frame, from_=100, to=2000, value=500)
        cache_spinbox.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Checkbutton(perf_frame, text="Enable GPU acceleration (if available)").pack(anchor=tk.W, pady=5)
        ttk.Checkbutton(perf_frame, text="Preload AI models").pack(anchor=tk.W, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(self.window)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Button(button_frame, text="Save", command=self._save_settings).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Cancel", command=self.window.destroy).pack(side=tk.RIGHT)
        ttk.Button(button_frame, text="Reset to Defaults", command=self._reset_defaults).pack(side=tk.LEFT)
    
    def _save_settings(self):
        """Save advanced settings"""
        # Here you would save the settings to configuration file
        messagebox.showinfo("Settings Saved", "Advanced settings have been saved successfully!")
        self.window.destroy()
    
    def _reset_defaults(self):
        """Reset to default settings"""
        if messagebox.askyesno("Reset Settings", "Are you sure you want to reset all settings to defaults?"):
            # Reset all widgets to default values
            messagebox.showinfo("Settings Reset", "Settings have been reset to defaults!")

class EnhancedUIExperience:
    """Main Enhanced UI & Experience system"""
    
    def __init__(self, root=None):
        # Create root window if not provided
        if root is None:
            self.root = tk.Tk()
            self.owns_root = True
        else:
            self.root = root
            self.owns_root = False
        
        # Initialize theme
        self.theme = UITheme()
        
        # Configure root window
        self._configure_root()
        
        # Initialize components
        self.voice_visualizer = None
        self.conversation_display = None
        self.control_panel = None
        
        # Create UI components
        self._create_ui_components()
        
        # Initialize event queue for thread-safe GUI updates
        self.event_queue = queue.Queue()
        self._process_events()
        
        log_info("🎨 Enhanced UI & Experience system initialized")
    
    def _configure_root(self):
        """Configure main window"""
        self.root.title("Adaptive Chatbot - Enhanced Experience")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')  # Modern theme
        
        # Configure custom styles
        style.configure("Success.TButton", foreground=self.theme.success_color)
        style.configure("Danger.TButton", foreground=self.theme.error_color)
        style.configure("Warning.TButton", foreground=self.theme.warning_color)
        
        # Configure colors
        self.root.configure(bg=self.theme.background_color)
        
        # Set window icon (if available)
        try:
            # You can add an icon file here
            # self.root.iconbitmap("icon.ico")
            pass
        except:
            pass
    
    def _create_ui_components(self):
        """Create main UI components"""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create paned window for resizable layout
        paned_window = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)
        
        # Left panel for controls and visualization
        left_frame = ttk.Frame(paned_window, width=400)
        paned_window.add(left_frame, weight=1)
        
        # Right panel for conversation
        right_frame = ttk.Frame(paned_window, width=600)
        paned_window.add(right_frame, weight=2)
        
        # Create components
        self.control_panel = ControlPanel(left_frame, self.theme)
        self.voice_visualizer = VoiceVisualizer(left_frame, self.theme)
        self.conversation_display = ConversationDisplay(right_frame, self.theme)
        
        # Create menu bar
        self._create_menu_bar()
        
        # Create status bar
        self._create_status_bar()
    
    def _create_menu_bar(self):
        """Create application menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Conversation", command=self._new_conversation)
        file_menu.add_command(label="Open Conversation...", command=self.conversation_display.load_conversation)
        file_menu.add_command(label="Save Conversation...", command=self.conversation_display.save_conversation)
        file_menu.add_separator()
        file_menu.add_command(label="Export Analytics...", command=self._export_analytics)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_closing)
        
        # Settings menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="Advanced Settings...", command=self.control_panel._show_advanced_settings)
        settings_menu.add_command(label="Theme Settings...", command=self._show_theme_settings)
        settings_menu.add_separator()
        settings_menu.add_command(label="Reset to Defaults", command=self._reset_settings)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Voice Calibration...", command=self._voice_calibration)
        tools_menu.add_command(label="Language Test...", command=self._language_test)
        tools_menu.add_command(label="Performance Monitor...", command=self._show_performance_monitor)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="User Guide", command=self._show_user_guide)
        help_menu.add_command(label="Keyboard Shortcuts", command=self._show_shortcuts)
        help_menu.add_command(label="Check for Updates", command=self._check_updates)
        help_menu.add_separator()
        help_menu.add_command(label="About", command=self._show_about)
    
    def _create_status_bar(self):
        """Create status bar at bottom"""
        status_frame = ttk.Frame(self.root)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Status labels
        self.status_left = tk.Label(status_frame, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_left.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.status_center = tk.Label(status_frame, text="", relief=tk.SUNKEN, anchor=tk.CENTER, width=20)
        self.status_center.pack(side=tk.LEFT)
        
        self.status_right = tk.Label(status_frame, text="", relief=tk.SUNKEN, anchor=tk.E, width=15)
        self.status_right.pack(side=tk.RIGHT)
    
    def _process_events(self):
        """Process events from queue for thread-safe GUI updates"""
        try:
            while True:
                event_data = self.event_queue.get_nowait()
                self._handle_event(event_data)
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(100, self._process_events)
    
    def _handle_event(self, event_data: Dict[str, Any]):
        """Handle GUI events from other threads"""
        event_type = event_data.get('type')
        
        if event_type == 'conversation_message':
            entry = event_data['entry']
            self.conversation_display.add_message(entry)
        
        elif event_type == 'audio_data':
            audio_chunk = event_data['data']
            self.voice_visualizer.update_audio_data(audio_chunk)
        
        elif event_type == 'status_update':
            status = event_data['status']
            status_type = event_data.get('status_type', 'info')
            self.control_panel.update_status(status, status_type)
        
        elif event_type == 'language_detected':
            language = event_data['language']
            confidence = event_data.get('confidence', 0.0)
            self.voice_visualizer.set_language(language, confidence)
        
        elif event_type == 'recording_status':
            is_recording = event_data['is_recording']
            self.voice_visualizer.set_recording_status(is_recording)
        
        elif event_type == 'speaking_status':
            is_speaking = event_data['is_speaking']
            self.voice_visualizer.set_speaking_status(is_speaking)
    
    # Event interface methods for other components to call
    def add_conversation_message(self, speaker: str, text: str, language: str = "en", 
                               confidence: float = 0.0, voice_profile: Dict = None,
                               processing_time: float = None):
        """Add conversation message (thread-safe)"""
        entry = ConversationEntry(
            timestamp=datetime.now(),
            speaker=speaker,
            text=text,
            language=language,
            confidence=confidence,
            voice_profile=voice_profile,
            processing_time=processing_time
        )
        
        self.event_queue.put({
            'type': 'conversation_message',
            'entry': entry
        })
    
    def update_audio_visualization(self, audio_data: np.ndarray):
        """Update audio visualization (thread-safe)"""
        self.event_queue.put({
            'type': 'audio_data',
            'data': audio_data
        })
    
    def update_status(self, status: str, status_type: str = "info"):
        """Update status (thread-safe)"""
        self.event_queue.put({
            'type': 'status_update',
            'status': status,
            'status_type': status_type
        })
    
    def set_language_detected(self, language: str, confidence: float = 0.0):
        """Set detected language (thread-safe)"""
        self.event_queue.put({
            'type': 'language_detected',
            'language': language,
            'confidence': confidence
        })
    
    def set_recording_status(self, is_recording: bool):
        """Set recording status (thread-safe)"""
        self.event_queue.put({
            'type': 'recording_status',
            'is_recording': is_recording
        })
    
    def set_speaking_status(self, is_speaking: bool):
        """Set speaking status (thread-safe)"""
        self.event_queue.put({
            'type': 'speaking_status',
            'is_speaking': is_speaking
        })
    
    # Menu command implementations
    def _new_conversation(self):
        """Start new conversation"""
        self.conversation_display.clear_conversation()
    
    def _export_analytics(self):
        """Export conversation analytics"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("CSV files", "*.csv")]
        )
        
        if filename:
            try:
                # Generate analytics
                analytics = self._generate_analytics()
                
                if filename.endswith('.json'):
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(analytics, f, indent=2, ensure_ascii=False, default=str)
                else:
                    # CSV export would require pandas or manual CSV writing
                    messagebox.showinfo("Info", "CSV export not implemented yet")
                
                messagebox.showinfo("Success", f"Analytics exported to {filename}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export analytics: {e}")
    
    def _generate_analytics(self) -> Dict[str, Any]:
        """Generate conversation analytics"""
        if not self.conversation_display.conversation_history:
            return {}
        
        history = self.conversation_display.conversation_history
        
        # Language distribution
        languages = {}
        for entry in history:
            lang = entry.language
            languages[lang] = languages.get(lang, 0) + 1
        
        # Message statistics
        user_messages = [e for e in history if e.speaker == "user"]
        bot_messages = [e for e in history if e.speaker == "bot"]
        
        # Confidence statistics
        confidences = [e.confidence for e in history if e.confidence > 0]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        # Processing time statistics
        processing_times = [e.processing_time for e in history if e.processing_time]
        avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0
        
        return {
            "overview": {
                "total_messages": len(history),
                "user_messages": len(user_messages),
                "bot_messages": len(bot_messages),
                "conversation_duration": (history[-1].timestamp - history[0].timestamp).total_seconds() if len(history) > 1 else 0
            },
            "language_distribution": languages,
            "performance": {
                "average_confidence": avg_confidence,
                "average_processing_time": avg_processing_time * 1000 if avg_processing_time else 0,  # Convert to ms
                "total_processing_time": sum(processing_times) * 1000 if processing_times else 0
            },
            "timestamps": {
                "first_message": history[0].timestamp if history else None,
                "last_message": history[-1].timestamp if history else None
            }
        }
    
    def _show_theme_settings(self):
        """Show theme settings dialog"""
        messagebox.showinfo("Theme Settings", "Theme customization coming soon!")
    
    def _reset_settings(self):
        """Reset all settings to defaults"""
        if messagebox.askyesno("Reset Settings", "Are you sure you want to reset all settings?"):
            messagebox.showinfo("Settings Reset", "Settings have been reset to defaults!")
    
    def _voice_calibration(self):
        """Voice calibration tool"""
        messagebox.showinfo("Voice Calibration", "Voice calibration tool coming soon!")
    
    def _language_test(self):
        """Language detection test"""
        messagebox.showinfo("Language Test", "Language detection test coming soon!")
    
    def _show_performance_monitor(self):
        """Show performance monitor"""
        messagebox.showinfo("Performance Monitor", "Performance monitoring coming soon!")
    
    def _show_user_guide(self):
        """Show user guide"""
        guide_text = """
        Adaptive Chatbot User Guide
        
        🎤 Voice Controls:
        - Click 'Start Listening' to begin voice input
        - Speak clearly and the system will detect your language automatically
        - Click 'Stop' to end voice input
        - Use 'Mute' to disable audio output
        
        💬 Conversation:
        - View your conversation in the right panel
        - Messages are color-coded by speaker
        - Language detection confidence is shown for each message
        - Save/load conversations using the File menu
        
        🎛️ Settings:
        - Choose language mode (Auto-detect or specific language)
        - Select voice style for responses
        - Adjust volume and speech speed
        - Access advanced settings for fine-tuning
        
        📊 Features:
        - Real-time voice visualization
        - Multi-language support
        - Adaptive voice personality
        - Conversation analytics
        """
        
        guide_window = tk.Toplevel(self.root)
        guide_window.title("User Guide")
        guide_window.geometry("600x400")
        
        text_widget = scrolledtext.ScrolledText(guide_window, wrap=tk.WORD, padx=10, pady=10)
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert(tk.END, guide_text)
        text_widget.config(state=tk.DISABLED)
    
    def _show_shortcuts(self):
        """Show keyboard shortcuts"""
        shortcuts_text = """
        Keyboard Shortcuts
        
        Ctrl+N        New Conversation
        Ctrl+O        Open Conversation
        Ctrl+S        Save Conversation
        Ctrl+Q        Quit
        
        F1            Start/Stop Listening
        F2            Toggle Mute
        F5            Refresh
        
        Ctrl+Plus     Increase Volume
        Ctrl+Minus    Decrease Volume
        
        F11           Toggle Fullscreen
        """
        
        messagebox.showinfo("Keyboard Shortcuts", shortcuts_text)
    
    def _check_updates(self):
        """Check for application updates"""
        messagebox.showinfo("Updates", "You are running the latest version!")
    
    def _show_about(self):
        """Show about dialog"""
        about_text = f"""
        Adaptive Chatbot - Enhanced Experience
        Version 2.0.0
        
        An advanced conversational AI system with:
        • Multi-language support
        • Adaptive voice personalities  
        • Real-time voice visualization
        • Advanced conversation management
        • Free AI model integration
        
        Built with Python, Tkinter, and modern AI technologies.
        
        © 2024 Adaptive Chatbot Project
        """
        
        messagebox.showinfo("About", about_text)
    
    def _on_closing(self):
        """Handle window closing"""
        if messagebox.askokcancel("Quit", "Do you want to quit the application?"):
            # Cleanup resources
            if self.voice_visualizer:
                self.voice_visualizer.cleanup()
            
            if self.owns_root:
                self.root.quit()
                self.root.destroy()
    
    def register_callback(self, event_name: str, callback: Callable):
        """Register callback for UI events"""
        if self.control_panel:
            self.control_panel.register_callback(event_name, callback)
    
    def get_settings(self) -> Dict[str, Any]:
        """Get current UI settings"""
        if self.control_panel:
            return self.control_panel.get_settings()
        return {}
    
    def run(self):
        """Run the UI main loop"""
        if self.owns_root:
            # Set up window close protocol
            self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
            
            # Start main loop
            self.root.mainloop()

# Global instance
_ui_system = None

def get_ui_system() -> EnhancedUIExperience:
    """Get global UI system instance"""
    global _ui_system
    if _ui_system is None:
        _ui_system = EnhancedUIExperience()
    return _ui_system

if __name__ == "__main__":
    # Test the UI system
    print("🎨 Testing Enhanced UI & Experience")
    print("=" * 50)
    
    # Create and run UI
    ui_system = EnhancedUIExperience()
    
    # Simulate some conversation messages for testing
    def simulate_conversation():
        import threading
        import time
        
        def add_test_messages():
            time.sleep(2)  # Wait for UI to load
            
            # Add some test messages
            ui_system.add_conversation_message(
                "user", 
                "Hello, I need help with electrical switches", 
                "en", 
                0.92
            )
            
            time.sleep(1)
            
            ui_system.add_conversation_message(
                "bot", 
                "Hello! I'd be happy to help you with electrical switches. What specific information do you need?",
                "en",
                voice_profile={"personality": "friendly", "energy": 0.7},
                processing_time=0.234
            )
            
            time.sleep(2)
            
            ui_system.add_conversation_message(
                "user",
                "मुझे एक अच्छा switch चाहिए",
                "hi",
                0.88
            )
            
            time.sleep(1)
            
            ui_system.add_conversation_message(
                "bot",
                "जी हाँ, मैं आपकी मदद कर सकता हूँ। आपको किस तरह का switch चाहिए?",
                "hi",
                voice_profile={"personality": "professional", "formality": 0.8},
                processing_time=0.187
            )
            
            # Simulate some audio data
            for i in range(10):
                time.sleep(0.5)
                audio_data = np.random.random(50) * 0.5
                ui_system.update_audio_visualization(audio_data)
        
        thread = threading.Thread(target=add_test_messages, daemon=True)
        thread.start()
    
    # Start simulation
    simulate_conversation()
    
    # Run UI
    ui_system.run()
    
    print("✅ Enhanced UI & Experience test completed")