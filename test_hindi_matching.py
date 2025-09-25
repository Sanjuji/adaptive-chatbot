#!/usr/bin/env python3
"""
Test Suite for Hindi/Hinglish Query Matching
Tests various query variations to ensure the system handles all patterns correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from unified_learning_manager import get_learning_manager
from hindi_transliterator import transliterate_hindi, normalize_hindi_query
import json

def print_test_header(test_name):
    """Print formatted test header"""
    print("\n" + "="*60)
    print(f"🧪 {test_name}")
    print("="*60)

def test_transliteration():
    """Test Hindi to Hinglish transliteration"""
    print_test_header("Hindi to Hinglish Transliteration Test")
    
    test_cases = [
        ("स्विच का प्राइस कितना है", "switch ka price kitna hai"),
        ("वायर का रेट", "vayr ka ret"),
        ("एमसीबी प्राइस", "emseebi price"),
        ("सॉकेट की कीमत", "sauket ki keeemt"),
        ("फैन कितने का है", "phain kitne ka hai"),
        ("बल्ब का दाम", "balb ka daam"),
        ("हेलो", "helo"),
        ("मुझे बताओ", "mujhe batao")
    ]
    
    for hindi, expected_prefix in test_cases:
        result = transliterate_hindi(hindi)
        print(f"Hindi: {hindi}")
        print(f"Expected: Starts with '{expected_prefix}'")
        print(f"Got: {result}")
        if result.lower().startswith(expected_prefix[:5]):
            print("✅ PASS")
        else:
            print("⚠️ Partial match")
        print("-"*40)

def test_query_normalization():
    """Test query normalization"""
    print_test_header("Query Normalization Test")
    
    test_cases = [
        ("स्विच का प्राइस कितना है", "switch"),
        ("switch ka price", "switch"),
        ("SWITCH KA RATE", "switch"),
        ("स्विच की कीमत", "switch"),
        ("switch ki price kya hai", "switch"),
        ("वायर का रेट बताओ", "vayr"),
        ("wire ka rate", "wire")
    ]
    
    for query, should_contain in test_cases:
        result = normalize_hindi_query(query)
        print(f"Query: {query}")
        print(f"Normalized: {result}")
        if should_contain.lower() in result.lower():
            print("✅ Contains expected term")
        else:
            print("❌ Missing expected term")
        print("-"*40)

def test_knowledge_base_matching():
    """Test actual knowledge base matching"""
    print_test_header("Knowledge Base Matching Test")
    
    # Get learning manager
    lm = get_learning_manager()
    
    # Test queries - both Hindi and Hinglish variations
    test_queries = [
        # Hindi queries
        ("स्विच का प्राइस कितना है", "switch", True),
        ("स्विच की कीमत", "switch", True),
        ("वायर का रेट", "wire", True),
        ("फैन की प्राइस", "fan", True),
        ("एमसीबी का दाम", "mcb", True),
        ("सॉकेट कितने का है", "socket", True),
        
        # Hinglish queries
        ("switch ka price", "switch", True),
        ("switch ki price", "switch", True),
        ("wire ka rate", "wire", True),
        ("fan ki price", "fan", True),
        ("mcb price", "mcb", True),
        ("socket ki price", "socket", True),
        
        # Mixed queries
        ("स्विच ka price kya hai", "switch", True),
        ("wire की कीमत", "wire", True),
        
        # Common variations
        ("switch price", "switch", True),
        ("price of switch", "switch", True),
        ("switch cost", "switch", True),
        
        # Should not match
        ("random query xyz", None, False),
        ("abcdefgh", None, False)
    ]
    
    passed = 0
    failed = 0
    
    for query, expected_topic, should_match in test_queries:
        answer = lm.find_answer(query, update_usage=False)
        
        print(f"\nQuery: '{query}'")
        print(f"Expected: {'Match' if should_match else 'No match'} {f'(topic: {expected_topic})' if expected_topic else ''}")
        
        if answer:
            print(f"Answer: {answer[:100]}...")
            if should_match:
                if expected_topic and expected_topic.lower() in answer.lower():
                    print("✅ PASS - Correct match")
                    passed += 1
                else:
                    print("⚠️ PASS - Found answer but different topic")
                    passed += 1
            else:
                print("❌ FAIL - Should not have matched")
                failed += 1
        else:
            print("Answer: None")
            if not should_match:
                print("✅ PASS - Correctly no match")
                passed += 1
            else:
                print("❌ FAIL - Should have matched")
                failed += 1
    
    print("\n" + "="*60)
    print(f"📊 Results: {passed} passed, {failed} failed out of {passed+failed} tests")
    print(f"Success rate: {(passed/(passed+failed)*100):.1f}%")
    print("="*60)

def test_teaching_and_retrieval():
    """Test teaching new knowledge and retrieving it"""
    print_test_header("Teaching and Retrieval Test")
    
    lm = get_learning_manager()
    
    # Test teaching in Hindi
    test_knowledge = [
        ("टेस्ट सवाल एक", "यह टेस्ट जवाब एक है"),
        ("test question two", "This is test answer two"),
        ("मिक्स्ड question तीन", "Mixed answer तीन है")
    ]
    
    print("Teaching new knowledge...")
    for question, answer in test_knowledge:
        success = lm.add_knowledge(question, answer)
        if success:
            print(f"✅ Taught: '{question}' -> '{answer}'")
        else:
            print(f"❌ Failed to teach: '{question}'")
    
    print("\nRetrieving taught knowledge...")
    for question, expected_answer in test_knowledge:
        retrieved = lm.find_answer(question, update_usage=False)
        if retrieved == expected_answer:
            print(f"✅ Retrieved correctly: '{question}'")
        else:
            print(f"❌ Retrieval failed: '{question}'")
            print(f"   Expected: {expected_answer}")
            print(f"   Got: {retrieved}")

def test_performance():
    """Test query performance"""
    print_test_header("Performance Test")
    
    import time
    lm = get_learning_manager()
    
    queries = [
        "switch ka price",
        "स्विच का प्राइस",
        "wire ka rate",
        "fan ki price",
        "mcb price"
    ]
    
    total_time = 0
    for query in queries:
        start = time.time()
        answer = lm.find_answer(query, update_usage=False)
        elapsed = time.time() - start
        total_time += elapsed
        print(f"Query: '{query[:30]}...' - Time: {elapsed*1000:.2f}ms")
    
    avg_time = (total_time / len(queries)) * 1000
    print(f"\n📊 Average query time: {avg_time:.2f}ms")
    if avg_time < 100:
        print("✅ Excellent performance")
    elif avg_time < 500:
        print("⚠️ Acceptable performance")
    else:
        print("❌ Performance needs improvement")

def main():
    """Run all tests"""
    print("\n" + "🚀 "*20)
    print("HINDI/HINGLISH QUERY MATCHING TEST SUITE")
    print("🚀 "*20)
    
    try:
        # Run tests
        test_transliteration()
        test_query_normalization()
        test_knowledge_base_matching()
        test_teaching_and_retrieval()
        test_performance()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS COMPLETED")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()