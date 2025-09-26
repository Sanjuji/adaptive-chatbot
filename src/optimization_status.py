#!/usr/bin/env python3
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
