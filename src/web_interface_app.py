#!/usr/bin/env python3
"""
🌐 Futuristic Flask-based Web Interface
Modern UI/UX for Adaptive Chatbot monitoring and control
"""

from flask import Flask, render_template, jsonify, request, send_file
from flask_socketio import SocketIO, emit
import sqlite3
import json
import psutil
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
import base64
import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import numpy as np

class FuturisticWebInterface:
    """Futuristic web interface for chatbot monitoring"""
    
    def __init__(self):
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'adaptive_chatbot_secret_key_2024'
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        # Database path
        self.db_path = Path("data/advanced_debugger_data.db")
        
        # Monitoring state
        self.monitoring = True
        self.connected_clients = 0
        
        # Setup routes
        self.setup_routes()
        self.setup_socketio_events()
        
        # Start background monitoring
        self.start_background_monitoring()
        
        try:
            print("🌐 Futuristic Web Interface initialized")
        except UnicodeEncodeError:
            print("Web Futuristic Web Interface initialized")
    
    def setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def dashboard():
            """Main dashboard page"""
            return render_template('futuristic_dashboard.html')
        
        @self.app.route('/api/status')
        def api_status():
            """API status endpoint"""
            return jsonify({
                'status': 'active' if self.monitoring else 'inactive',
                'connected_clients': self.connected_clients,
                'timestamp': datetime.now().isoformat(),
                'system': {
                    'cpu': psutil.cpu_percent(),
                    'memory': psutil.virtual_memory().percent,
                    'disk': psutil.disk_usage('/').percent if hasattr(psutil, 'disk_usage') else 0
                }
            })
        
        @self.app.route('/api/conversations')
        def api_conversations():
            """Get recent conversations"""
            try:
                if not self.db_path.exists():
                    return jsonify([])
                
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT * FROM voice_interactions 
                    ORDER BY timestamp DESC LIMIT 50
                """)
                conversations = cursor.fetchall()
                conn.close()
                
                # Convert to list of dicts
                conv_list = []
                for conv in conversations:
                    conv_dict = {
                        'id': conv[0] if len(conv) > 0 else None,
                        'input_text': conv[1] if len(conv) > 1 else '',
                        'language': conv[2] if len(conv) > 2 else '',
                        'response': conv[3] if len(conv) > 3 else '',
                        'timestamp': conv[4] if len(conv) > 4 else '',
                        'voice_quality': conv[5] if len(conv) > 5 else 0,
                        'response_time': conv[6] if len(conv) > 6 else 0,
                        'confidence': conv[7] if len(conv) > 7 else 0
                    }
                    conv_list.append(conv_dict)
                
                return jsonify(conv_list)
                
            except Exception as e:
                try:
                    print(f"⚠️ API conversations error: {e}")
                except UnicodeEncodeError:
                    print(f"API conversations error: {e}")
                return jsonify([])
        
        @self.app.route('/api/system_metrics')
        def api_system_metrics():
            """Get system performance metrics"""
            try:
                if not self.db_path.exists():
                    return jsonify([])
                
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT * FROM system_metrics 
                    ORDER BY timestamp DESC LIMIT 100
                """)
                metrics = cursor.fetchall()
                conn.close()
                
                # Convert to list of dicts
                metrics_list = []
                for metric in metrics:
                    metric_dict = {
                        'timestamp': metric[0] if len(metric) > 0 else '',
                        'cpu_percent': metric[1] if len(metric) > 1 else 0,
                        'memory_percent': metric[2] if len(metric) > 2 else 0,
                        'disk_percent': metric[3] if len(metric) > 3 else 0
                    }
                    metrics_list.append(metric_dict)
                
                return jsonify(metrics_list)
                
            except Exception as e:
                try:
                    print(f"⚠️ API system metrics error: {e}")
                except UnicodeEncodeError:
                    print(f"API system metrics error: {e}")
                return jsonify([])
        
        @self.app.route('/api/charts/conversations_trend')
        def api_conversations_trend_chart():
            """Generate conversations trend chart"""
            try:
                # Create a figure
                fig, ax = plt.subplots(figsize=(12, 6), dpi=100)
                fig.patch.set_facecolor('#0d1117')
                ax.set_facecolor('#161b22')
                
                # Get conversation data
                if self.db_path.exists():
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()
                    
                    cursor.execute("""
                        SELECT timestamp FROM voice_interactions 
                        ORDER BY timestamp DESC LIMIT 50
                    """)
                    timestamps = cursor.fetchall()
                    conn.close()
                    
                    if timestamps:
                        # Process data for visualization
                        times = [datetime.fromisoformat(ts[0]) for ts in timestamps if ts[0]]
                        times.reverse()  # Reverse to show chronological order
                        
                        # Create cumulative conversation count
                        counts = list(range(1, len(times) + 1))
                        
                        # Plot with futuristic styling
                        ax.plot(times, counts, color='#00d8ff', linewidth=3, marker='o', 
                               markersize=4, markerfacecolor='#00d8ff', alpha=0.8)
                        ax.fill_between(times, counts, alpha=0.2, color='#00d8ff')
                    
                else:
                    # Demo data if no database
                    times = [datetime.now() - timedelta(minutes=x) for x in range(20, 0, -1)]
                    counts = np.cumsum(np.random.randint(1, 4, 20))
                    
                    ax.plot(times, counts, color='#00d8ff', linewidth=3, marker='o',
                           markersize=4, markerfacecolor='#00d8ff', alpha=0.8)
                    ax.fill_between(times, counts, alpha=0.2, color='#00d8ff')
                
                # Styling
                ax.set_title('Conversation Trends Over Time', color='white', fontsize=16, fontweight='bold')
                ax.set_xlabel('Time', color='white', fontsize=12)
                ax.set_ylabel('Cumulative Conversations', color='white', fontsize=12)
                ax.tick_params(colors='white', labelsize=10)
                ax.grid(True, alpha=0.3, color='white')
                ax.spines['bottom'].set_color('white')
                ax.spines['top'].set_color('white')
                ax.spines['right'].set_color('white')
                ax.spines['left'].set_color('white')
                
                # Convert to base64
                img_buffer = io.BytesIO()
                plt.savefig(img_buffer, format='png', facecolor='#0d1117', 
                           bbox_inches='tight', dpi=100)
                img_buffer.seek(0)
                img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
                plt.close()
                
                return jsonify({'image': f'data:image/png;base64,{img_base64}'})
                
            except Exception as e:
                try:
                    print(f"⚠️ Chart generation error: {e}")
                except UnicodeEncodeError:
                    print(f"Chart generation error: {e}")
                return jsonify({'error': str(e)})
        
        @self.app.route('/api/charts/system_performance')
        def api_system_performance_chart():
            """Generate system performance chart"""
            try:
                fig, ax = plt.subplots(figsize=(12, 6), dpi=100)
                fig.patch.set_facecolor('#0d1117')
                ax.set_facecolor('#161b22')
                
                # Get system metrics data
                if self.db_path.exists():
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()
                    
                    cursor.execute("""
                        SELECT timestamp, cpu_percent, memory_percent 
                        FROM system_metrics 
                        ORDER BY timestamp DESC LIMIT 50
                    """)
                    metrics = cursor.fetchall()
                    conn.close()
                    
                    if metrics:
                        times = [datetime.fromisoformat(m[0]) for m in metrics if m[0]]
                        cpu_data = [m[1] for m in metrics]
                        memory_data = [m[2] for m in metrics]
                        
                        times.reverse()
                        cpu_data.reverse()
                        memory_data.reverse()
                        
                        ax.plot(times, cpu_data, color='#ff6b6b', linewidth=3, 
                               label='CPU Usage (%)', marker='o', markersize=3)
                        ax.plot(times, memory_data, color='#4ecdc4', linewidth=3, 
                               label='Memory Usage (%)', marker='s', markersize=3)
                else:
                    # Demo data
                    times = [datetime.now() - timedelta(minutes=x) for x in range(20, 0, -1)]
                    cpu_data = np.random.randint(20, 80, 20)
                    memory_data = np.random.randint(30, 70, 20)
                    
                    ax.plot(times, cpu_data, color='#ff6b6b', linewidth=3, 
                           label='CPU Usage (%)', marker='o', markersize=3)
                    ax.plot(times, memory_data, color='#4ecdc4', linewidth=3, 
                           label='Memory Usage (%)', marker='s', markersize=3)
                
                # Styling
                ax.set_title('System Performance Metrics', color='white', fontsize=16, fontweight='bold')
                ax.set_xlabel('Time', color='white', fontsize=12)
                ax.set_ylabel('Usage (%)', color='white', fontsize=12)
                ax.tick_params(colors='white', labelsize=10)
                ax.grid(True, alpha=0.3, color='white')
                ax.legend(loc='upper left', facecolor='#161b22', edgecolor='white', labelcolor='white')
                ax.spines['bottom'].set_color('white')
                ax.spines['top'].set_color('white')
                ax.spines['right'].set_color('white')
                ax.spines['left'].set_color('white')
                ax.set_ylim(0, 100)
                
                # Convert to base64
                img_buffer = io.BytesIO()
                plt.savefig(img_buffer, format='png', facecolor='#0d1117', 
                           bbox_inches='tight', dpi=100)
                img_buffer.seek(0)
                img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
                plt.close()
                
                return jsonify({'image': f'data:image/png;base64,{img_base64}'})
                
            except Exception as e:
                try:
                    print(f"⚠️ Chart generation error: {e}")
                except UnicodeEncodeError:
                    print(f"Chart generation error: {e}")
                return jsonify({'error': str(e)})
    
    def setup_socketio_events(self):
        """Setup SocketIO real-time events"""
        
        @self.socketio.on('connect')
        def handle_connect():
            self.connected_clients += 1
            try:
                print(f"🔗 Client connected. Total: {self.connected_clients}")
            except UnicodeEncodeError:
                print(f"Client connected. Total: {self.connected_clients}")
            emit('status', {'connected_clients': self.connected_clients})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            self.connected_clients -= 1
            try:
                print(f"🔌 Client disconnected. Total: {self.connected_clients}")
            except UnicodeEncodeError:
                print(f"Client disconnected. Total: {self.connected_clients}")
        
        @self.socketio.on('get_real_time_data')
        def handle_real_time_data():
            """Send real-time system data"""
            try:
                system_data = {
                    'cpu_percent': psutil.cpu_percent(),
                    'memory_percent': psutil.virtual_memory().percent,
                    'timestamp': datetime.now().isoformat(),
                    'active_processes': len(psutil.pids())
                }
                emit('real_time_data', system_data)
            except Exception as e:
                try:
                    print(f"⚠️ Real-time data error: {e}")
                except UnicodeEncodeError:
                    print(f"Real-time data error: {e}")
    
    def start_background_monitoring(self):
        """Start background monitoring threads"""
        
        def broadcast_system_metrics():
            """Broadcast system metrics every 5 seconds"""
            while self.monitoring:
                try:
                    if self.connected_clients > 0:
                        system_data = {
                            'cpu_percent': psutil.cpu_percent(),
                            'memory_percent': psutil.virtual_memory().percent,
                            'timestamp': datetime.now().isoformat(),
                            'disk_percent': psutil.disk_usage('/').percent if hasattr(psutil, 'disk_usage') else 0
                        }
                        
                        self.socketio.emit('system_update', system_data)
                    
                    time.sleep(5)
                    
                except Exception as e:
                    try:
                        print(f"⚠️ Background monitoring error: {e}")
                    except UnicodeEncodeError:
                        print(f"Background monitoring error: {e}")
                    time.sleep(10)
        
        # Start monitoring thread
        monitor_thread = threading.Thread(target=broadcast_system_metrics, daemon=True)
        monitor_thread.start()
        
        try:
            print("✅ Background monitoring started")
        except UnicodeEncodeError:
            print("Background monitoring started")
    
    def create_html_template(self):
        """Create the futuristic HTML template"""
        
        templates_dir = Path("templates")
        templates_dir.mkdir(exist_ok=True)
        
        html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 Adaptive Chatbot - Futuristic Dashboard</title>
    <script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/js/all.min.js"></script>
    <style>
        /* Futuristic Dark Theme */
        :root {
            --bg-primary: #0d1117;
            --bg-secondary: #161b22;
            --bg-tertiary: #21262d;
            --text-primary: #f0f6fc;
            --text-secondary: #8b949e;
            --accent-blue: #00d8ff;
            --accent-green: #39d353;
            --accent-red: #ff6b6b;
            --accent-purple: #a855f7;
            --accent-orange: #ff8c42;
            --border-color: #30363d;
            --glow-color: rgba(0, 216, 255, 0.3);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            overflow-x: hidden;
        }

        /* Animated Background */
        .bg-animation {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -1;
            background: linear-gradient(45deg, #0d1117, #161b22, #21262d);
            background-size: 400% 400%;
            animation: gradientShift 15s ease infinite;
        }

        @keyframes gradientShift {
            0%, 100% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
        }

        /* Header */
        .header {
            background: var(--bg-secondary);
            padding: 1rem 2rem;
            border-bottom: 1px solid var(--border-color);
            box-shadow: 0 4px 20px rgba(0, 216, 255, 0.1);
        }

        .header-content {
            display: flex;
            justify-content: space-between;
            align-items: center;
            max-width: 1400px;
            margin: 0 auto;
        }

        .logo {
            font-size: 1.8rem;
            font-weight: bold;
            color: var(--accent-blue);
            text-shadow: 0 0 10px var(--glow-color);
        }

        .header-stats {
            display: flex;
            gap: 2rem;
            align-items: center;
        }

        .stat-item {
            text-align: center;
        }

        .stat-value {
            font-size: 1.2rem;
            font-weight: bold;
            color: var(--accent-green);
        }

        .stat-label {
            font-size: 0.8rem;
            color: var(--text-secondary);
            margin-top: 0.2rem;
        }

        /* Main Container */
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }

        /* Dashboard Grid */
        .dashboard-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2rem;
            margin-bottom: 2rem;
        }

        @media (max-width: 768px) {
            .dashboard-grid {
                grid-template-columns: 1fr;
            }
        }

        /* Cards */
        .card {
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }

        .card::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 2px;
            background: linear-gradient(90deg, transparent, var(--accent-blue), transparent);
            animation: shine 3s ease-in-out infinite;
        }

        @keyframes shine {
            0% { left: -100%; }
            100% { left: 100%; }
        }

        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 30px rgba(0, 216, 255, 0.2);
            border-color: var(--accent-blue);
        }

        .card-title {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 1.2rem;
            font-weight: bold;
            margin-bottom: 1rem;
            color: var(--text-primary);
        }

        .card-icon {
            font-size: 1.5rem;
            color: var(--accent-blue);
        }

        /* Metrics Cards */
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }

        .metric-card {
            background: linear-gradient(135deg, var(--bg-secondary), var(--bg-tertiary));
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 1.5rem;
            text-align: center;
            position: relative;
            overflow: hidden;
        }

        .metric-card::after {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(0, 216, 255, 0.1) 0%, transparent 70%);
            animation: pulse 4s ease-in-out infinite;
        }

        @keyframes pulse {
            0%, 100% { transform: scale(0.5); opacity: 0; }
            50% { transform: scale(1); opacity: 1; }
        }

        .metric-value {
            font-size: 2.5rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
            color: var(--accent-blue);
            text-shadow: 0 0 10px var(--glow-color);
        }

        .metric-label {
            font-size: 0.9rem;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        /* Chart Containers */
        .chart-container {
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 2rem;
        }

        .chart-img {
            width: 100%;
            border-radius: 8px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        }

        /* Conversations List */
        .conversations-list {
            max-height: 400px;
            overflow-y: auto;
            background: var(--bg-tertiary);
            border-radius: 8px;
            padding: 1rem;
        }

        .conversation-item {
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 0.5rem;
            transition: all 0.3s ease;
        }

        .conversation-item:hover {
            border-color: var(--accent-blue);
            transform: translateX(5px);
        }

        .conversation-text {
            color: var(--text-primary);
            margin-bottom: 0.5rem;
        }

        .conversation-meta {
            display: flex;
            justify-content: between;
            font-size: 0.8rem;
            color: var(--text-secondary);
        }

        .language-badge {
            background: var(--accent-purple);
            color: white;
            padding: 0.2rem 0.6rem;
            border-radius: 12px;
            font-size: 0.7rem;
            font-weight: bold;
        }

        /* Status Indicators */
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 0.5rem;
        }

        .status-online {
            background: var(--accent-green);
            box-shadow: 0 0 10px var(--accent-green);
            animation: heartbeat 2s ease-in-out infinite;
        }

        @keyframes heartbeat {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.1); }
        }

        .status-offline {
            background: var(--accent-red);
        }

        /* Loading Animation */
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 2px solid var(--border-color);
            border-radius: 50%;
            border-top-color: var(--accent-blue);
            animation: spin 1s ease-in-out infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        /* Footer */
        .footer {
            text-align: center;
            padding: 2rem;
            color: var(--text-secondary);
            border-top: 1px solid var(--border-color);
            margin-top: 3rem;
        }

        /* Responsive Design */
        @media (max-width: 768px) {
            .container {
                padding: 1rem;
            }
            
            .header-stats {
                gap: 1rem;
            }
            
            .metrics-grid {
                grid-template-columns: 1fr;
            }
        }

        /* Scrollbar Styling */
        ::-webkit-scrollbar {
            width: 8px;
        }

        ::-webkit-scrollbar-track {
            background: var(--bg-tertiary);
        }

        ::-webkit-scrollbar-thumb {
            background: var(--accent-blue);
            border-radius: 4px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: #00a8cc;
        }
    </style>
