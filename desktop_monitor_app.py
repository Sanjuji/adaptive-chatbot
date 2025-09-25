#!/usr/bin/env python3
"""
🖥️ Professional Desktop Monitoring Application
Real-time monitoring dashboard for Adaptive Chatbot system
"""

import tkinter as tk
import customtkinter as ctk
import threading
import time
import json
import sqlite3
import psutil
import asyncio
import websockets
from datetime import datetime, timedelta
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkinter
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from typing import Dict, List, Optional
import queue

class ProfessionalMonitorApp:
    """Professional desktop monitoring application"""
    
    def __init__(self):
        # Configure CustomTkinter
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Initialize main window
        self.root = ctk.CTk()
        self.root.title("🤖 Adaptive Chatbot - Professional Monitor v2.0")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)
        
        # Data queues for thread-safe updates
        self.data_queue = queue.Queue()
        self.websocket_queue = queue.Queue()
        
        # Database connection
        self.db_path = Path("data/advanced_debugger_data.db")
        
        # Monitoring state
        self.monitoring = False
        self.websocket_connected = False
        
        # Data storage
        self.conversation_data = []
        self.system_data = []
        self.voice_data = []
        
        # Initialize UI
        self.create_ui()
        self.start_monitoring()
        
        print("🖥️ Professional Monitor App initialized")
    
    def create_ui(self):
        """Create the professional UI layout"""
        
        # Main container
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        self.create_header()
        
        # Main content area with tabs
        self.create_tabview()
        
        # Status bar
        self.create_status_bar()
    
    def create_header(self):
        """Create professional header with branding"""
        
        header_frame = ctk.CTkFrame(self.main_frame, height=80)
        header_frame.pack(fill="x", padx=10, pady=(10, 0))
        header_frame.pack_propagate(False)
        
        # Title and logo area
        title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_frame.pack(side="left", fill="both", expand=True, padx=20, pady=15)
        
        # Main title
        title_label = ctk.CTkLabel(
            title_frame, 
            text="🤖 Adaptive Chatbot Professional Monitor",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(anchor="w")
        
        # Subtitle
        subtitle_label = ctk.CTkLabel(
            title_frame,
            text="Real-time Voice Chat Analytics & System Health Dashboard",
            font=ctk.CTkFont(size=14),
            text_color="gray70"
        )
        subtitle_label.pack(anchor="w")
        
        # Control buttons
        controls_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        controls_frame.pack(side="right", padx=20, pady=15)
        
        self.start_stop_btn = ctk.CTkButton(
            controls_frame,
            text="🔴 Stop Monitoring",
            command=self.toggle_monitoring,
            width=150,
            height=35,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.start_stop_btn.pack(side="right", padx=5)
        
        self.export_btn = ctk.CTkButton(
            controls_frame,
            text="📊 Export Data",
            command=self.export_data,
            width=130,
            height=35
        )
        self.export_btn.pack(side="right", padx=5)
    
    def create_tabview(self):
        """Create tabbed interface for different monitoring views"""
        
        self.tabview = ctk.CTkTabview(self.main_frame)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create tabs
        self.tab_overview = self.tabview.add("📊 Overview")
        self.tab_conversations = self.tabview.add("💬 Conversations")
        self.tab_voice = self.tabview.add("🎤 Voice Analytics")
        self.tab_system = self.tabview.add("⚙️ System Health")
        self.tab_logs = self.tabview.add("📝 Live Logs")
        
        # Initialize each tab
        self.create_overview_tab()
        self.create_conversations_tab()
        self.create_voice_tab()
        self.create_system_tab()
        self.create_logs_tab()
    
    def create_overview_tab(self):
        """Create overview dashboard with key metrics"""
        
        # Top metrics row
        metrics_frame = ctk.CTkFrame(self.tab_overview)
        metrics_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        # Metric cards
        self.create_metric_card(metrics_frame, "💬 Total Conversations", "0", "left")
        self.create_metric_card(metrics_frame, "🎤 Voice Interactions", "0", "left")
        self.create_metric_card(metrics_frame, "⏱️ Avg Response Time", "0ms", "left")
        self.create_metric_card(metrics_frame, "📊 System Health", "100%", "right")
        
        # Charts area
        charts_frame = ctk.CTkFrame(self.tab_overview)
        charts_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Left chart - Conversation trend
        left_chart_frame = ctk.CTkFrame(charts_frame)
        left_chart_frame.pack(side="left", fill="both", expand=True, padx=(10, 5), pady=10)
        
        chart_title = ctk.CTkLabel(left_chart_frame, text="📈 Conversation Trends", 
                                  font=ctk.CTkFont(size=16, weight="bold"))
        chart_title.pack(pady=(10, 5))
        
        # Matplotlib figure for conversation trends
        self.overview_fig = Figure(figsize=(6, 4), dpi=100, facecolor='#2b2b2b')
        self.overview_ax = self.overview_fig.add_subplot(111)
        self.overview_canvas = FigureCanvasTkinter(self.overview_fig, left_chart_frame)
        self.overview_canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        
        # Right stats panel
        right_stats_frame = ctk.CTkFrame(charts_frame)
        right_stats_frame.pack(side="right", fill="y", padx=(5, 10), pady=10)
        
        stats_title = ctk.CTkLabel(right_stats_frame, text="🎯 Live Statistics",
                                  font=ctk.CTkFont(size=16, weight="bold"))
        stats_title.pack(pady=(10, 15))
        
        # Live stats
        self.stats_frame = ctk.CTkScrollableFrame(right_stats_frame, width=250)
        self.stats_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.create_stat_item("Languages Detected", "0")
        self.create_stat_item("Voice Quality Score", "0%")
        self.create_stat_item("Processing Efficiency", "0%")
        self.create_stat_item("Memory Usage", "0 MB")
        self.create_stat_item("CPU Usage", "0%")
    
    def create_metric_card(self, parent, title, value, side):
        """Create a metric display card"""
        
        card = ctk.CTkFrame(parent)
        card.pack(side=side, fill="both", expand=True, padx=5, pady=10)
        
        title_label = ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=12))
        title_label.pack(pady=(15, 5))
        
        value_label = ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=20, weight="bold"))
        value_label.pack(pady=(0, 15))
        
        # Store reference for updates
        if not hasattr(self, 'metric_labels'):
            self.metric_labels = {}
        self.metric_labels[title] = value_label
    
    def create_stat_item(self, label, value):
        """Create a statistics item in the stats panel"""
        
        item_frame = ctk.CTkFrame(self.stats_frame)
        item_frame.pack(fill="x", pady=2)
        
        label_widget = ctk.CTkLabel(item_frame, text=label, font=ctk.CTkFont(size=11))
        label_widget.pack(side="left", padx=(10, 5), pady=8)
        
        value_widget = ctk.CTkLabel(item_frame, text=value, font=ctk.CTkFont(size=11, weight="bold"))
        value_widget.pack(side="right", padx=(5, 10), pady=8)
        
        # Store reference for updates
        if not hasattr(self, 'stat_labels'):
            self.stat_labels = {}
        self.stat_labels[label] = value_widget
    
    def create_conversations_tab(self):
        """Create conversations monitoring tab"""
        
        # Conversation list
        list_frame = ctk.CTkFrame(self.tab_conversations)
        list_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        list_title = ctk.CTkLabel(list_frame, text="💬 Recent Conversations",
                                 font=ctk.CTkFont(size=16, weight="bold"))
        list_title.pack(pady=(10, 5))
        
        self.conversations_list = ctk.CTkScrollableFrame(list_frame)
        self.conversations_list.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Conversation details
        details_frame = ctk.CTkFrame(self.tab_conversations, width=400)
        details_frame.pack(side="right", fill="y", padx=10, pady=10)
        details_frame.pack_propagate(False)
        
        details_title = ctk.CTkLabel(details_frame, text="📊 Conversation Details",
                                    font=ctk.CTkFont(size=16, weight="bold"))
        details_title.pack(pady=(10, 5))
        
        self.conversation_details = ctk.CTkTextbox(details_frame)
        self.conversation_details.pack(fill="both", expand=True, padx=10, pady=10)
    
    def create_voice_tab(self):
        """Create voice analytics tab"""
        
        # Voice metrics
        voice_metrics_frame = ctk.CTkFrame(self.tab_voice)
        voice_metrics_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        self.create_metric_card(voice_metrics_frame, "🎤 Voice Quality", "0%", "left")
        self.create_metric_card(voice_metrics_frame, "🗣️ Speech Rate", "0 WPM", "left")
        self.create_metric_card(voice_metrics_frame, "🎵 Tone Analysis", "Neutral", "left")
        self.create_metric_card(voice_metrics_frame, "⏱️ Processing Time", "0ms", "right")
        
        # Voice analytics chart
        voice_chart_frame = ctk.CTkFrame(self.tab_voice)
        voice_chart_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        chart_title = ctk.CTkLabel(voice_chart_frame, text="🎤 Voice Analytics Over Time",
                                  font=ctk.CTkFont(size=16, weight="bold"))
        chart_title.pack(pady=(10, 5))
        
        # Voice analytics matplotlib figure
        self.voice_fig = Figure(figsize=(12, 6), dpi=100, facecolor='#2b2b2b')
        self.voice_ax = self.voice_fig.add_subplot(111)
        self.voice_canvas = FigureCanvasTkinter(self.voice_fig, voice_chart_frame)
        self.voice_canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
    
    def create_system_tab(self):
        """Create system health monitoring tab"""
        
        # System metrics grid
        system_metrics_frame = ctk.CTkFrame(self.tab_system)
        system_metrics_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        self.create_metric_card(system_metrics_frame, "💾 Memory Usage", "0 MB", "left")
        self.create_metric_card(system_metrics_frame, "🖥️ CPU Usage", "0%", "left")
        self.create_metric_card(system_metrics_frame, "💽 Disk Usage", "0%", "left")
        self.create_metric_card(system_metrics_frame, "🌐 Network", "Active", "right")
        
        # System performance chart
        system_chart_frame = ctk.CTkFrame(self.tab_system)
        system_chart_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        chart_title = ctk.CTkLabel(system_chart_frame, text="⚙️ System Performance History",
                                  font=ctk.CTkFont(size=16, weight="bold"))
        chart_title.pack(pady=(10, 5))
        
        # System performance matplotlib figure
        self.system_fig = Figure(figsize=(12, 6), dpi=100, facecolor='#2b2b2b')
        self.system_ax = self.system_fig.add_subplot(111)
        self.system_canvas = FigureCanvasTkinter(self.system_fig, system_chart_frame)
        self.system_canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
    
    def create_logs_tab(self):
        """Create live logs monitoring tab"""
        
        # Log controls
        log_controls_frame = ctk.CTkFrame(self.tab_logs)
        log_controls_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        controls_title = ctk.CTkLabel(log_controls_frame, text="📝 Live System Logs",
                                     font=ctk.CTkFont(size=16, weight="bold"))
        controls_title.pack(side="left", padx=10, pady=10)
        
        clear_btn = ctk.CTkButton(log_controls_frame, text="🗑️ Clear Logs",
                                 command=self.clear_logs, width=100)
        clear_btn.pack(side="right", padx=10, pady=10)
        
        save_logs_btn = ctk.CTkButton(log_controls_frame, text="💾 Save Logs",
                                     command=self.save_logs, width=100)
        save_logs_btn.pack(side="right", padx=5, pady=10)
        
        # Live logs display
        self.logs_textbox = ctk.CTkTextbox(self.tab_logs)
        self.logs_textbox.pack(fill="both", expand=True, padx=10, pady=5)
    
    def create_status_bar(self):
        """Create status bar at bottom"""
        
        self.status_frame = ctk.CTkFrame(self.main_frame, height=40)
        self.status_frame.pack(fill="x", padx=10, pady=(0, 10))
        self.status_frame.pack_propagate(False)
        
        # Status indicators
        self.status_label = ctk.CTkLabel(self.status_frame, text="🟢 Monitoring Active")
        self.status_label.pack(side="left", padx=15, pady=10)
        
        self.connection_label = ctk.CTkLabel(self.status_frame, text="🔗 Database Connected")
        self.connection_label.pack(side="left", padx=15, pady=10)
        
        # Timestamp
        self.timestamp_label = ctk.CTkLabel(self.status_frame, text="")
        self.timestamp_label.pack(side="right", padx=15, pady=10)
        
        # Update timestamp regularly
        self.update_timestamp()
    
    def update_timestamp(self):
        """Update the timestamp display"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.timestamp_label.configure(text=f"🕒 {current_time}")
        self.root.after(1000, self.update_timestamp)
    
    def start_monitoring(self):
        """Start the monitoring threads"""
        
        self.monitoring = True
        
        # Start database monitoring thread
        db_thread = threading.Thread(target=self.monitor_database, daemon=True)
        db_thread.start()
        
        # Start system monitoring thread
        system_thread = threading.Thread(target=self.monitor_system, daemon=True)
        system_thread.start()
        
        # Start WebSocket monitoring thread
        websocket_thread = threading.Thread(target=self.monitor_websocket, daemon=True)
        websocket_thread.start()
        
        # Start UI update thread
        self.root.after(100, self.update_ui)
        
        print("✅ All monitoring threads started")
    
    def monitor_database(self):
        """Monitor the SQLite database for new data"""
        
        while self.monitoring:
            try:
                if self.db_path.exists():
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()
                    
                    # Query recent conversations
                    cursor.execute("""
                        SELECT * FROM voice_interactions 
                        ORDER BY timestamp DESC LIMIT 50
                    """)
                    conversations = cursor.fetchall()
                    
                    # Query system metrics
                    cursor.execute("""
                        SELECT * FROM system_metrics 
                        ORDER BY timestamp DESC LIMIT 100
                    """)
                    system_metrics = cursor.fetchall()
                    
                    # Put data in queue for UI update
                    self.data_queue.put({
                        'type': 'database',
                        'conversations': conversations,
                        'system_metrics': system_metrics
                    })
                    
                    conn.close()
                
                time.sleep(2)  # Check every 2 seconds
                
            except Exception as e:
                print(f"❌ Database monitoring error: {e}")
                time.sleep(5)
    
    def monitor_system(self):
        """Monitor system resources"""
        
        while self.monitoring:
            try:
                # Get system metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                
                system_data = {
                    'timestamp': datetime.now(),
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'memory_used_mb': memory.used // (1024 * 1024),
                    'disk_percent': disk.percent
                }
                
                # Put data in queue
                self.data_queue.put({
                    'type': 'system',
                    'data': system_data
                })
                
                time.sleep(3)  # Check every 3 seconds
                
            except Exception as e:
                print(f"❌ System monitoring error: {e}")
                time.sleep(5)
    
    def monitor_websocket(self):
        """Monitor WebSocket connection for real-time updates"""
        
        async def websocket_client():
            try:
                uri = "ws://localhost:8765"
                async with websockets.connect(uri) as websocket:
                    self.websocket_connected = True
                    print("🔗 WebSocket connected")
                    
                    async for message in websocket:
                        try:
                            data = json.loads(message)
                            self.websocket_queue.put(data)
                        except json.JSONDecodeError:
                            print("❌ Invalid WebSocket message")
                            
            except Exception as e:
                self.websocket_connected = False
                print(f"❌ WebSocket connection error: {e}")
                time.sleep(5)
        
        # Run WebSocket client
        while self.monitoring:
            try:
                asyncio.run(websocket_client())
            except:
                time.sleep(10)  # Retry connection
    
    def update_ui(self):
        """Update the UI with new data"""
        
        # Process data queue
        while not self.data_queue.empty():
            try:
                data = self.data_queue.get_nowait()
                self.process_data_update(data)
            except queue.Empty:
                break
        
        # Process WebSocket queue
        while not self.websocket_queue.empty():
            try:
                data = self.websocket_queue.get_nowait()
                self.process_websocket_update(data)
            except queue.Empty:
                break
        
        # Update charts
        self.update_charts()
        
        # Schedule next update
        if self.monitoring:
            self.root.after(1000, self.update_ui)
    
    def process_data_update(self, data):
        """Process database data updates"""
        
        if data['type'] == 'database':
            self.conversation_data = data['conversations']
            self.update_conversations_list()
            
        elif data['type'] == 'system':
            self.system_data.append(data['data'])
            # Keep only last 100 points
            if len(self.system_data) > 100:
                self.system_data = self.system_data[-100:]
            
            self.update_system_metrics(data['data'])
    
    def process_websocket_update(self, data):
        """Process WebSocket real-time updates"""
        
        # Add to logs
        log_entry = f"[{datetime.now().strftime('%H:%M:%S')}] {json.dumps(data, indent=2)}\n"
        self.logs_textbox.insert("end", log_entry)
        self.logs_textbox.see("end")
    
    def update_conversations_list(self):
        """Update the conversations list display"""
        
        # Clear existing items
        for widget in self.conversations_list.winfo_children():
            widget.destroy()
        
        # Add conversation items
        for i, conv in enumerate(self.conversation_data[:20]):  # Show latest 20
            conv_frame = ctk.CTkFrame(self.conversations_list)
            conv_frame.pack(fill="x", pady=2)
            
            # Conversation summary
            summary = f"Conv {i+1}: {conv[1] if len(conv) > 1 else 'N/A'}"
            conv_label = ctk.CTkLabel(conv_frame, text=summary[:50] + "...")
            conv_label.pack(side="left", padx=10, pady=5)
            
            # View button
            view_btn = ctk.CTkButton(conv_frame, text="View", width=60,
                                    command=lambda c=conv: self.show_conversation_details(c))
            view_btn.pack(side="right", padx=10, pady=5)
    
    def show_conversation_details(self, conversation):
        """Show detailed conversation information"""
        
        details = f"""
