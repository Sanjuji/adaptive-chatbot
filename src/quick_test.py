from advanced_nlp import get_nlp_engine

nlp = get_nlp_engine()

# Test sentiment
result = nlp.analyze_sentiment("I love this product!")
print(f"Sentiment: {result['sentiment']} ({result['confidence']:.2f})")

# Test Hindi greeting
result2 = nlp.extract_intent("नमस्ते")
print(f"Hindi greeting intent: {result2['intent']} ({result2['confidence']:.2f})")

# Test Hindi appreciation  
result3 = nlp.extract_intent("धन्यवाद")
print(f"Hindi appreciation intent: {result3['intent']} ({result3['confidence']:.2f})")