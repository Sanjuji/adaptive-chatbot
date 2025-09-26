#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
System Health Check - Comprehensive Diagnostics for Adaptive Chatbot
Performs deep analysis and identifies critical issues across all components.
"""

import os
import sys
import json
import traceback
import platform
import subprocess
import importlib
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")

class SystemHealthChecker:
    """Comprehensive system health and diagnostics checker"""
    
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'system_info': {},
            'dependencies': {},
            'modules': {},
            'performance': {},
            'security': {},
            'files': {},
            'issues': [],
            'recommendations': []
        }
        
    def run_comprehensive_check(self) -> Dict[str, Any]:
        """Run complete system health check"""
        print("🔍 COMPREHENSIVE SYSTEM HEALTH CHECK")
        print("=" * 50)
        
        # System information
        print("\n1️⃣ System Information...")
        self._check_system_info()
        
        # Dependencies check
        print("\n2️⃣ Dependencies Check...")
        self._check_dependencies()
        
        # Module integrity
        print("\n3️⃣ Module Integrity Check...")
        self._check_modules()
        
        # Performance analysis
        print("\n4️⃣ Performance Analysis...")
        self._check_performance()
        
        # Security validation
        print("\n5️⃣ Security Validation...")
        self._check_security()
        
        # File system check
        print("\n6️⃣ File System Check...")
        self._check_files()
        
        # Generate report
        self._generate_report()
        
        return self.results
    
    def _check_system_info(self):
        """Check system information and compatibility"""
        try:
            self.results['system_info'] = {
                'platform': platform.platform(),
                'system': platform.system(),
                'machine': platform.machine(),
                'processor': platform.processor(),
                'python_version': sys.version,
                'python_executable': sys.executable,
                'current_dir': os.getcwd(),
                'user': os.getenv('USERNAME') or os.getenv('USER', 'unknown'),
                'path_separator': os.sep
            }
            
            print(f"✅ Platform: {platform.platform()}")
            print(f"✅ Python: {sys.version.split()[0]}")
            
            # Check Python version compatibility
            version = sys.version_info
            if version.major < 3 or (version.major == 3 and version.minor < 8):
                self.results['issues'].append({
                    'severity': 'HIGH',
                    'type': 'COMPATIBILITY',
                    'message': f'Python {version.major}.{version.minor} may not be fully supported. Recommend Python 3.8+'
                })
                
        except Exception as e:
            self._add_issue('SYSTEM_INFO', 'MEDIUM', f'System info check failed: {e}')
    
    def _check_dependencies(self):
        """Check all required dependencies"""
        required_packages = {
            'edge-tts': 'EdgeTTS for voice synthesis',
            'pygame': 'Audio playback',
            'speechrecognition': 'Speech recognition',
            'pyaudio': 'Audio input (optional)',
            'requests': 'HTTP requests',
            'configparser': 'Configuration management'
        }
        
        self.results['dependencies'] = {}
        
        for package, description in required_packages.items():
            try:
                if package == 'speechrecognition':
                    import speech_recognition as sr
                    version = getattr(sr, '__version__', 'unknown')
                elif package == 'edge-tts':
                    import edge_tts
                    version = getattr(edge_tts, '__version__', 'unknown')
                else:
                    module = importlib.import_module(package.replace('-', '_'))
                    version = getattr(module, '__version__', 'unknown')
                
                self.results['dependencies'][package] = {
                    'status': 'AVAILABLE',
                    'version': version,
                    'description': description
                }
                print(f"✅ {package}: {version}")
                
            except ImportError as e:
                self.results['dependencies'][package] = {
                    'status': 'MISSING',
                    'version': None,
                    'description': description,
                    'error': str(e)
                }
                severity = 'HIGH' if package in ['edge-tts', 'pygame', 'speechrecognition'] else 'MEDIUM'
                self._add_issue('DEPENDENCY', severity, f'Missing package: {package} - {description}')
                print(f"❌ {package}: MISSING")
                
    def _check_modules(self):
        """Check integrity of custom modules"""
        core_modules = [
            'config.py',
            'logger.py', 
            'simple_voice.py',
            'unified_learning_manager.py',
            'validators.py',
            'adaptive_chatbot.py'
        ]
        
        self.results['modules'] = {}
        
        for module_file in core_modules:
            try:
                if os.path.exists(module_file):
                    # Try to compile
                    with open(module_file, 'r', encoding='utf-8') as f:
                        code = f.read()
                    
                    compile(code, module_file, 'exec')
                    
                    self.results['modules'][module_file] = {
                        'status': 'OK',
                        'size': len(code),
                        'lines': len(code.splitlines())
                    }
                    print(f"✅ {module_file}: OK")
                else:
                    self.results['modules'][module_file] = {
                        'status': 'MISSING',
                        'size': 0,
                        'lines': 0
                    }
                    self._add_issue('MODULE', 'HIGH', f'Missing core module: {module_file}')
                    print(f"❌ {module_file}: MISSING")
                    
            except SyntaxError as e:
                self.results['modules'][module_file] = {
                    'status': 'SYNTAX_ERROR',
                    'error': str(e),
                    'line': e.lineno
                }
                self._add_issue('MODULE', 'HIGH', f'Syntax error in {module_file}: {e}')
                print(f"❌ {module_file}: SYNTAX ERROR")
                
            except Exception as e:
                self.results['modules'][module_file] = {
                    'status': 'ERROR',
                    'error': str(e)
                }
                self._add_issue('MODULE', 'MEDIUM', f'Module check failed for {module_file}: {e}')
                print(f"⚠️ {module_file}: ERROR")
    
    def _check_performance(self):
        """Check system performance characteristics"""
        try:
            import time
            import psutil
            
            # Memory check
            memory = psutil.virtual_memory()
            available_mb = memory.available // (1024 * 1024)
            
            # Disk space check
            disk = psutil.disk_usage('.')
            free_gb = disk.free // (1024 * 1024 * 1024)
            
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            self.results['performance'] = {
                'memory_available_mb': available_mb,
                'disk_free_gb': free_gb,
                'cpu_percent': cpu_percent,
                'cpu_count': psutil.cpu_count()
            }
            
            print(f"✅ Memory Available: {available_mb} MB")
            print(f"✅ Disk Free: {free_gb} GB")
            print(f"✅ CPU Usage: {cpu_percent}%")
            
            # Performance warnings
            if available_mb < 512:
                self._add_issue('PERFORMANCE', 'MEDIUM', f'Low memory: {available_mb}MB available')
            
            if free_gb < 1:
                self._add_issue('PERFORMANCE', 'HIGH', f'Low disk space: {free_gb}GB free')
                
            if cpu_percent > 80:
                self._add_issue('PERFORMANCE', 'MEDIUM', f'High CPU usage: {cpu_percent}%')
                
        except ImportError:
            print("⚠️ psutil not available - skipping performance check")
            self.results['performance'] = {'status': 'UNAVAILABLE'}
        except Exception as e:
            self._add_issue('PERFORMANCE', 'LOW', f'Performance check failed: {e}')
    
    def _check_security(self):
        """Check security configurations and vulnerabilities"""
        security_checks = []
        
        # File permissions check
        try:
            for file_path in ['adaptive_chatbot.py', 'config.py']:
                if os.path.exists(file_path):
                    stat = os.stat(file_path)
                    mode = oct(stat.st_mode)[-3:]
                    if mode == '777':
                        security_checks.append({
                            'check': 'file_permissions',
                            'status': 'WARN',
                            'message': f'{file_path} has overly permissive permissions: {mode}'
                        })
                    else:
                        security_checks.append({
                            'check': 'file_permissions', 
                            'status': 'OK',
                            'message': f'{file_path} permissions: {mode}'
                        })
        except Exception as e:
            security_checks.append({
                'check': 'file_permissions',
                'status': 'ERROR',
                'message': f'Permission check failed: {e}'
            })
        
        # Configuration security
        try:
            if os.path.exists('config.py'):
                with open('config.py', 'r') as f:
                    config_content = f.read()
                
                dangerous_patterns = ['password', 'secret', 'key', 'token', 'api_key']
                found_secrets = []
                
                for pattern in dangerous_patterns:
                    if pattern in config_content.lower():
                        found_secrets.append(pattern)
                
                if found_secrets:
                    security_checks.append({
                        'check': 'config_secrets',
                        'status': 'WARN',
                        'message': f'Potential secrets in config: {found_secrets}'
                    })
                else:
                    security_checks.append({
                        'check': 'config_secrets',
                        'status': 'OK',
                        'message': 'No obvious secrets in config'
                    })
        except Exception as e:
            security_checks.append({
                'check': 'config_secrets',
                'status': 'ERROR', 
                'message': f'Config security check failed: {e}'
            })
        
        self.results['security'] = {'checks': security_checks}
        
        for check in security_checks:
            status_icon = "✅" if check['status'] == 'OK' else "⚠️" if check['status'] == 'WARN' else "❌"
            print(f"{status_icon} {check['check']}: {check['message']}")
            
            if check['status'] in ['WARN', 'ERROR']:
                severity = 'MEDIUM' if check['status'] == 'WARN' else 'HIGH'
                self._add_issue('SECURITY', severity, check['message'])
    
    def _check_files(self):
        """Check file system integrity and structure"""
        required_dirs = ['data', 'logs']
        optional_dirs = ['backups', 'exports']
        
        self.results['files'] = {
            'directories': {},
            'data_files': {},
            'log_files': {}
        }
        
        # Check directories
        for dir_name in required_dirs:
            if os.path.exists(dir_name) and os.path.isdir(dir_name):
                self.results['files']['directories'][dir_name] = {'status': 'EXISTS', 'required': True}
                print(f"✅ Directory: {dir_name}/")
            else:
                self.results['files']['directories'][dir_name] = {'status': 'MISSING', 'required': True}
                self._add_issue('FILESYSTEM', 'MEDIUM', f'Missing required directory: {dir_name}/')
                print(f"❌ Directory: {dir_name}/ (MISSING)")
        
        for dir_name in optional_dirs:
            if os.path.exists(dir_name) and os.path.isdir(dir_name):
                self.results['files']['directories'][dir_name] = {'status': 'EXISTS', 'required': False}
                print(f"✅ Directory: {dir_name}/ (optional)")
        
        # Check data files
        data_files = ['data/knowledge_base.json', 'data/config.ini']
        for file_path in data_files:
            if os.path.exists(file_path):
                stat = os.stat(file_path)
                self.results['files']['data_files'][file_path] = {
                    'status': 'EXISTS',
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                }
                print(f"✅ Data file: {file_path} ({stat.st_size} bytes)")
            else:
                self.results['files']['data_files'][file_path] = {'status': 'MISSING'}
                print(f"⚠️ Data file: {file_path} (will be created)")
    
    def _add_issue(self, category: str, severity: str, message: str):
        """Add issue to results"""
        self.results['issues'].append({
            'category': category,
            'severity': severity,
            'message': message,
            'timestamp': datetime.now().isoformat()
        })
    
    def _generate_report(self):
        """Generate comprehensive report with recommendations"""
        print(f"\n{'='*50}")
        print("📋 HEALTH CHECK SUMMARY")
        print(f"{'='*50}")
        
        # Count issues by severity
        high_issues = [i for i in self.results['issues'] if i['severity'] == 'HIGH']
        medium_issues = [i for i in self.results['issues'] if i['severity'] == 'MEDIUM']
        low_issues = [i for i in self.results['issues'] if i['severity'] == 'LOW']
        
        print(f"🚨 High Priority Issues: {len(high_issues)}")
        print(f"⚠️ Medium Priority Issues: {len(medium_issues)}")
        print(f"💡 Low Priority Issues: {len(low_issues)}")
        
        # Show critical issues
        if high_issues:
            print(f"\n🚨 CRITICAL ISSUES:")
            for issue in high_issues:
                print(f"   • {issue['message']}")
        
        if medium_issues:
            print(f"\n⚠️ MEDIUM PRIORITY ISSUES:")
            for issue in medium_issues[:5]:  # Show first 5
                print(f"   • {issue['message']}")
        
        # Generate recommendations
        self._generate_recommendations()
        
        if self.results['recommendations']:
            print(f"\n💡 RECOMMENDATIONS:")
            for rec in self.results['recommendations']:
                print(f"   • {rec}")
        
        # Overall health score
        total_issues = len(self.results['issues'])
        if total_issues == 0:
            health_score = 100
            health_status = "EXCELLENT"
        elif len(high_issues) > 0:
            health_score = max(60 - len(high_issues) * 10, 30)
            health_status = "CRITICAL"
        elif len(medium_issues) > 3:
            health_score = max(80 - len(medium_issues) * 5, 50)
            health_status = "NEEDS ATTENTION"
        else:
            health_score = max(90 - total_issues * 2, 70)
            health_status = "GOOD"
        
        self.results['health_score'] = health_score
        self.results['health_status'] = health_status
        
        print(f"\n🏥 OVERALL HEALTH SCORE: {health_score}/100 ({health_status})")
        
        # Save report
        try:
            report_file = f"system_health_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            print(f"📄 Detailed report saved: {report_file}")
        except Exception as e:
            print(f"⚠️ Could not save report: {e}")
    
    def _generate_recommendations(self):
        """Generate actionable recommendations based on issues"""
        recs = []
        
        # Dependency recommendations
        missing_deps = [pkg for pkg, info in self.results.get('dependencies', {}).items() 
                       if info.get('status') == 'MISSING']
        if missing_deps:
            recs.append(f"Install missing packages: pip install {' '.join(missing_deps)}")
        
        # Performance recommendations
        perf = self.results.get('performance', {})
        if perf.get('memory_available_mb', 9999) < 512:
            recs.append("Close other applications to free up memory")
        
        if perf.get('disk_free_gb', 999) < 1:
            recs.append("Free up disk space or move chatbot to a location with more space")
        
        # Module recommendations
        missing_modules = [mod for mod, info in self.results.get('modules', {}).items() 
                          if info.get('status') in ['MISSING', 'SYNTAX_ERROR']]
        if missing_modules:
            recs.append(f"Fix or restore missing/corrupted modules: {', '.join(missing_modules)}")
        
        # File system recommendations  
        missing_dirs = [dir_name for dir_name, info in self.results.get('files', {}).get('directories', {}).items()
                       if info.get('status') == 'MISSING' and info.get('required')]
        if missing_dirs:
            recs.append(f"Create required directories: {', '.join(missing_dirs)}")
        
        # Security recommendations
        security_issues = [check for check in self.results.get('security', {}).get('checks', [])
                          if check.get('status') == 'WARN']
        if security_issues:
            recs.append("Review and fix security warnings in the detailed report")
        
        self.results['recommendations'] = recs

def main():
    """Run system health check"""
    try:
        checker = SystemHealthChecker()
        results = checker.run_comprehensive_check()
        
        # Exit with appropriate code
        high_issues = len([i for i in results['issues'] if i['severity'] == 'HIGH'])
        sys.exit(1 if high_issues > 0 else 0)
        
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        traceback.print_exc()
        sys.exit(2)

if __name__ == "__main__":
    main()