</head>
<body>
    <div class="bg-animation"></div>
    
    <!-- Header -->
    <header class="header">
        <div class="header-content">
            <div class="logo">
                <i class="fas fa-robot"></i> Adaptive Chatbot Dashboard
            </div>
            <div class="header-stats">
                <div class="stat-item">
                    <div class="stat-value" id="cpu-usage">0%</div>
                    <div class="stat-label">CPU Usage</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value" id="memory-usage">0%</div>
                    <div class="stat-label">Memory</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value" id="connected-clients">0</div>
                    <div class="stat-label">Connected</div>
                </div>
                <div class="stat-item">
                    <span class="status-indicator status-online" id="status-indicator"></span>
                    <span id="status-text">Online</span>
                </div>
            </div>
        </div>
    </header>

    <!-- Main Container -->
    <div class="container">
        
        <!-- Metrics Overview -->
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value" id="total-conversations">0</div>
                <div class="metric-label">Total Conversations</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" id="avg-response-time">0ms</div>
                <div class="metric-label">Avg Response Time</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" id="languages-detected">0</div>
                <div class="metric-label">Languages Detected</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" id="voice-interactions">0</div>
                <div class="metric-label">Voice Interactions</div>
            </div>
        </div>

        <!-- Dashboard Grid -->
        <div class="dashboard-grid">
            
            <!-- Conversations Trend Chart -->
            <div class="card">
                <div class="card-title">
                    <i class="fas fa-chart-line card-icon"></i>
                    Conversation Trends
                </div>
                <div class="chart-container">
                    <img id="conversations-chart" class="chart-img" alt="Loading chart..." />
                </div>
            </div>

            <!-- System Performance Chart -->
            <div class="card">
                <div class="card-title">
                    <i class="fas fa-tachometer-alt card-icon"></i>
                    System Performance
                </div>
                <div class="chart-container">
                    <img id="system-chart" class="chart-img" alt="Loading chart..." />
                </div>
            </div>

        </div>

        <!-- Recent Conversations -->
        <div class="card">
            <div class="card-title">
                <i class="fas fa-comments card-icon"></i>
                Recent Conversations
            </div>
            <div class="conversations-list" id="conversations-list">
                <div class="loading"></div>
            </div>
        </div>

    </div>

    <!-- Footer -->
    <footer class="footer">
        <p>🤖 Adaptive Chatbot Professional Dashboard v2.0 | Built with ❤️ for the Future</p>
        <p>Real-time monitoring powered by Flask & SocketIO</p>
    </footer>

    <script>
        // Initialize Socket.IO
        const socket = io();

        // DOM Elements
        const elements = {
            cpuUsage: document.getElementById('cpu-usage'),
            memoryUsage: document.getElementById('memory-usage'),
            connectedClients: document.getElementById('connected-clients'),
            statusIndicator: document.getElementById('status-indicator'),
            statusText: document.getElementById('status-text'),
            totalConversations: document.getElementById('total-conversations'),
            avgResponseTime: document.getElementById('avg-response-time'),
            languagesDetected: document.getElementById('languages-detected'),
            voiceInteractions: document.getElementById('voice-interactions'),
            conversationsChart: document.getElementById('conversations-chart'),
            systemChart: document.getElementById('system-chart'),
            conversationsList: document.getElementById('conversations-list')
        };

        // Socket.IO Event Handlers
        socket.on('connect', () => {
            console.log('Connected to server');
            elements.statusIndicator.className = 'status-indicator status-online';
            elements.statusText.textContent = 'Online';
            loadInitialData();
        });

        socket.on('disconnect', () => {
            console.log('Disconnected from server');
            elements.statusIndicator.className = 'status-indicator status-offline';
            elements.statusText.textContent = 'Offline';
        });

        socket.on('system_update', (data) => {
            updateSystemMetrics(data);
        });

        // Update system metrics
        function updateSystemMetrics(data) {
            elements.cpuUsage.textContent = `${data.cpu_percent.toFixed(1)}%`;
            elements.memoryUsage.textContent = `${data.memory_percent.toFixed(1)}%`;
            
            // Update CPU color based on usage
            if (data.cpu_percent > 80) {
                elements.cpuUsage.style.color = 'var(--accent-red)';
            } else if (data.cpu_percent > 60) {
                elements.cpuUsage.style.color = 'var(--accent-orange)';
            } else {
                elements.cpuUsage.style.color = 'var(--accent-green)';
            }
            
            // Update memory color based on usage
            if (data.memory_percent > 80) {
                elements.memoryUsage.style.color = 'var(--accent-red)';
            } else if (data.memory_percent > 60) {
                elements.memoryUsage.style.color = 'var(--accent-orange)';
            } else {
                elements.memoryUsage.style.color = 'var(--accent-green)';
            }
        }

        // Load initial data
        async function loadInitialData() {
            try {
                // Load conversations
                const conversationsResponse = await fetch('/api/conversations');
                const conversations = await conversationsResponse.json();
                updateConversationsMetrics(conversations);
                updateConversationsList(conversations);

                // Load charts
                loadCharts();

            } catch (error) {
                console.error('Error loading initial data:', error);
            }
        }

        // Update conversations metrics
        function updateConversationsMetrics(conversations) {
            elements.totalConversations.textContent = conversations.length;
            
            if (conversations.length > 0) {
                // Calculate average response time
                const totalResponseTime = conversations.reduce((sum, conv) => sum + (conv.response_time || 0), 0);
                const avgResponseTime = totalResponseTime / conversations.length;
                elements.avgResponseTime.textContent = `${Math.round(avgResponseTime)}ms`;
                
                // Count unique languages
                const languages = new Set(conversations.map(conv => conv.language).filter(lang => lang));
                elements.languagesDetected.textContent = languages.size;
                
                // Count voice interactions (assuming all are voice for now)
                elements.voiceInteractions.textContent = conversations.length;
            }
        }

        // Update conversations list
        function updateConversationsList(conversations) {
            const listElement = elements.conversationsList;
            listElement.innerHTML = '';
            
            if (conversations.length === 0) {
                listElement.innerHTML = '<p style="text-align: center; color: var(--text-secondary);">No conversations yet</p>';
                return;
            }
            
            conversations.slice(0, 10).forEach(conv => {
                const item = document.createElement('div');
                item.className = 'conversation-item';
                
                const text = conv.input_text || 'No input text';
                const response = conv.response || 'No response';
                const language = conv.language || 'Unknown';
                const timestamp = conv.timestamp ? new Date(conv.timestamp).toLocaleString() : 'Unknown time';
                
                item.innerHTML = `
                    <div class="conversation-text">
                        <strong>Input:</strong> ${text.substring(0, 100)}${text.length > 100 ? '...' : ''}
                    </div>
                    <div class="conversation-text">
                        <strong>Response:</strong> ${response.substring(0, 100)}${response.length > 100 ? '...' : ''}
                    </div>
                    <div class="conversation-meta">
                        <span><span class="language-badge">${language}</span></span>
                        <span>${timestamp}</span>
                    </div>
                `;
                
                listElement.appendChild(item);
            });
        }

        // Load charts
        async function loadCharts() {
            try {
                // Load conversations trend chart
                const convChartResponse = await fetch('/api/charts/conversations_trend');
                const convChartData = await convChartResponse.json();
                if (convChartData.image) {
                    elements.conversationsChart.src = convChartData.image;
                }

                // Load system performance chart
                const sysChartResponse = await fetch('/api/charts/system_performance');
                const sysChartData = await sysChartResponse.json();
                if (sysChartData.image) {
                    elements.systemChart.src = sysChartData.image;
                }

            } catch (error) {
                console.error('Error loading charts:', error);
            }
        }

        // Refresh data periodically
        setInterval(loadInitialData, 30000); // Refresh every 30 seconds
        setInterval(loadCharts, 60000); // Refresh charts every minute

        // Request real-time data
        socket.emit('get_real_time_data');
        setInterval(() => socket.emit('get_real_time_data'), 5000);

    </script>
