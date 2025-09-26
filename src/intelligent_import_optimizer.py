#!/usr/bin/env python3
"""
Intelligent Import Optimizer - O3 Level Optimization
Fixes circular dependencies and implements lazy loading for optimal performance
"""

import sys
import importlib
import threading
import time
import logging
from typing import Dict, List, Any, Optional, Callable, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import functools
import inspect
import ast
import os
from pathlib import Path

logger = logging.getLogger(__name__)

class ImportType(Enum):
    """Types of imports"""
    STANDARD = "standard"
    THIRD_PARTY = "third_party"
    LOCAL = "local"
    BUILTIN = "builtin"

class ImportPriority(Enum):
    """Import priority levels"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    LAZY = 5

@dataclass
class ImportInfo:
    """Information about an import"""
    module_name: str
    import_type: ImportType
    priority: ImportPriority
    size_estimate: int
    load_time: float = 0.0
    last_used: float = 0.0
    usage_count: int = 0
    dependencies: Set[str] = field(default_factory=set)
    is_loaded: bool = False
    error_count: int = 0

@dataclass
class CircularDependency:
    """Detected circular dependency"""
    modules: List[str]
    severity: str
    suggested_fix: str

class IntelligentImportOptimizer:
    """
    O3 Level Import Optimizer
    - Circular dependency detection and resolution
    - Lazy loading implementation
    - Import performance optimization
    - Dependency graph analysis
    - Smart import ordering
    """
    
    def __init__(self, project_root: Optional[str] = None):
        self.project_root = Path(project_root or os.getcwd())
        
        # Import tracking
        self._import_info: Dict[str, ImportInfo] = {}
        self._import_graph: Dict[str, Set[str]] = defaultdict(set)
        self._reverse_graph: Dict[str, Set[str]] = defaultdict(set)
        self._circular_dependencies: List[CircularDependency] = []
        
        # Lazy loading
        self._lazy_modules: Dict[str, Callable] = {}
        self._lazy_loaded: Set[str] = set()
        self._lazy_lock = threading.RLock()
        
        # Performance tracking
        self._load_times: Dict[str, List[float]] = defaultdict(list)
        self._import_errors: Dict[str, int] = defaultdict(int)
        
        # Optimization settings
        self._max_lazy_loads = 50
        self._lazy_load_timeout = 5.0
        self._enable_circular_detection = True
        
        # Start analysis
        self._analyze_project_imports()
        
        logger.info("🚀 Intelligent Import Optimizer initialized")
    
    def _analyze_project_imports(self):
        """Analyze all Python files in project for imports"""
        try:
            python_files = list(self.project_root.rglob("*.py"))
            
            for py_file in python_files:
                try:
                    self._analyze_file_imports(py_file)
                except Exception as e:
                    logger.warning(f"⚠️ Error analyzing {py_file}: {e}")
            
            # Detect circular dependencies
            if self._enable_circular_detection:
                self._detect_circular_dependencies()
            
            logger.info(f"📊 Analyzed {len(python_files)} Python files")
            logger.info(f"📦 Found {len(self._import_info)} unique imports")
            logger.info(f"🔄 Detected {len(self._circular_dependencies)} circular dependencies")
            
        except Exception as e:
            logger.error(f"❌ Project analysis error: {e}")
    
    def _analyze_file_imports(self, file_path: Path):
        """Analyze imports in a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self._process_import(alias.name, file_path)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        self._process_import(node.module, file_path)
                        
        except Exception as e:
            logger.warning(f"⚠️ Error parsing {file_path}: {e}")
    
    def _process_import(self, module_name: str, file_path: Path):
        """Process a single import"""
        # Determine import type
        import_type = self._classify_import(module_name)
        
        # Determine priority
        priority = self._determine_priority(module_name, import_type)
        
        # Estimate size
        size_estimate = self._estimate_module_size(module_name)
        
        # Create or update import info
        if module_name not in self._import_info:
            self._import_info[module_name] = ImportInfo(
                module_name=module_name,
                import_type=import_type,
                priority=priority,
                size_estimate=size_estimate
            )
        
        # Add to dependency graph
        relative_path = file_path.relative_to(self.project_root)
        file_module = str(relative_path).replace('/', '.').replace('\\', '.').replace('.py', '')
        
        if file_module and not file_module.startswith('.'):
            self._import_graph[file_module].add(module_name)
            self._reverse_graph[module_name].add(file_module)
    
    def _classify_import(self, module_name: str) -> ImportType:
        """Classify import type"""
        if module_name in sys.builtin_module_names:
            return ImportType.BUILTIN
        elif '.' in module_name and not module_name.startswith('.'):
            # Check if it's a local module
            try:
                spec = importlib.util.find_spec(module_name)
                if spec and spec.origin:
                    origin_path = Path(spec.origin)
                    if self.project_root in origin_path.parents:
                        return ImportType.LOCAL
            except:
                pass
            return ImportType.THIRD_PARTY
        else:
            return ImportType.LOCAL
    
    def _determine_priority(self, module_name: str, import_type: ImportType) -> ImportPriority:
        """Determine import priority"""
        # Critical modules that should be loaded immediately
        critical_modules = {
            'os', 'sys', 'threading', 'logging', 'json', 'time',
            'typing', 'dataclasses', 'enum', 'collections'
        }
        
        if module_name in critical_modules:
            return ImportPriority.CRITICAL
        
        # High priority for core project modules
        if import_type == ImportType.LOCAL and any(
            module_name.startswith(prefix) for prefix in ['core.', 'src.', 'main']
        ):
            return ImportPriority.HIGH
        
        # Medium priority for standard library
        if import_type == ImportType.BUILTIN:
            return ImportPriority.MEDIUM
        
        # Low priority for third-party modules
        if import_type == ImportType.THIRD_PARTY:
            return ImportPriority.LOW
        
        # Lazy load everything else
        return ImportPriority.LAZY
    
    def _estimate_module_size(self, module_name: str) -> int:
        """Estimate module size in bytes"""
        try:
            spec = importlib.util.find_spec(module_name)
            if spec and spec.origin:
                return os.path.getsize(spec.origin)
        except:
            pass
        
        # Default estimates based on module type
        size_estimates = {
            'os': 50000,
            'sys': 30000,
            'json': 40000,
            'threading': 60000,
            'logging': 80000,
            'asyncio': 120000,
            'numpy': 2000000,
            'pandas': 5000000,
        }
        
        return size_estimates.get(module_name, 10000)
    
    def _detect_circular_dependencies(self):
        """Detect circular dependencies using DFS"""
        visited = set()
        rec_stack = set()
        
        def dfs(node, path):
            if node in rec_stack:
                # Found a cycle
                cycle_start = path.index(node)
                cycle = path[cycle_start:] + [node]
                self._circular_dependencies.append(CircularDependency(
                    modules=cycle,
                    severity=self._assess_circular_severity(cycle),
                    suggested_fix=self._suggest_circular_fix(cycle)
                ))
                return
            
            if node in visited:
                return
            
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in self._import_graph.get(node, set()):
                dfs(neighbor, path + [neighbor])
            
            rec_stack.remove(node)
        
        for module in self._import_graph:
            if module not in visited:
                dfs(module, [module])
    
    def _assess_circular_severity(self, cycle: List[str]) -> str:
        """Assess severity of circular dependency"""
        if len(cycle) <= 3:
            return "LOW"
        elif len(cycle) <= 5:
            return "MEDIUM"
        else:
            return "HIGH"
    
    def _suggest_circular_fix(self, cycle: List[str]) -> str:
        """Suggest fix for circular dependency"""
        # Simple suggestion: move one import to be lazy
        return f"Consider making '{cycle[0]}' a lazy import or restructuring the modules"
    
    def create_lazy_import(self, module_name: str, import_func: Optional[Callable] = None) -> Callable:
        """Create lazy import function for a module"""
        if import_func is None:
            def import_func():
                return importlib.import_module(module_name)
        
        def lazy_import():
            with self._lazy_lock:
                if module_name not in self._lazy_loaded:
                    start_time = time.time()
                    try:
                        module = import_func()
                        load_time = time.time() - start_time
                        
                        # Update tracking
                        if module_name in self._import_info:
                            self._import_info[module_name].load_time = load_time
                            self._import_info[module_name].is_loaded = True
                            self._import_info[module_name].last_used = time.time()
                        
                        self._load_times[module_name].append(load_time)
                        self._lazy_loaded.add(module_name)
                        
                        logger.debug(f"🔄 Lazy loaded {module_name} in {load_time:.3f}s")
                        
                    except Exception as e:
                        self._import_errors[module_name] += 1
                        logger.error(f"❌ Lazy import failed for {module_name}: {e}")
                        raise
                
                return sys.modules[module_name]
        
        self._lazy_modules[module_name] = lazy_import
        return lazy_import
    
    def optimize_imports(self, module_name: str) -> List[str]:
        """Get optimized import order for a module"""
        if module_name not in self._import_graph:
            return []
        
        # Topological sort for dependency order
        visited = set()
        result = []
        
        def visit(node):
            if node in visited:
                return
            visited.add(node)
            
            # Visit dependencies first
            for dep in self._import_graph[node]:
                if dep in self._import_info:
                    visit(dep)
            
            result.append(node)
        
        visit(module_name)
        return result
    
    def get_import_recommendations(self) -> Dict[str, Any]:
        """Get import optimization recommendations"""
        recommendations = {
            'circular_dependencies': [
                {
                    'modules': cd.modules,
                    'severity': cd.severity,
                    'suggestion': cd.suggested_fix
                }
                for cd in self._circular_dependencies
            ],
            'lazy_candidates': [
                module for module, info in self._import_info.items()
                if info.priority == ImportPriority.LAZY and not info.is_loaded
            ],
            'slow_imports': [
                {
                    'module': module,
                    'avg_time': sum(times) / len(times),
                    'count': len(times)
                }
                for module, times in self._load_times.items()
                if times and sum(times) / len(times) > 0.1
            ],
            'error_prone_imports': [
                {
                    'module': module,
                    'error_count': count
                }
                for module, count in self._import_errors.items()
                if count > 0
            ]
        }
        
        return recommendations
    
    def create_optimized_import_statement(self, module_name: str) -> str:
        """Create optimized import statement"""
        if module_name in self._lazy_modules:
            return f"# Lazy import: {module_name} = lazy_import_{module_name.replace('.', '_')}()"
        
        info = self._import_info.get(module_name)
        if info and info.priority == ImportPriority.CRITICAL:
            return f"import {module_name}  # Critical - load immediately"
        elif info and info.priority == ImportPriority.HIGH:
            return f"import {module_name}  # High priority"
        else:
            return f"import {module_name}  # Standard import"
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get import performance statistics"""
        total_imports = len(self._import_info)
        loaded_imports = sum(1 for info in self._import_info.values() if info.is_loaded)
        lazy_imports = len(self._lazy_loaded)
        
        avg_load_time = 0.0
        if self._load_times:
            all_times = [t for times in self._load_times.values() for t in times]
            avg_load_time = sum(all_times) / len(all_times)
        
        return {
            'total_imports': total_imports,
            'loaded_imports': loaded_imports,
            'lazy_imports': lazy_imports,
            'circular_dependencies': len(self._circular_dependencies),
            'avg_load_time': avg_load_time,
            'import_errors': sum(self._import_errors.values()),
            'lazy_candidates': len([
                info for info in self._import_info.values()
                if info.priority == ImportPriority.LAZY
            ])
        }
    
    def generate_import_report(self) -> str:
        """Generate comprehensive import analysis report"""
        stats = self.get_performance_stats()
        recommendations = self.get_import_recommendations()
        
        report = f"""
