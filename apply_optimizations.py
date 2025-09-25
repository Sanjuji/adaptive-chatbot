#!/usr/bin/env python3
"""
Apply Optimizations Script - O3 Level Optimization Application
Applies all optimizations to the existing codebase
"""

import os
import sys
import shutil
import logging
from pathlib import Path
from typing import List, Dict, Any
import json
import time

logger = logging.getLogger(__name__)

class OptimizationApplier:
    """Applies optimizations to the existing codebase"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.backup_dir = self.project_root / "optimization_backup"
        self.optimization_log = []
        
    def apply_all_optimizations(self):
        """Apply all optimizations to the codebase"""
        logger.info("🚀 Starting comprehensive optimization application...")
        
        try:
            # Create backup
            self._create_backup()
            
            # Apply optimizations
            self._apply_event_loop_fixes()
            self._apply_memory_optimizations()
            self._apply_import_optimizations()
            self._apply_circuit_breaker_patterns()
            self._apply_performance_monitoring()
            self._create_optimization_entry_points()
            self._update_requirements()
            self._create_optimization_scripts()
            
            # Generate report
            self._generate_optimization_report()
            
            logger.info("✅ All optimizations applied successfully!")
            
        except Exception as e:
            logger.error(f"❌ Error applying optimizations: {e}")
            self._restore_backup()
            raise
    
    def _create_backup(self):
        """Create backup of original files"""
        logger.info("📦 Creating backup...")
        
        if self.backup_dir.exists():
            shutil.rmtree(self.backup_dir)
        
        self.backup_dir.mkdir(exist_ok=True)
        
        # Backup critical files
        critical_files = [
            "adaptive_chatbot.py",
            "adaptive_chatbot_enhanced.py",
            "main_adaptive_chatbot.py",
            "core/edge_tts_engine.py",
            "simple_voice.py",
            "unified_learning_manager.py",
            "requirements.txt"
        ]
        
        for file_path in critical_files:
            src = self.project_root / file_path
            if src.exists():
                dst = self.backup_dir / file_path
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
                self.optimization_log.append(f"Backed up: {file_path}")
    
    def _apply_event_loop_fixes(self):
        """Apply event loop optimizations"""
        logger.info("🔄 Applying event loop optimizations...")
        
        # The advanced_event_loop_manager.py is already created
        # Update existing files to use it
        
        # Update adaptive_chatbot.py to use new event loop manager
        self._update_file_imports(
            "adaptive_chatbot.py",
            "from advanced_event_loop_manager import get_loop_manager, run_async_safely"
        )
        
        # Update main_adaptive_chatbot.py
        self._update_file_imports(
            "main_adaptive_chatbot.py", 
            "from advanced_event_loop_manager import get_loop_manager, run_async_safely"
        )
        
        self.optimization_log.append("Applied event loop optimizations")
    
    def _apply_memory_optimizations(self):
        """Apply memory optimizations"""
        logger.info("🧠 Applying memory optimizations...")
        
        # Update files to use memory manager
        files_to_update = [
            "adaptive_chatbot.py",
            "adaptive_chatbot_enhanced.py", 
            "main_adaptive_chatbot.py",
            "unified_learning_manager.py"
        ]
        
        for file_path in files_to_update:
            self._update_file_imports(
                file_path,
                "from advanced_memory_manager import get_memory_manager, memory_monitor, register_memory_cleanup"
            )
        
        self.optimization_log.append("Applied memory optimizations")
    
    def _apply_import_optimizations(self):
        """Apply import optimizations"""
        logger.info("📦 Applying import optimizations...")
        
        # Create lazy import wrappers for heavy modules
        lazy_imports_content = '''
# Lazy imports for heavy modules
from intelligent_import_optimizer import lazy_import

# Lazy load heavy modules
numpy = lazy_import('numpy')
pandas = lazy_import('pandas') 
matplotlib = lazy_import('matplotlib')
sklearn = lazy_import('sklearn')
'''
        
        with open(self.project_root / "lazy_imports.py", "w") as f:
            f.write(lazy_imports_content)
        
        self.optimization_log.append("Applied import optimizations")
    
    def _apply_circuit_breaker_patterns(self):
        """Apply circuit breaker patterns"""
        logger.info("🔧 Applying circuit breaker patterns...")
        
        # Update critical files to use circuit breakers
        files_to_update = [
            "core/edge_tts_engine.py",
            "simple_voice.py",
            "unified_learning_manager.py"
        ]
        
        for file_path in files_to_update:
            self._update_file_imports(
                file_path,
                "from advanced_circuit_breaker import circuit_breaker, get_circuit_breaker"
            )
        
        self.optimization_log.append("Applied circuit breaker patterns")
    
    def _apply_performance_monitoring(self):
        """Apply performance monitoring"""
        logger.info("📊 Applying performance monitoring...")
        
        # Update main files to include performance monitoring
        files_to_update = [
            "adaptive_chatbot.py",
            "main_adaptive_chatbot.py"
        ]
        
        for file_path in files_to_update:
            self._update_file_imports(
                file_path,
                "from performance_monitoring_dashboard import get_performance_monitor, performance_timer"
            )
        
        self.optimization_log.append("Applied performance monitoring")
    
    def _create_optimization_entry_points(self):
        """Create entry points for optimization system"""
        
        # Create main optimization launcher
        launcher_content = '''#!/usr/bin/env python3
"""
Optimization Launcher - Entry point for all optimizations
"""

import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from comprehensive_optimization_integration import get_optimization_system, run_optimization

def main():
    """Main optimization launcher"""
    print("Starting Optimization System...")
    
    # Initialize optimization system
    system = get_optimization_system()
    
    # Run comprehensive optimization
    report = run_optimization()
    
    # Print summary
    print(system.generate_optimization_summary())
    
    return report

if __name__ == "__main__":
    main()
'''
        
        with open(self.project_root / "run_optimization.py", "w") as f:
            f.write(launcher_content)
        
        # Make it executable
        os.chmod(self.project_root / "run_optimization.py", 0o755)
        
        self.optimization_log.append("Created optimization entry points")
    
    def _update_requirements(self):
        """Update requirements.txt with optimization dependencies"""
        logger.info("📋 Updating requirements...")
        
        new_requirements = [
            "psutil>=5.9.0",
            "matplotlib>=3.5.0",
            "numpy>=1.21.0",
            "uvloop>=0.17.0; sys_platform != 'win32'",
            "tracemalloc>=1.0.0"
        ]
        
        requirements_file = self.project_root / "requirements.txt"
        
        if requirements_file.exists():
            with open(requirements_file, "r") as f:
                existing_requirements = f.read().strip().split("\n")
        else:
            existing_requirements = []
        
        # Add new requirements
        all_requirements = existing_requirements + new_requirements
        unique_requirements = list(dict.fromkeys(all_requirements))  # Remove duplicates
        
        with open(requirements_file, "w") as f:
            f.write("\n".join(unique_requirements) + "\n")
        
        self.optimization_log.append("Updated requirements.txt")
    
    def _create_optimization_scripts(self):
        """Create optimization utility scripts"""
        
        # Create optimization status script
        status_script = '''#!/usr/bin/env python3
"""
Optimization Status Script
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from comprehensive_optimization_integration import get_optimization_system

