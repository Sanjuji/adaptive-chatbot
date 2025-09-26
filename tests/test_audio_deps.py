#!/usr/bin/env python3
"""
Test script to verify audio dependencies are working.
"""

def test_audio_imports():
    """Test importing audio dependencies."""
    try:
        import speech_recognition
        print("✓ speech_recognition imported successfully")
        
        import pyaudio
        print("✓ pyaudio imported successfully")
        
        import pygame
        print("✓ pygame imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Audio import failed: {e}")
        return False

def test_basic_audio_functionality():
    """Test basic audio functionality."""
    try:
        # Test speech recognition
        import speech_recognition as sr
        r = sr.Recognizer()
        print("✓ Speech recognition recognizer created")
        
        # Test pygame
        import pygame
        pygame.mixer.init()
        print("✓ Pygame mixer initialized")
        pygame.mixer.quit()
        
        # Test pyaudio
        import pyaudio
        p = pyaudio.PyAudio()
        device_count = p.get_device_count()
        print(f"✓ PyAudio initialized - found {device_count} audio devices")
        p.terminate()
        
        return True
        
    except Exception as e:
        print(f"❌ Audio functionality test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing audio dependency imports...")
    imports_ok = test_audio_imports()
    
    if imports_ok:
        print("\nTesting basic audio functionality...")
        functionality_ok = test_basic_audio_functionality()
        
        if functionality_ok:
            print("\n✅ All audio tests passed!")
        else:
            print("\n⚠️  Audio imports work but functionality tests failed.")
    else:
        print("\n❌ Audio import tests failed.")