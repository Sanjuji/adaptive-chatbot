#!/usr/bin/env python3
"""
Comprehensive test script to verify ALL dependencies are working correctly.
This includes the previously problematic audio dependencies.
"""

def test_all_imports():
    """Test importing all dependencies."""
    dependencies = {
        # Core dependencies
        'python-dotenv': 'dotenv',
        'pydantic': 'pydantic',
        'typer': 'typer',
        'rich': 'rich',
        'sqlalchemy': 'sqlalchemy',
        
        # ML and NLP dependencies
        'nltk': 'nltk',
        'scikit-learn': 'sklearn',
        'numpy': 'numpy',
        'pandas': 'pandas',
        'sentence-transformers': 'sentence_transformers',
        'faiss-cpu': 'faiss',
        
        # Additional AI/ML dependencies
        'torch': 'torch',
        'transformers': 'transformers',
        'matplotlib': 'matplotlib',
        'Pillow': 'PIL',
        
        # Text processing
        'langdetect': 'langdetect',
        'textblob': 'textblob',
        
        # Audio processing (ALL working now!)
        'speechrecognition': 'speech_recognition',
        'pyttsx3': 'pyttsx3',
        'pyaudio': 'pyaudio',
        'gtts': 'gtts',
        'pygame': 'pygame',
        'edge-tts': 'edge_tts',
        
        # Windows-specific
        'pywin32': 'win32api',
        'comtypes': 'comtypes',
        
        # Web framework
        'fastapi': 'fastapi',
        'uvicorn': 'uvicorn',
        
        # Additional utilities
        'requests': 'requests',
        'colorama': 'colorama',
        'click': 'click',
        
        # Configuration
        'pyyaml': 'yaml',
        'python-dateutil': 'dateutil',
        
        # Development tools
        'pytest': 'pytest',
        'black': 'black',
        'flake8': 'flake8',
        'mypy': 'mypy',
        'pytest-asyncio': 'pytest_asyncio',
    }
    
    failed_imports = []
    successful_imports = []
    
    for package_name, import_name in dependencies.items():
        try:
            __import__(import_name)
            print(f"✓ {package_name} imported successfully")
            successful_imports.append(package_name)
        except ImportError as e:
            print(f"❌ {package_name} import failed: {e}")
            failed_imports.append((package_name, str(e)))
    
    print(f"\n📊 Import Summary:")
    print(f"✅ Successful: {len(successful_imports)}/{len(dependencies)}")
    print(f"❌ Failed: {len(failed_imports)}/{len(dependencies)}")
    
    if failed_imports:
        print("\n❌ Failed imports:")
        for package, error in failed_imports:
            print(f"  - {package}: {error}")
    
    return len(failed_imports) == 0

def test_comprehensive_functionality():
    """Test comprehensive functionality of key libraries."""
    try:
        print("\n🔧 Testing core functionality...")
        
        # Test numpy
        import numpy as np
        arr = np.array([1, 2, 3, 4, 5])
        print(f"✓ NumPy: Array sum = {arr.sum()}")
        
        # Test pandas
        import pandas as pd
        df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
        print(f"✓ Pandas: DataFrame shape = {df.shape}")
        
        # Test sklearn
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        vectorizer = TfidfVectorizer()
        texts = ["hello world", "world hello", "python programming"]
        vectors = vectorizer.fit_transform(texts)
        similarity = cosine_similarity(vectors[0], vectors[1])[0][0]
        print(f"✓ Scikit-learn: Text similarity = {similarity:.3f}")
        
        # Test torch
        import torch
        tensor = torch.tensor([1.0, 2.0, 3.0])
        result = torch.nn.functional.relu(tensor - 1.5)
        print(f"✓ PyTorch: ReLU result = {result.tolist()}")
        
        # Test transformers (lightweight test)
        from transformers import AutoTokenizer
        print("✓ Transformers: AutoTokenizer available")
        
        # Test FAISS
        import faiss
        import numpy as np
        d = 64  # dimension
        nb = 1000  # database size
        nq = 10   # nb of queries
        np.random.seed(1234)
        xb = np.random.random((nb, d)).astype('float32')
        xq = np.random.random((nq, d)).astype('float32')
        index = faiss.IndexFlatL2(d)
        index.add(xb)
        k = 4  # we want to see 4 nearest neighbors
        D, I = index.search(xq, k)
        print(f"✓ FAISS: Search completed, found {len(I)} results")
        
        # Test audio functionality
        print("\n🎵 Testing audio functionality...")
        
        # Test speech recognition
        import speech_recognition as sr
        r = sr.Recognizer()
        print("✓ SpeechRecognition: Recognizer created")
        
        # Test pyttsx3
        import pyttsx3
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        print(f"✓ pyttsx3: Found {len(voices)} voices")
        engine.stop()
        
        # Test pygame
        import pygame
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        print("✓ Pygame: Mixer initialized")
        pygame.mixer.quit()
        
        # Test pyaudio
        import pyaudio
        p = pyaudio.PyAudio()
        device_count = p.get_device_count()
        print(f"✓ PyAudio: Found {device_count} audio devices")
        p.terminate()
        
        # Test text processing
        print("\n📝 Testing text processing...")
        
        # Test langdetect
        from langdetect import detect
        lang = detect("Hello, this is a test sentence in English.")
        print(f"✓ langdetect: Detected language = {lang}")
        
        # Test textblob
        from textblob import TextBlob
        blob = TextBlob("The quick brown fox jumps over the lazy dog.")
        sentiment = blob.sentiment
        print(f"✓ TextBlob: Sentiment polarity = {sentiment.polarity:.3f}")
        
        # Test web framework
        print("\n🌐 Testing web framework...")
        
        from fastapi import FastAPI
        app = FastAPI()
        print("✓ FastAPI: App created")
        
        print("\n🎉 All functionality tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting comprehensive dependency testing...")
    print("=" * 60)
    
    imports_ok = test_all_imports()
    
    if imports_ok:
        functionality_ok = test_comprehensive_functionality()
        
        if functionality_ok:
            print("\n" + "=" * 60)
            print("🎉 ✅ ALL TESTS PASSED! 🎉")
            print("Your adaptive chatbot environment is fully ready!")
            print("=" * 60)
        else:
            print("\n" + "=" * 60)
            print("⚠️ Imports successful but some functionality tests failed.")
            print("Your environment is mostly ready but may need minor adjustments.")
            print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ Some import tests failed. Please install missing dependencies.")
        print("=" * 60)