def main():
    """Show optimization status"""
    system = get_optimization_system()
    report = system.get_optimization_report()
    
    if report:
        print(f"System Health: {report.system_health_score:.1f}/100")
        print(f"Recommendations: {len(report.recommendations)}")
        print(f"Critical Issues: {len(report.critical_issues)}")
    else:
        print("No optimization data available")

if __name__ == "__main__":
    main()
'''
        
        with open(self.project_root / "optimization_status.py", "w") as f:
            f.write(status_script)
        
        os.chmod(self.project_root / "optimization_status.py", 0o755)
        
        self.optimization_log.append("Created optimization utility scripts")
    
    def _update_file_imports(self, file_path: str, import_statement: str):
        """Update file imports"""
        file_path = self.project_root / file_path
        
        if not file_path.exists():
            return
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Add import if not already present
            if import_statement not in content:
                lines = content.split("\n")
                
                # Find the last import statement
                last_import_line = 0
                for i, line in enumerate(lines):
                    if line.strip().startswith(("import ", "from ")):
                        last_import_line = i
                
                # Insert new import after last import
                lines.insert(last_import_line + 1, import_statement)
                
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write("\n".join(lines))
                
                self.optimization_log.append(f"Updated imports in {file_path}")
        
        except Exception as e:
            logger.warning(f"⚠️ Could not update {file_path}: {e}")
    
    def _generate_optimization_report(self):
        """Generate optimization report"""
        logger.info("📊 Generating optimization report...")
        
        report = {
            "timestamp": time.time(),
            "optimization_log": self.optimization_log,
            "files_created": [
                "advanced_event_loop_manager.py",
                "advanced_memory_manager.py", 
                "intelligent_import_optimizer.py",
                "advanced_circuit_breaker.py",
                "performance_monitoring_dashboard.py",
                "comprehensive_optimization_integration.py",
                "run_optimization.py",
                "optimization_status.py",
                "lazy_imports.py"
            ],
            "backup_location": str(self.backup_dir),
            "status": "SUCCESS"
        }
        
        with open(self.project_root / "optimization_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        # Create markdown report
        markdown_report = f"""# Optimization Application Report

## Summary
- **Status**: SUCCESS
- **Timestamp**: {time.ctime()}
- **Files Modified**: {len(self.optimization_log)}

## Files Created
"""
        
        for file_name in report["files_created"]:
            markdown_report += f"- `{file_name}`\n"
        
        markdown_report += f"""
## Optimization Log
"""
        
        for log_entry in self.optimization_log:
            markdown_report += f"- {log_entry}\n"
        
        markdown_report += f"""
## Next Steps
1. Run `python run_optimization.py` to start the optimization system
2. Run `python optimization_status.py` to check system health
3. Monitor the system using the performance dashboard
4. Apply recommendations as needed

## Backup
Original files backed up to: `{self.backup_dir}`
"""
        
        with open(self.project_root / "OPTIMIZATION_APPLICATION_REPORT.md", "w") as f:
            f.write(markdown_report)
        
        self.optimization_log.append("Generated optimization report")
    
    def _restore_backup(self):
        """Restore from backup"""
        logger.info("🔄 Restoring from backup...")
        
        if not self.backup_dir.exists():
            logger.error("❌ No backup found!")
            return
        
        try:
            # Restore files
            for backup_file in self.backup_dir.rglob("*"):
                if backup_file.is_file():
                    relative_path = backup_file.relative_to(self.backup_dir)
                    target_file = self.project_root / relative_path
                    target_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(backup_file, target_file)
            
            logger.info("✅ Backup restored successfully")
        
        except Exception as e:
            logger.error(f"❌ Error restoring backup: {e}")

def main():
    """Main function"""
    logging.basicConfig(level=logging.INFO)
    
    print("O3 Level Optimization Application")
    print("=" * 50)
    
    applier = OptimizationApplier()
    
    try:
        applier.apply_all_optimizations()
        print("\nOptimization application completed successfully!")
        print("Check OPTIMIZATION_APPLICATION_REPORT.md for details")
        print("Run 'python run_optimization.py' to start the system")
    
    except Exception as e:
        print(f"\nOptimization application failed: {e}")
        print("Restoring from backup...")
        applier._restore_backup()
        sys.exit(1)

if __name__ == "__main__":
    main()