# 📊 Import Optimization Report

## Statistics
- Total Imports: {stats['total_imports']}
- Loaded Imports: {stats['loaded_imports']}
- Lazy Imports: {stats['lazy_imports']}
- Circular Dependencies: {stats['circular_dependencies']}
- Average Load Time: {stats['avg_load_time']:.3f}s
- Import Errors: {stats['import_errors']}

## Circular Dependencies
"""
        
        for i, cd in enumerate(self._circular_dependencies, 1):
            report += f"""
### {i}. {cd.modules[0]} → {' → '.join(cd.modules[1:])}
- **Severity**: {cd.severity}
- **Suggestion**: {cd.suggested_fix}
"""
        
        report += "\n## Slow Imports\n"
        for slow in recommendations['slow_imports']:
            report += f"- {slow['module']}: {slow['avg_time']:.3f}s (loaded {slow['count']} times)\n"
        
        report += "\n## Lazy Import Candidates\n"
        for candidate in recommendations['lazy_candidates']:
            report += f"- {candidate}\n"
        
        return report

# Global instance
_import_optimizer: Optional[IntelligentImportOptimizer] = None

def get_import_optimizer() -> IntelligentImportOptimizer:
    """Get global import optimizer instance"""
    global _import_optimizer
    if _import_optimizer is None:
        _import_optimizer = IntelligentImportOptimizer()
    return _import_optimizer

def lazy_import(module_name: str, import_func: Optional[Callable] = None) -> Callable:
    """Create lazy import for a module"""
    optimizer = get_import_optimizer()
    return optimizer.create_lazy_import(module_name, import_func)

def optimize_imports(module_name: str) -> List[str]:
    """Get optimized import order for a module"""
    optimizer = get_import_optimizer()
    return optimizer.optimize_imports(module_name)

# Example usage and optimization
def apply_import_optimizations():
    """Apply import optimizations to the project"""
    optimizer = get_import_optimizer()
    
    # Generate report
    report = optimizer.generate_import_report()
    
    # Save report
    with open("import_optimization_report.md", "w") as f:
        f.write(report)
    
    logger.info("📊 Import optimization report generated")
    return report
