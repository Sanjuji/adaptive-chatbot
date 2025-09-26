#!/usr/bin/env python3
"""
Test script to verify that all critical dependencies are working correctly.
This excludes problematic audio dependencies (pyaudio, pygame) for now.
"""

def test_imports():
    """Test importing all main dependencies."""
    try:
        # Core dependencies
        import dotenv
        print("✓ python-dotenv imported successfully")
        
        import pydantic
        print("✓ pydantic imported successfully")
        
        import typer
        print("✓ typer imported successfully")
        
        import rich
        print("✓ rich imported successfully")
        
        import sqlalchemy
        print("✓ sqlalchemy imported successfully")
        
        # ML and NLP dependencies
        import nltk
        print("✓ nltk imported successfully")
        
        import sklearn
        print("✓ scikit-learn imported successfully")
        
        import numpy
        print("✓ numpy imported successfully")
        
        import pandas
        print("✓ pandas imported successfully")
        
        import sentence_transformers
        print("✓ sentence-transformers imported successfully")
        
        import faiss
        print("✓ faiss-cpu imported successfully")
        
        # Additional AI/ML dependencies
        import torch
        print("✓ torch imported successfully")
        
        import transformers
        print("✓ transformers imported successfully")
        
        import matplotlib
        print("✓ matplotlib imported successfully")
        
        from PIL import Image
        print("✓ Pillow imported successfully")
        
        # Text processing
        import langdetect
        print("✓ langdetect imported successfully")
        
        import textblob
        print("✓ textblob imported successfully")
        
        # Audio processing (test without pyaudio/pygame)
        import pyttsx3
        print("✓ pyttsx3 imported successfully")
        
        import gtts
        print("✓ gtts imported successfully")
        
        import edge_tts
        print("✓ edge-tts imported successfully")
        
        # Windows-specific
        import win32api
        print("✓ pywin32 imported successfully")
        
        import comtypes
        print("✓ comtypes imported successfully")
        
        # Web framework
        import fastapi
        print("✓ fastapi imported successfully")
        
        import uvicorn
        print("✓ uvicorn imported successfully")
        
        # Development tools
        import pytest
        print("✓ pytest imported successfully")
        
        import black
        print("✓ black imported successfully")
        
        print("\n🎉 All critical dependencies imported successfully!")
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    
    return True

def test_basic_functionality():
    """Test basic functionality of key libraries."""
    try:
        # Test numpy
        import numpy as np
        arr = np.array([1, 2, 3])
        print(f"✓ NumPy basic test: {arr.sum()}")
        
        # Test sklearn
        from sklearn.feature_extraction.text import TfidfVectorizer
        vectorizer = TfidfVectorizer()
        print("✓ Scikit-learn basic test passed")
        
        # Test torch
        import torch
        tensor = torch.tensor([1.0, 2.0, 3.0])
        print(f"✓ PyTorch basic test: {tensor.sum()}")
        
        # Test transformers
        from transformers import pipeline
        print("✓ Transformers basic test passed")
        
        # Test FAISS
        import faiss
        index = faiss.IndexFlatL2(4)
        print("✓ FAISS basic test passed")
        
        print("\n🎉 Basic functionality tests passed!")
        
    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("Testing dependency imports...")
    imports_ok = test_imports()
    
    if imports_ok:
        print("\nTesting basic functionality...")
        functionality_ok = test_basic_functionality()
        
        if functionality_ok:
            print("\n✅ All tests passed! Dependencies are working correctly.")
        else:
            print("\n⚠️  Some functionality tests failed, but imports are working.")
    else:
        print("\n❌ Import tests failed. Check your installation.")