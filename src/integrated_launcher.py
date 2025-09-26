#!/usr/bin/env python3
"""
🚀 Integrated Launcher for Adaptive Chatbot Professional Suite
Launches and coordinates all system components
"""

import sys
import subprocess
import threading
import time
import webbrowser
from pathlib import Path
import psutil
import os
from datetime import datetime
import json

class IntegratedLauncher:
    """Professional launcher for all adaptive chatbot components"""
    
    def __init__(self):
        self.project_dir = Path(__file__).parent.absolute()
        self.processes = {}
        self.components = {
            'main_chatbot': {
                'name': 'Main Adaptive Chatbot',
                'script': 'main_adaptive_chatbot.py',
                'description': 'Core voice chat system with multilingual support',
                'icon': '🤖',
                'required': True,
                'port': None
            },
            'advanced_debugger': {
                'name': 'Advanced Debugger & Tracker',
                'script': 'advanced_debugger_tracker.py',
                'description': 'Real-time voice chat debugging and performance tracking',
                'icon': '🔍',
                'required': False,
                'port': 8765
            },
            'desktop_monitor': {
                'name': 'Desktop Monitor App',
                'script': 'desktop_monitor_app.py',
                'description': 'Professional desktop monitoring dashboard',
                'icon': '🖥️',
                'required': False,
                'port': None
            },
            'web_interface': {
                'name': 'Futuristic Web Interface',
                'script': 'web_interface_app.py',
                'description': 'Modern web-based monitoring dashboard',
                'icon': '🌐',
                'required': False,
                'port': 5000
            }
        }
        
        print("🚀 Integrated Launcher initialized")
        self.print_banner()
    
    def print_banner(self):
        """Print professional banner"""
        banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║    🤖 ADAPTIVE CHATBOT PROFESSIONAL SUITE v2.0                             ║
