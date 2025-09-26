#!/usr/bin/env python3
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