</body>
</html>'''
        
        template_path = templates_dir / "futuristic_dashboard.html"
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        try:
            print(f"✅ Created HTML template: {template_path}")
        except UnicodeEncodeError:
            print(f"Created HTML template: {template_path}")
        return template_path
    
    def run(self, host='0.0.0.0', port=5000, debug=False):
        """Run the Flask web application"""
        
        # Create HTML template
        self.create_html_template()
        
        try:
            print(f"🌐 Starting Futuristic Web Interface...")
            print(f"🚀 Dashboard will be available at: http://localhost:{port}")
            print("🎨 Featuring modern UI/UX with real-time updates")
        except UnicodeEncodeError:
            print(f"Starting Futuristic Web Interface...")
            print(f"Dashboard will be available at: http://localhost:{port}")
            print("Featuring modern UI/UX with real-time updates")
        
        try:
            self.socketio.run(
                self.app,
                host=host,
                port=port,
                debug=debug,
                allow_unsafe_werkzeug=True
            )
        except KeyboardInterrupt:
            try:
                print("✅ Web Interface stopped by user")
            except UnicodeEncodeError:
                print("Web Interface stopped by user")
        except Exception as e:
            try:
                print(f"⚠️ Web Interface error: {e}")
            except UnicodeEncodeError:
                print(f"Web Interface error: {e}")
        finally:
            self.monitoring = False
            try:
                print("🔚 Web Interface closed")
            except UnicodeEncodeError:
                print("Web Interface closed")

if __name__ == "__main__":
    try:
        print("🌐 Adaptive Chatbot Futuristic Web Interface")
    except UnicodeEncodeError:
        print("Web Adaptive Chatbot Futuristic Web Interface")
    print("=" * 60)
    
    try:
        web_interface = FuturisticWebInterface()
        web_interface.run(debug=True)
    except Exception as e:
        try:
            print(f"⚠️ Failed to start web interface: {e}")
        except UnicodeEncodeError:
            print(f"Failed to start web interface: {e}")
        input("Press Enter to exit...")