║                                                                              ║
║    🎯 Professional Multilingual Voice Assistant                             ║
║    🔧 Advanced Debugging & Performance Tracking                             ║
║    📊 Real-time Monitoring & Analytics Dashboard                            ║
║    🌐 Modern Web Interface with Futuristic UI/UX                            ║
║                                                                              ║
║    Built with ❤️ for Professional Voice AI Applications                     ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
        """
        print(banner)
        print(f"📍 Project Directory: {self.project_dir}")
        print(f"⏰ Launch Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
    
    def check_dependencies(self):
        """Check if all required files and dependencies exist"""
        
        print("🔍 Checking system dependencies...")
        
        missing_files = []
        for component_id, component in self.components.items():
            script_path = self.project_dir / component['script']
            if not script_path.exists():
                missing_files.append(f"{component['icon']} {component['script']}")
        
        if missing_files:
            print("❌ Missing required files:")
            for file in missing_files:
                print(f"   • {file}")
            return False
        
        # Check Python packages
        package_mapping = {
            'flask': 'flask',
            'flask_socketio': 'flask_socketio',
            'sqlite3': 'sqlite3',
            'psutil': 'psutil',
            'matplotlib': 'matplotlib',
            'speech_recognition': 'speech_recognition',
            'pyttsx3': 'pyttsx3',
            'edge_tts': 'edge_tts',
            'langdetect': 'langdetect',
            'customtkinter': 'customtkinter',
            'websockets': 'websockets',
            'numpy': 'numpy',
            'transformers': 'transformers'
        }
        
        missing_packages = []
        for package_name, import_name in package_mapping.items():
            try:
                __import__(import_name)
            except ImportError:
                missing_packages.append(package_name)
        
        if missing_packages:
            print("⚠️ Missing Python packages:")
            for package in missing_packages:
                print(f"   • {package}")
            print("\n💡 Install missing packages with:")
            print(f"   pip install {' '.join(missing_packages)}")
        
        print("✅ All dependencies checked")
        return len(missing_files) == 0
    
    def show_launcher_menu(self):
        """Show interactive launcher menu"""
        
        while True:
            print("\n" + "="*60)
            print("🚀 ADAPTIVE CHATBOT PROFESSIONAL LAUNCHER")
            print("="*60)
            
            # Show available components
            print("\n📋 Available Components:")
            for i, (component_id, component) in enumerate(self.components.items(), 1):
                status = "🟢 Running" if component_id in self.processes else "⚪ Stopped"
                required = "⭐ Required" if component['required'] else "🔧 Optional"
                
                print(f"  {i}. {component['icon']} {component['name']:<30} {status:<12} {required}")
                print(f"      📝 {component['description']}")
                if component.get('port'):
                    print(f"      🌐 Port: {component['port']}")
                print()
            
            # Show control options
            print("🎛️ Control Options:")
            print("  A. 🚀 Launch All Components")
            print("  B. 🛑 Stop All Components")
            print("  C. 📊 System Status")
            print("  D. 🌐 Open Web Dashboard")
            print("  E. 🖥️ Open Desktop Monitor")
            print("  F. 📦 Build Installer")
            print("  Q. 🚪 Quit Launcher")
            
            print("\n" + "-"*60)
            choice = input("Enter your choice: ").upper().strip()
            
            if choice == 'Q':
                self.shutdown_all()
                break
            elif choice == 'A':
                self.launch_all_components()
            elif choice == 'B':
                self.stop_all_components()
            elif choice == 'C':
                self.show_system_status()
            elif choice == 'D':
                self.open_web_dashboard()
            elif choice == 'E':
                self.launch_desktop_monitor()
            elif choice == 'F':
                self.launch_installer_builder()
            elif choice.isdigit():
                component_index = int(choice) - 1
                component_ids = list(self.components.keys())
                if 0 <= component_index < len(component_ids):
                    component_id = component_ids[component_index]
                    self.toggle_component(component_id)
                else:
                    print("❌ Invalid component number")
            else:
                print("❌ Invalid choice")
            
            input("\nPress Enter to continue...")
    
    def launch_component(self, component_id):
        """Launch a specific component"""
        
        if component_id in self.processes:
            print(f"⚠️ {self.components[component_id]['name']} is already running")
            return False
        
        component = self.components[component_id]
        script_path = self.project_dir / component['script']
        
        print(f"🚀 Starting {component['icon']} {component['name']}...")
        
        try:
            # Launch the component as a subprocess
            process = subprocess.Popen(
                [sys.executable, str(script_path)],
                cwd=self.project_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self.processes[component_id] = {
                'process': process,
                'component': component,
                'start_time': datetime.now()
            }
            
            # Start output monitoring in a separate thread
            monitor_thread = threading.Thread(
                target=self.monitor_component_output,
                args=(component_id, process),
                daemon=True
            )
            monitor_thread.start()
            
            # Give the component time to start
            time.sleep(2)
            
            # Check if process is still running
            if process.poll() is None:
                print(f"✅ {component['name']} started successfully")
                if component.get('port'):
                    print(f"🌐 Available at: http://localhost:{component['port']}")
                return True
            else:
                print(f"❌ {component['name']} failed to start")
                del self.processes[component_id]
                return False
            
        except Exception as e:
            print(f"❌ Failed to start {component['name']}: {e}")
            return False
    
    def stop_component(self, component_id):
        """Stop a specific component"""
        
        if component_id not in self.processes:
            print(f"⚠️ {self.components[component_id]['name']} is not running")
            return False
        
        component_info = self.processes[component_id]
        component = component_info['component']
        process = component_info['process']
        
        print(f"🛑 Stopping {component['icon']} {component['name']}...")
        
        try:
            # Terminate the process gracefully
            process.terminate()
            
            # Wait for process to terminate (with timeout)
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # Force kill if it doesn't terminate gracefully
                process.kill()
                process.wait()
            
            del self.processes[component_id]
            print(f"✅ {component['name']} stopped successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error stopping {component['name']}: {e}")
            return False
    
    def toggle_component(self, component_id):
        """Toggle a component (start if stopped, stop if running)"""
        
        if component_id in self.processes:
            self.stop_component(component_id)
        else:
            self.launch_component(component_id)
    
    def launch_all_components(self):
        """Launch all components in proper order"""
        
        print("🚀 Launching all components...")
        
        # Launch order: main chatbot first, then supporting components
        launch_order = ['main_chatbot', 'advanced_debugger', 'web_interface']
        
        success_count = 0
        for component_id in launch_order:
            if self.launch_component(component_id):
                success_count += 1
                time.sleep(3)  # Wait between launches
        
        print(f"\n🎉 Launched {success_count}/{len(launch_order)} components successfully!")
        
        # Automatically open web dashboard if web interface started
        if 'web_interface' in self.processes:
            time.sleep(5)  # Wait for web server to be ready
            self.open_web_dashboard()
    
    def stop_all_components(self):
        """Stop all running components"""
        
        print("🛑 Stopping all components...")
        
        stopped_count = 0
        for component_id in list(self.processes.keys()):
            if self.stop_component(component_id):
                stopped_count += 1
                time.sleep(1)
        
        print(f"✅ Stopped {stopped_count} components")
    
    def monitor_component_output(self, component_id, process):
        """Monitor component output in a separate thread"""
        
        component = self.components[component_id]
        
        while process.poll() is None:
            try:
                # Read output line by line
                line = process.stdout.readline()
                if line:
                    # Log important messages
                    if any(keyword in line.lower() for keyword in ['error', 'failed', 'exception']):
                        print(f"❌ {component['icon']} {component_id}: {line.strip()}")
                    elif any(keyword in line.lower() for keyword in ['started', 'ready', 'listening']):
                        print(f"✅ {component['icon']} {component_id}: {line.strip()}")
                
                time.sleep(0.1)
                
            except Exception as e:
                print(f"❌ Error monitoring {component_id}: {e}")
                break
    
    def show_system_status(self):
        """Show detailed system status"""
        
        print("\n📊 SYSTEM STATUS REPORT")
        print("="*50)
        
        # System resources
        print(f"💾 Memory Usage: {psutil.virtual_memory().percent:.1f}%")
        print(f"🖥️  CPU Usage: {psutil.cpu_percent()}%")
        print(f"💽 Disk Usage: {psutil.disk_usage('/').percent:.1f}%" if hasattr(psutil, 'disk_usage') else "💽 Disk Usage: N/A")
        
        # Running components
        print(f"\n🏃 Running Components: {len(self.processes)}/{len(self.components)}")
        
        for component_id, component in self.components.items():
            if component_id in self.processes:
                start_time = self.processes[component_id]['start_time']
                uptime = datetime.now() - start_time
                process = self.processes[component_id]['process']
                
                print(f"  ✅ {component['icon']} {component['name']}")
                print(f"     📊 PID: {process.pid}")
                print(f"     ⏱️ Uptime: {uptime}")
                if component.get('port'):
                    print(f"     🌐 Port: {component['port']}")
            else:
                print(f"  ⚪ {component['icon']} {component['name']} (Stopped)")
        
        # Ports in use
        print(f"\n🌐 Network Ports:")
        for component_id, component in self.components.items():
            if component.get('port') and component_id in self.processes:
                print(f"  • Port {component['port']}: {component['name']}")
    
    def open_web_dashboard(self):
        """Open the web dashboard in default browser"""
        
        if 'web_interface' not in self.processes:
            print("❌ Web interface is not running")
            print("💡 Start the web interface first")
            return
        
        url = "http://localhost:5000"
        print(f"🌐 Opening web dashboard: {url}")
        
        try:
            webbrowser.open(url)
            print("✅ Web dashboard opened in browser")
        except Exception as e:
            print(f"❌ Failed to open browser: {e}")
            print(f"💡 Manually navigate to: {url}")
    
    def launch_desktop_monitor(self):
        """Launch the desktop monitor application"""
        
        if 'desktop_monitor' in self.processes:
            print("⚠️ Desktop monitor is already running")
            return
        
        print("🖥️ Starting desktop monitor application...")
        self.launch_component('desktop_monitor')
    
    def launch_installer_builder(self):
        """Launch the installer builder"""
        
        builder_script = self.project_dir / 'build_professional_installer.py'
        
        if not builder_script.exists():
            print("❌ Installer builder script not found")
            return
        
        print("📦 Starting professional installer builder...")
        
        try:
            subprocess.run([sys.executable, str(builder_script)], cwd=self.project_dir)
        except Exception as e:
            print(f"❌ Failed to start installer builder: {e}")
    
    def shutdown_all(self):
        """Gracefully shutdown all components"""
        
        print("\n🛑 Shutting down Adaptive Chatbot Professional Suite...")
        
        self.stop_all_components()
        
        print("✅ All components stopped")
        print("🔚 Thank you for using Adaptive Chatbot Professional Suite!")
        print("💫 Built with ❤️ for the Future of Voice AI")
    
    def save_session(self):
        """Save current session configuration"""
        
        session_data = {
            'timestamp': datetime.now().isoformat(),
            'running_components': list(self.processes.keys()),
            'project_dir': str(self.project_dir)
        }
        
        session_file = self.project_dir / 'launcher_session.json'
        
        try:
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2)
            print(f"✅ Session saved to: {session_file}")
        except Exception as e:
            print(f"❌ Failed to save session: {e}")
    
    def load_session(self):
        """Load previous session configuration"""
        
        session_file = self.project_dir / 'launcher_session.json'
        
        if not session_file.exists():
            return
        
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            print(f"📂 Found previous session from: {session_data.get('timestamp', 'Unknown')}")
            
            if input("🔄 Restore previous session? (y/N): ").lower().startswith('y'):
                for component_id in session_data.get('running_components', []):
                    if component_id in self.components:
                        self.launch_component(component_id)
                        time.sleep(2)
                
                print("✅ Session restored")
            
        except Exception as e:
            print(f"❌ Failed to load session: {e}")
    
    def run(self):
        """Run the integrated launcher"""
        
        try:
            # Check dependencies
            if not self.check_dependencies():
                print("\n❌ Dependency check failed!")
                input("Press Enter to continue anyway or Ctrl+C to exit...")
            
            # Load previous session
            self.load_session()
            
            # Show main menu
            self.show_launcher_menu()
            
        except KeyboardInterrupt:
            print("\n\n🛑 Launcher interrupted by user")
        except Exception as e:
            print(f"\n❌ Launcher error: {e}")
        finally:
            self.save_session()
            self.shutdown_all()

if __name__ == "__main__":
    print("🚀 Adaptive Chatbot Professional Suite - Integrated Launcher")
    print("=" * 70)
    
    try:
        launcher = IntegratedLauncher()
        launcher.run()
    except Exception as e:
        print(f"❌ Critical launcher error: {e}")
        input("Press Enter to exit...")