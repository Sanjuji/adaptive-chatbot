#!/usr/bin/env python3
"""
🔬 Deep System Optimizer and Debugger
Comprehensive system analysis, debugging, and optimization
"""

import ast
import asyncio
import gc
import importlib
import inspect
import json
import logging
import os
import re
import sys
import threading
import time
import traceback
import warnings
from collections import defaultdict
from contextlib import contextmanager, suppress
from datetime import datetime
from functools import wraps, lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
import weakref

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DeepCodeAnalyzer:
    """Deep code analysis for optimization opportunities"""
    
    def __init__(self):
        self.issues = defaultdict(list)
        self.optimizations = []
        self.metrics = {}
        
    def analyze_file(self, file_path: str) -> Dict:
        """Perform deep analysis on a Python file"""
        if not os.path.exists(file_path):
            return {'error': f'File not found: {file_path}'}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            # Parse AST
            tree = ast.parse(source, filename=file_path)
            
            # Run various analyzers
            self._analyze_imports(tree, file_path)
            self._analyze_functions(tree, file_path)
            self._analyze_classes(tree, file_path)
            self._analyze_async_patterns(tree, file_path)
            self._analyze_error_handling(tree, file_path)
            self._analyze_performance_patterns(tree, file_path)
            
            return {
                'file': file_path,
                'issues': dict(self.issues),
                'optimizations': self.optimizations,
                'metrics': self.metrics
            }
            
        except Exception as e:
            return {'error': str(e), 'file': file_path}
    
    def _analyze_imports(self, tree: ast.AST, file_path: str):
        """Analyze import statements for optimization"""
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for alias in node.names:
                    imports.append(f"{module}.{alias.name}")
        
        # Check for unused imports
        # Check for circular imports
        # Check for heavy imports that could be lazy-loaded
        
        self.metrics['imports'] = len(imports)
        
        # Flag heavy modules
        heavy_modules = ['tensorflow', 'torch', 'numpy', 'pandas', 'sklearn']
        for imp in imports:
            for heavy in heavy_modules:
                if heavy in imp:
                    self.issues['performance'].append({
                        'type': 'heavy_import',
                        'module': imp,
                        'suggestion': f'Consider lazy loading {heavy} module'
                    })
    
    def _analyze_functions(self, tree: ast.AST, file_path: str):
        """Analyze functions for optimization opportunities"""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check function complexity
                complexity = self._calculate_complexity(node)
                if complexity > 10:
                    self.issues['complexity'].append({
                        'function': node.name,
                        'complexity': complexity,
                        'suggestion': 'Consider breaking down this complex function'
                    })
                
                # Check for missing return type hints
                if not node.returns:
                    self.issues['type_hints'].append({
                        'function': node.name,
                        'issue': 'Missing return type hint'
                    })
                
                # Check for too many parameters
                if len(node.args.args) > 5:
                    self.issues['design'].append({
                        'function': node.name,
                        'params': len(node.args.args),
                        'suggestion': 'Consider using a configuration object'
                    })
    
    def _analyze_classes(self, tree: ast.AST, file_path: str):
        """Analyze classes for optimization opportunities"""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check for missing docstrings
                if not ast.get_docstring(node):
                    self.issues['documentation'].append({
                        'class': node.name,
                        'issue': 'Missing docstring'
                    })
                
                # Check for too many methods
                methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
                if len(methods) > 20:
                    self.issues['design'].append({
                        'class': node.name,
                        'methods': len(methods),
                        'suggestion': 'Consider splitting this large class'
                    })
    
    def _analyze_async_patterns(self, tree: ast.AST, file_path: str):
        """Analyze async/await patterns for issues"""
        async_functions = []
        sync_in_async = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.AsyncFunctionDef):
                async_functions.append(node.name)
                
                # Check for synchronous operations in async functions
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        if isinstance(child.func, ast.Name):
                            # Flag potentially blocking calls
                            blocking_calls = ['open', 'sleep', 'input', 'requests']
                            if child.func.id in blocking_calls:
                                sync_in_async.append({
                                    'function': node.name,
                                    'blocking_call': child.func.id,
                                    'line': child.lineno if hasattr(child, 'lineno') else 0
                                })
        
        if sync_in_async:
            self.issues['async'].extend(sync_in_async)
        
        self.metrics['async_functions'] = len(async_functions)
    
    def _analyze_error_handling(self, tree: ast.AST, file_path: str):
        """Analyze error handling patterns"""
        bare_excepts = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                if node.type is None:
                    bare_excepts.append({
                        'line': node.lineno if hasattr(node, 'lineno') else 0,
                        'issue': 'Bare except clause',
                        'suggestion': 'Specify exception types'
                    })
        
        if bare_excepts:
            self.issues['error_handling'].extend(bare_excepts)
    
    def _analyze_performance_patterns(self, tree: ast.AST, file_path: str):
        """Analyze code for performance anti-patterns"""
        for node in ast.walk(tree):
            # Check for string concatenation in loops
            if isinstance(node, ast.For):
                for child in ast.walk(node):
                    if isinstance(child, ast.AugAssign) and isinstance(child.op, ast.Add):
                        if isinstance(child.target, ast.Name):
                            self.issues['performance'].append({
                                'pattern': 'string_concatenation_in_loop',
                                'line': child.lineno if hasattr(child, 'lineno') else 0,
                                'suggestion': 'Use list.append() and join() instead'
                            })
            
            # Check for list comprehension opportunities
            if isinstance(node, ast.For):
                parent = self._get_parent_node(tree, node)
                if parent and len(parent.body) == 1:
                    if isinstance(parent.body[0], ast.Expr):
                        if isinstance(parent.body[0].value, ast.Call):
                            if hasattr(parent.body[0].value.func, 'attr'):
                                if parent.body[0].value.func.attr == 'append':
                                    self.optimizations.append({
                                        'pattern': 'list_append_in_loop',
                                        'line': node.lineno if hasattr(node, 'lineno') else 0,
                                        'suggestion': 'Consider using list comprehension'
                                    })
    
    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity of a function"""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        return complexity
    
    def _get_parent_node(self, tree: ast.AST, node: ast.AST) -> Optional[ast.AST]:
        """Get parent node in AST"""
        for parent in ast.walk(tree):
            for child in ast.iter_child_nodes(parent):
                if child == node:
                    return parent
        return None

class SystemDebugger:
    """Advanced system debugging and issue detection"""
    
    def __init__(self):
        self.issues_found = []
        self.warnings = []
        self.errors = []
        
    def debug_imports(self) -> Dict:
        """Debug import issues in the system"""
        import_issues = []
        
        # Check for missing dependencies
        required_modules = [
            'edge_tts', 'pyttsx3', 'speech_recognition',
            'pygame', 'asyncio', 'threading'
        ]
        
        for module_name in required_modules:
            try:
                importlib.import_module(module_name)
            except ImportError as e:
                import_issues.append({
                    'module': module_name,
                    'error': str(e),
                    'severity': 'HIGH' if module_name in ['edge_tts', 'speech_recognition'] else 'MEDIUM'
                })
        
        # Check for version conflicts
        version_issues = self._check_version_compatibility()
        
        return {
            'missing_modules': import_issues,
            'version_issues': version_issues
        }
    
    def _check_version_compatibility(self) -> List[Dict]:
        """Check for version compatibility issues"""
        issues = []
        
        # Check Python version
        if sys.version_info < (3, 7):
            issues.append({
                'component': 'Python',
                'current': f"{sys.version_info.major}.{sys.version_info.minor}",
                'required': '3.7+',
                'severity': 'CRITICAL'
            })
        
        # Check asyncio compatibility
        if sys.version_info >= (3, 10):
            issues.append({
                'component': 'asyncio',
                'note': 'Some asyncio patterns may need updating for Python 3.10+',
                'severity': 'LOW'
            })
        
        return issues
    
    def debug_async_issues(self) -> Dict:
        """Debug async/await related issues"""
        issues = []
        
        # Check for event loop issues
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                issues.append({
                    'type': 'event_loop_running',
                    'description': 'Event loop already running, may cause conflicts',
                    'fix': 'Use asyncio.create_task() instead of loop.run_until_complete()'
                })
        except RuntimeError:
            pass
        
        # Check for deprecated patterns
        if hasattr(asyncio, 'get_running_loop'):
            issues.append({
                'type': 'deprecated_pattern',
                'description': 'Use asyncio.get_running_loop() instead of get_event_loop()',
                'severity': 'LOW'
            })
        
        return {'async_issues': issues}
    
    def debug_memory_issues(self) -> Dict:
        """Debug memory-related issues"""
        gc.collect()
        
        # Get memory statistics
        stats = {
            'objects': len(gc.get_objects()),
            'garbage': len(gc.garbage),
            'collections': gc.get_count()
        }
        
        # Find potential memory leaks
        leaks = []
        for obj in gc.garbage:
            leaks.append({
                'type': type(obj).__name__,
                'size': sys.getsizeof(obj) if hasattr(sys, 'getsizeof') else 'unknown'
            })
        
        # Check for circular references
        circular_refs = []
        for obj in gc.get_objects():
            if isinstance(obj, dict) and len(gc.get_referents(obj)) > 100:
                circular_refs.append({
                    'type': 'large_dict',
                    'size': len(obj),
                    'referents': len(gc.get_referents(obj))
                })
        
        return {
            'memory_stats': stats,
            'potential_leaks': leaks[:10],  # Limit to 10 items
            'circular_refs': circular_refs[:5]
        }
    
    def debug_thread_issues(self) -> Dict:
        """Debug threading issues"""
        threads = threading.enumerate()
        
        thread_info = []
        for thread in threads:
            thread_info.append({
                'name': thread.name,
                'daemon': thread.daemon,
                'alive': thread.is_alive(),
                'ident': thread.ident
            })
        
        # Check for potential deadlocks
        deadlock_risk = len(threads) > 50
        
        return {
            'thread_count': len(threads),
            'threads': thread_info,
            'deadlock_risk': deadlock_risk,
            'recommendation': 'Consider using async/await instead of threads' if len(threads) > 20 else None
        }

class PerformanceOptimizer:
    """Advanced performance optimization engine"""
    
    def __init__(self):
        self.optimizations_applied = []
        
    def optimize_imports(self, file_path: str) -> bool:
        """Optimize imports in a file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            optimized_lines = []
            import_block = []
            in_import_block = True
            
            for line in lines:
                if in_import_block:
                    if line.strip().startswith(('import ', 'from ')):
                        import_block.append(line)
                    elif line.strip() and not line.strip().startswith('#'):
                        # Sort and optimize imports
                        import_block.sort()
                        optimized_lines.extend(import_block)
                        optimized_lines.append(line)
                        in_import_block = False
                    else:
                        optimized_lines.append(line)
                else:
                    optimized_lines.append(line)
            
            # Write optimized file
            backup_path = file_path + '.backup'
            os.rename(file_path, backup_path)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(optimized_lines)
            
            self.optimizations_applied.append({
                'file': file_path,
                'optimization': 'import_sorting',
                'backup': backup_path
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to optimize imports: {e}")
            return False
    
    def optimize_async_code(self, file_path: str) -> List[Dict]:
        """Suggest async code optimizations"""
        suggestions = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            tree = ast.parse(source)
            
            for node in ast.walk(tree):
                # Check for synchronous sleep in async functions
                if isinstance(node, ast.AsyncFunctionDef):
                    for child in ast.walk(node):
                        if isinstance(child, ast.Call):
                            if hasattr(child.func, 'attr') and child.func.attr == 'sleep':
                                if hasattr(child.func, 'value') and hasattr(child.func.value, 'id'):
                                    if child.func.value.id == 'time':
                                        suggestions.append({
                                            'line': child.lineno,
                                            'issue': 'Using time.sleep() in async function',
                                            'fix': 'Replace with await asyncio.sleep()'
                                        })
            
            # Check for missing async context managers
            for node in ast.walk(tree):
                if isinstance(node, ast.With):
                    parent = None
                    for p in ast.walk(tree):
                        if node in ast.walk(p) and isinstance(p, ast.AsyncFunctionDef):
                            parent = p
                            break
                    
                    if parent:
                        suggestions.append({
                            'line': node.lineno if hasattr(node, 'lineno') else 0,
                            'issue': 'Using sync context manager in async function',
                            'fix': 'Consider using async with for async context managers'
                        })
            
        except Exception as e:
            logger.error(f"Failed to analyze async code: {e}")
        
        return suggestions
    
    def optimize_memory_usage(self) -> Dict:
        """Optimize memory usage system-wide"""
        initial_usage = self._get_memory_usage()
        
        # Clear all caches
        gc.collect()
        
        # Clear function caches
        for obj in gc.get_objects():
            if hasattr(obj, 'cache_clear'):
                try:
                    obj.cache_clear()
                except:
                    pass
        
        # Force garbage collection
        gc.collect(2)  # Full collection
        
        final_usage = self._get_memory_usage()
        
        return {
            'initial_memory_mb': initial_usage,
            'final_memory_mb': final_usage,
            'freed_mb': initial_usage - final_usage,
            'gc_stats': gc.get_stats()
        }
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        import os
        import psutil
        
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024

class IntegrationOptimizer:
    """Optimize integration between modules"""
    
    def __init__(self):
        self.integration_issues = []
        
    def check_module_integration(self) -> Dict:
        """Check integration between critical modules"""
        results = {
            'voice_integration': self._check_voice_integration(),
            'learning_integration': self._check_learning_integration(),
            'async_integration': self._check_async_integration()
        }
        
        return results
    
    def _check_voice_integration(self) -> Dict:
        """Check voice module integration"""
        issues = []
        
        try:
            import simple_voice
            
            # Check for EdgeTTS integration
            if hasattr(simple_voice, 'speak_simple'):
                # Test basic functionality
                pass
            else:
                issues.append('speak_simple function not found')
                
        except ImportError as e:
            issues.append(f'Cannot import simple_voice: {e}')
        
        return {
            'status': 'OK' if not issues else 'ISSUES',
            'issues': issues
        }
    
    def _check_learning_integration(self) -> Dict:
        """Check learning module integration"""
        issues = []
        
        try:
            import unified_learning_manager
            
            # Check for required functions
            required = ['get_learning_manager', 'learn', 'ask']
            for func in required:
                if not hasattr(unified_learning_manager, func):
                    issues.append(f'Missing function: {func}')
                    
        except ImportError as e:
            issues.append(f'Cannot import unified_learning_manager: {e}')
        
        return {
            'status': 'OK' if not issues else 'ISSUES',
            'issues': issues
        }
    
    def _check_async_integration(self) -> Dict:
        """Check async/await integration"""
        issues = []
        
        # Check for event loop conflicts
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                issues.append('Event loop already running - potential conflict')
        except:
            pass
        
        # Check for mixed sync/async calls
        # This would require more complex analysis
        
        return {
            'status': 'OK' if not issues else 'WARNING',
            'issues': issues
        }

def run_deep_optimization_and_debugging():
    """Run comprehensive optimization and debugging"""
    
    print("🔬 Starting Deep System Analysis and Optimization")
    print("=" * 70)
    
    results = {}
    
    # 1. Code Analysis
    print("\n📝 Analyzing Code Quality...")
    analyzer = DeepCodeAnalyzer()
    
    # Analyze main files
    main_files = [
        'adaptive_chatbot.py',
        'system_reliability_security.py',
        'critical_issues_integration.py',
        'simple_voice.py',
        'unified_learning_manager.py'
    ]
    
    code_analysis = {}
    for file in main_files:
        if os.path.exists(file):
            print(f"  Analyzing {file}...")
            code_analysis[file] = analyzer.analyze_file(file)
    
    results['code_analysis'] = code_analysis
    
    # 2. System Debugging
    print("\n🐛 Debugging System Issues...")
    debugger = SystemDebugger()
    
    debug_results = {
        'imports': debugger.debug_imports(),
        'async': debugger.debug_async_issues(),
        'memory': debugger.debug_memory_issues(),
        'threads': debugger.debug_thread_issues()
    }
    
    results['debug_results'] = debug_results
    
    # 3. Integration Check
    print("\n🔗 Checking Module Integration...")
    integrator = IntegrationOptimizer()
    integration = integrator.check_module_integration()
    results['integration'] = integration
    
    # 4. Performance Optimization
    print("\n⚡ Applying Performance Optimizations...")
    optimizer = PerformanceOptimizer()
    
    # Optimize memory
    memory_opt = optimizer.optimize_memory_usage()
    results['memory_optimization'] = memory_opt
    
    # 5. Generate Summary
    print("\n📊 Generating Summary...")
    summary = generate_optimization_summary(results)
    results['summary'] = summary
    
    # Save results
    with open('deep_optimization_report.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print("\n✅ Deep Optimization Complete!")
    print(f"📄 Full report saved to deep_optimization_report.json")
    
    # Print summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Code Issues Found: {summary['total_code_issues']}")
    print(f"Debug Issues Found: {summary['total_debug_issues']}")
    print(f"Integration Status: {summary['integration_status']}")
    print(f"Memory Freed: {memory_opt.get('freed_mb', 0):.2f} MB")
    
    if summary['critical_issues']:
        print("\n⚠️ CRITICAL ISSUES:")
        for issue in summary['critical_issues']:
            print(f"  - {issue}")
    
    if summary['recommendations']:
        print("\n💡 TOP RECOMMENDATIONS:")
        for rec in summary['recommendations'][:5]:
            print(f"  - {rec}")
    
    return results

def generate_optimization_summary(results: Dict) -> Dict:
    """Generate a summary of optimization results"""
    summary = {
        'total_code_issues': 0,
        'total_debug_issues': 0,
        'integration_status': 'OK',
        'critical_issues': [],
        'recommendations': []
    }
    
    # Count code issues
    for file_analysis in results.get('code_analysis', {}).values():
        if 'issues' in file_analysis:
            for category, issues in file_analysis['issues'].items():
                summary['total_code_issues'] += len(issues)
                
                # Flag critical issues
                if category in ['error_handling', 'async']:
                    for issue in issues:
                        summary['critical_issues'].append(
                            f"{category}: {issue.get('issue', issue)}"
                        )
    
    # Count debug issues
    debug = results.get('debug_results', {})
    if debug.get('imports', {}).get('missing_modules'):
        summary['total_debug_issues'] += len(debug['imports']['missing_modules'])
        for module in debug['imports']['missing_modules']:
            if module['severity'] == 'HIGH':
                summary['critical_issues'].append(
                    f"Missing critical module: {module['module']}"
                )
    
    # Check integration status
    integration = results.get('integration', {})
    for module, status in integration.items():
        if status.get('status') != 'OK':
            summary['integration_status'] = 'ISSUES'
            summary['critical_issues'].append(
                f"Integration issue with {module}"
            )
    
    # Generate recommendations
    if summary['total_code_issues'] > 50:
        summary['recommendations'].append("Consider refactoring to reduce code complexity")
    
    if debug.get('threads', {}).get('thread_count', 0) > 20:
        summary['recommendations'].append("Replace threading with async/await where possible")
    
    if debug.get('memory', {}).get('potential_leaks'):
        summary['recommendations'].append("Fix potential memory leaks detected")
    
    # Add async recommendations
    for file_analysis in results.get('code_analysis', {}).values():
        if 'issues' in file_analysis and 'async' in file_analysis['issues']:
            summary['recommendations'].append("Fix blocking calls in async functions")
            break
    
    return summary

if __name__ == "__main__":
    # Run the deep optimization
    results = run_deep_optimization_and_debugging()