#!/usr/bin/env python3
"""
Research Lightweight TTS Alternatives for Hindi on Windows 11
"""

import subprocess
import sys
import os

def check_pip_package(package_name):
    """Check if package is available on PyPI"""
    try:
        result = subprocess.run([
            sys.executable, "-c", f"import pkg_resources; pkg_resources.get_distribution('{package_name}')"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            return True, "Already installed"
        else:
            # Check if available for install
            result = subprocess.run([
                sys.executable, "-m", "pip", "show", package_name
            ], capture_output=True, text=True)
            return False, "Available for install" if "not found" not in result.stdout else "Not found"
    except Exception as e:
        return False, f"Error: {e}"

def research_lightweight_tts():
    """Research lightweight TTS options"""
    
    print("🔍 LIGHTWEIGHT TTS RESEARCH FOR HINDI")
    print("=" * 50)
    
    lightweight_options = [
        {
            "name": "eSpeak-NG Python",
            "package": "espeak",
            "description": "Lightweight multilingual TTS with Hindi support",
            "size": "~5MB",
            "quality": "Basic but clear",
            "hindi_support": "Yes - Devanagari",
            "pros": ["Very small size", "Fast", "Offline", "Hindi built-in"],
            "cons": ["Robotic voice", "Not neural TTS"]
        },
        {
            "name": "Windows Speech Platform Runtime",
            "package": None,
            "description": "Additional Windows voices (Hindi available)",
            "size": "~50MB per voice",
            "quality": "Good",
            "hindi_support": "Yes - with additional download",
            "pros": ["Native Windows", "Good quality", "Professional"],
            "cons": ["Need separate download", "Larger size"]
        },
        {
            "name": "Balabolka + Additional Voices",
            "package": None,
            "description": "Free TTS with SAPI voice support",
            "size": "~10MB + voices",
            "quality": "Good",
            "hindi_support": "With SAPI Hindi voices",
            "pros": ["Many options", "Good integration"],
            "cons": ["Separate application needed"]
        },
        {
            "name": "pyttsx3 with additional voices",
            "package": "pyttsx3",
            "description": "Current engine with more voice options",
            "size": "~1MB",
            "quality": "Good",
            "hindi_support": "With system voices",
            "pros": ["Already installed", "Easy to use"],
            "cons": ["Limited to system voices"]
        },
        {
            "name": "Flite (Festival Lite)",
            "package": "flite",
            "description": "Lightweight version of Festival TTS",
            "size": "~10MB", 
            "quality": "Basic",
            "hindi_support": "Limited",
            "pros": ["Very lightweight", "Fast"],
            "cons": ["Poor Hindi support"]
        }
    ]
    
    for option in lightweight_options:
        print(f"\\n📦 {option['name']}")
        print("-" * 30)
        print(f"📝 Description: {option['description']}")
        print(f"💾 Size: {option['size']}")
        print(f"🎵 Quality: {option['quality']}")
        print(f"🇮🇳 Hindi Support: {option['hindi_support']}")
        print(f"✅ Pros: {', '.join(option['pros'])}")
        print(f"❌ Cons: {', '.join(option['cons'])}")
        
        if option['package']:
            available, status = check_pip_package(option['package'])
            print(f"📦 Package Status: {status}")
    
    print(f"\\n🎯 TOP RECOMMENDATIONS:")
    print("=" * 30)
    print("1. 🥇 eSpeak-NG - Best lightweight option for Hindi")
    print("2. 🥈 Windows Speech Platform Hindi Voice - Professional quality")
    print("3. 🥉 Enhanced pyttsx3 setup - Improve current system")
    
    print(f"\\n💡 NEXT STEPS:")
    print("Let me test the most promising option: eSpeak-NG")

if __name__ == "__main__":
    research_lightweight_tts()