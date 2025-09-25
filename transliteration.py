#!/usr/bin/env python3
"""
Transliteration utility for converting Devanagari to Hinglish
Converts Hindi text in Devanagari script to Roman/Latin script (Hinglish)
"""

def devanagari_to_hinglish(text: str) -> str:
    """
    Convert Devanagari text to Hinglish (Roman script)
    """
    if not text:
        return text
    
    # Devanagari to Roman mapping
    devanagari_map = {
        # Vowels
        'अ': 'a', 'आ': 'aa', 'इ': 'i', 'ई': 'ee', 'उ': 'u', 'ऊ': 'oo',
        'ऋ': 'ri', 'ए': 'e', 'ऐ': 'ai', 'ओ': 'o', 'औ': 'au',
        
        # Consonants
        'क': 'k', 'ख': 'kh', 'ग': 'g', 'घ': 'gh', 'ङ': 'ng',
        'च': 'ch', 'छ': 'chh', 'ज': 'j', 'झ': 'jh', 'ञ': 'ny',
        'ट': 't', 'ठ': 'th', 'ड': 'd', 'ढ': 'dh', 'ण': 'n',
        'त': 't', 'थ': 'th', 'द': 'd', 'ध': 'dh', 'न': 'n',
        'प': 'p', 'फ': 'ph', 'ब': 'b', 'भ': 'bh', 'म': 'm',
        'य': 'y', 'र': 'r', 'ल': 'l', 'व': 'v',
        'श': 'sh', 'ष': 'sh', 'स': 's', 'ह': 'h',
        
        # Additional consonants
        'क्ष': 'ksh', 'त्र': 'tr', 'ज्ञ': 'gya',
        
        # Vowel signs (matras)
        'ा': 'aa', 'ि': 'i', 'ी': 'ee', 'ु': 'u', 'ू': 'oo',
        'ृ': 'ri', 'े': 'e', 'ै': 'ai', 'ो': 'o', 'ौ': 'au',
        
        # Halant and other marks
        '्': '', 'ं': 'n', 'ः': 'h', 'ँ': 'n',
        
        # Numbers
        '०': '0', '१': '1', '२': '2', '३': '3', '४': '4',
        '५': '5', '६': '6', '७': '7', '८': '8', '९': '9',
        
        # Common punctuation
        '।': '.', '॥': '||'
    }
    
    # Convert character by character
    result = []
    i = 0
    
    while i < len(text):
        # Check for two-character combinations first
        if i < len(text) - 1:
            two_char = text[i:i+2]
            if two_char in devanagari_map:
                result.append(devanagari_map[two_char])
                i += 2
                continue
        
        # Check single character
        char = text[i]
        if char in devanagari_map:
            result.append(devanagari_map[char])
        elif char.isascii():
            # Keep English characters as is
            result.append(char)
        else:
            # For unmapped Devanagari characters, try basic transliteration
            result.append(char)
        
        i += 1
    
    # Join and clean up the result
    hinglish_text = ''.join(result)
    
    # Post-processing cleanup
    hinglish_text = _cleanup_transliteration(hinglish_text)
    
    return hinglish_text

def _cleanup_transliteration(text: str) -> str:
    """Clean up transliterated text"""
    # Remove excessive 'a' sounds that are implicit in Devanagari
    text = text.replace('aa', 'aa')  # Keep explicit long 'aa'
    
    # Fix common patterns
    replacements = [
        ('kaa', 'ka'),
        ('gaa', 'ga'),
        ('jaa', 'ja'),
        ('taa', 'ta'),
        ('daa', 'da'),
        ('naa', 'na'),
        ('paa', 'pa'),
        ('baa', 'ba'),
        ('maa', 'ma'),
        ('yaa', 'ya'),
        ('raa', 'ra'),
        ('laa', 'la'),
        ('vaa', 'va'),
        ('saa', 'sa'),
        ('haa', 'ha'),
    ]
    
    # Apply replacements at word boundaries
    for original, replacement in replacements:
        # Only replace at the end of words or before consonants
        import re
        text = re.sub(f'{original}(?=\\s|$|[bcdfghjklmnpqrstvwxyz])', replacement, text)
    
    # Clean up multiple spaces
    text = ' '.join(text.split())
    
    return text

def has_devanagari(text: str) -> bool:
    """Check if text contains Devanagari characters"""
    if not text:
        return False
    
    # Devanagari Unicode range: U+0900 to U+097F
    for char in text:
        if '\u0900' <= char <= '\u097F':
            return True
    
    return False

def smart_transliterate(text: str) -> str:
    """
    Smart transliteration that only converts Devanagari parts
    and keeps English parts intact
    """
    if not text or not has_devanagari(text):
        return text
    
    return devanagari_to_hinglish(text)

# Common Hindi words and their Hinglish equivalents for better accuracy
COMMON_WORDS = {
    'नमस्ते': 'namaste',
    'धन्यवाद': 'dhanyawad', 
    'अलविदा': 'alvida',
    'कैसे': 'kaise',
    'क्या': 'kya',
    'कहाँ': 'kahan',
    'कब': 'kab',
    'कौन': 'kaun',
    'क्यों': 'kyun',
    'कितना': 'kitna',
    'अच्छा': 'accha',
    'बुरा': 'bura',
    'बड़ा': 'bada',
    'छोटा': 'chota',
    'नया': 'naya',
    'पुराना': 'purana',
    'सुंदर': 'sundar',
    'अभी': 'abhi',
    'फिर': 'phir',
    'वहाँ': 'wahan',
    'यहाँ': 'yahan',
    'घर': 'ghar',
    'काम': 'kaam',
    'समय': 'samay',
    'पानी': 'paani',
    'खाना': 'khana',
    'स्कूल': 'school',
    'अस्पताल': 'aspatal',
    'बाज़ार': 'bazaar',
    'दोस्त': 'dost',
    'परिवार': 'parivar',
    'मदद': 'madad',
    'समस्या': 'samasya',
    'खुश': 'khush',
    'दुखी': 'dukhi',
    'प्यार': 'pyaar'
}

def enhanced_transliterate(text: str) -> str:
    """Enhanced transliteration using common word mappings"""
    if not text or not has_devanagari(text):
        return text
    
    # First, try to match common words
    words = text.split()
    transliterated_words = []
    
    for word in words:
        # Remove punctuation for matching
        clean_word = word.strip('.,!?;:"()[]{}')
        
        if clean_word in COMMON_WORDS:
            # Replace with common word mapping
            punct = word[len(clean_word):]  # Get trailing punctuation
            transliterated_words.append(COMMON_WORDS[clean_word] + punct)
        else:
            # Use character-by-character transliteration
            transliterated_words.append(devanagari_to_hinglish(word))
    
    return ' '.join(transliterated_words)

def main():
    """Test the transliteration functions"""
    test_texts = [
        "नमस्ते! कैसे हैं आप?",
        "मैं ठीक हूँ, धन्यवाद।",
        "आप का नाम क्या है?",
        "मुझे मदद चाहिए।",
        "यह बहुत अच्छा है।"
    ]
    
    print("Devanagari to Hinglish Transliteration Test:")
    print("=" * 50)
    
    for text in test_texts:
        hinglish = enhanced_transliterate(text)
        print(f"Original:  {text}")
        print(f"Hinglish:  {hinglish}")
        print()

if __name__ == "__main__":
    main()