Conversation Details:
====================

ID: {conversation[0] if len(conversation) > 0 else 'N/A'}
Input Text: {conversation[1] if len(conversation) > 1 else 'N/A'}
Detected Language: {conversation[2] if len(conversation) > 2 else 'N/A'}
Response: {conversation[3] if len(conversation) > 3 else 'N/A'}
Timestamp: {conversation[4] if len(conversation) > 4 else 'N/A'}

Processing Metrics:
------------------
Voice Quality: {conversation[5] if len(conversation) > 5 else 'N/A'}
Response Time: {conversation[6] if len(conversation) > 6 else 'N/A'}ms
Confidence: {conversation[7] if len(conversation) > 7 else 'N/A'}%
"""
        
        self.conversation_details.delete("1.0", "end")
        self.conversation_details.insert("1.0", details)
    
    def update_system_metrics(self, metrics):
        """Update system metrics display"""
        
        if hasattr(self, 'metric_labels'):
            self.metric_labels.get("💾 Memory Usage", ctk.CTkLabel()).configure(
                text=f"{metrics['memory_used_mb']} MB"
            )
            self.metric_labels.get("🖥️ CPU Usage", ctk.CTkLabel()).configure(
                text=f"{metrics['cpu_percent']:.1f}%"
            )
    
    def update_charts(self):
        """Update all chart displays"""
        
        # Update overview chart
        if hasattr(self, 'overview_ax') and self.conversation_data:
            self.overview_ax.clear()
            self.overview_ax.set_facecolor('#2b2b2b')
            
            # Simple conversation count over time
            times = [datetime.now() - timedelta(minutes=x) for x in range(len(self.conversation_data))]
            counts = list(range(len(self.conversation_data)))
            
            self.overview_ax.plot(times, counts, color='#1f77b4', linewidth=2)
            self.overview_ax.set_title("Conversation Trends", color='white')
            self.overview_ax.tick_params(colors='white')
            self.overview_ax.grid(True, alpha=0.3)
            
            self.overview_canvas.draw()
        
        # Update system chart
        if hasattr(self, 'system_ax') and self.system_data:
            self.system_ax.clear()
            self.system_ax.set_facecolor('#2b2b2b')
            
            times = [item['timestamp'] for item in self.system_data]
            cpu_data = [item['cpu_percent'] for item in self.system_data]
            memory_data = [item['memory_percent'] for item in self.system_data]
            
            self.system_ax.plot(times, cpu_data, label='CPU %', color='#ff7f0e')
            self.system_ax.plot(times, memory_data, label='Memory %', color='#2ca02c')
            self.system_ax.set_title("System Performance", color='white')
            self.system_ax.legend()
            self.system_ax.tick_params(colors='white')
            self.system_ax.grid(True, alpha=0.3)
            
            self.system_canvas.draw()
    
    def toggle_monitoring(self):
        """Toggle monitoring on/off"""
        
        if self.monitoring:
            self.monitoring = False
            self.start_stop_btn.configure(text="🟢 Start Monitoring")
            self.status_label.configure(text="🔴 Monitoring Stopped")
        else:
            self.monitoring = True
            self.start_monitoring()
            self.start_stop_btn.configure(text="🔴 Stop Monitoring")
            self.status_label.configure(text="🟢 Monitoring Active")
    
    def export_data(self):
        """Export monitoring data to file"""
        
        try:
            export_data = {
                'conversations': self.conversation_data,
                'system_metrics': [
                    {
                        'timestamp': item['timestamp'].isoformat(),
                        'cpu_percent': item['cpu_percent'],
                        'memory_percent': item['memory_percent'],
                        'memory_used_mb': item['memory_used_mb']
                    } for item in self.system_data
                ],
                'export_timestamp': datetime.now().isoformat()
            }
            
            filename = f"monitoring_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = Path(filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Data exported to: {filepath}")
            
        except Exception as e:
            print(f"❌ Export failed: {e}")
    
    def clear_logs(self):
        """Clear the logs display"""
        self.logs_textbox.delete("1.0", "end")
    
    def save_logs(self):
        """Save current logs to file"""
        
        try:
            logs_content = self.logs_textbox.get("1.0", "end")
            filename = f"monitor_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(logs_content)
            
            print(f"✅ Logs saved to: {filename}")
            
        except Exception as e:
            print(f"❌ Save logs failed: {e}")
    
    def run(self):
        """Start the application"""
        
        print("🖥️ Starting Professional Monitor App...")
        print("📊 Dashboard ready at your service!")
        
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\n🛑 Monitor App stopped by user")
        finally:
            self.monitoring = False
            print("🔚 Monitor App closed")

if __name__ == "__main__":
    print("🖥️ Adaptive Chatbot Professional Monitor")
    print("=" * 50)
    
    try:
        app = ProfessionalMonitorApp()
        app.run()
    except Exception as e:
        print(f"❌ Failed to start monitor app: {e}")
        input("Press Enter to exit...")