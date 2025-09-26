#!/usr/bin/env python3
"""
Hindi to Hinglish Transliteration Module
Converts Devanagari script to Latin script for better query matching
"""

import re
from typing import Dict, List, Optional

class HindiTransliterator:
    """Transliterate Hindi (Devanagari) text to Hinglish (Latin script)"""
    
    def __init__(self):
        # Comprehensive Hindi to Hinglish mapping
        self.mapping = {
            # Vowels
            'अ': 'a', 'आ': 'aa', 'इ': 'i', 'ई': 'ee', 'उ': 'u', 'ऊ': 'oo',
            'ए': 'e', 'ऐ': 'ai', 'ओ': 'o', 'औ': 'au', 'ऋ': 'ri',
            
            # Consonants
            'क': 'k', 'ख': 'kh', 'ग': 'g', 'घ': 'gh', 'ङ': 'ng',
            'च': 'ch', 'छ': 'chh', 'ज': 'j', 'झ': 'jh', 'ञ': 'ny',
            'ट': 't', 'ठ': 'th', 'ड': 'd', 'ढ': 'dh', 'ण': 'n',
            'त': 't', 'थ': 'th', 'द': 'd', 'ध': 'dh', 'न': 'n',
            'प': 'p', 'फ': 'ph', 'ब': 'b', 'भ': 'bh', 'म': 'm',
            'य': 'y', 'र': 'r', 'ल': 'l', 'व': 'v', 'व़': 'w',
            'श': 'sh', 'ष': 'sh', 'स': 's', 'ह': 'h',
            'क्ष': 'ksh', 'त्र': 'tr', 'ज्ञ': 'gy',
            
            # Matras (vowel signs)
            'ा': 'a', 'ि': 'i', 'ी': 'ee', 'ु': 'u', 'ू': 'oo',
            'े': 'e', 'ै': 'ai', 'ो': 'o', 'ौ': 'au',
            'ं': 'n', 'ः': 'h', 'ँ': 'n',
            '्': '',  # Halant (suppresses inherent vowel)
            
            # Numbers
            '०': '0', '१': '1', '२': '2', '३': '3', '४': '4',
            '५': '5', '६': '6', '७': '7', '८': '8', '९': '9',
            
            # Common words (special cases)
            'है': 'hai', 'हैं': 'hain', 'था': 'tha', 'थे': 'the',
            'को': 'ko', 'का': 'ka', 'की': 'ki', 'के': 'ke',
            'में': 'mein', 'से': 'se', 'पर': 'par', 'या': 'ya',
            'और': 'aur', 'तो': 'to', 'ने': 'ne', 'यह': 'yah',
            'वह': 'vah', 'जो': 'jo', 'कि': 'ki', 'जब': 'jab',
            
            # Common electronics terms
            'स्विच': 'switch', 'वायर': 'wire', 'सॉकेट': 'socket',
            'बल्ब': 'bulb', 'फैन': 'fan', 'बैटरी': 'battery',
            'इनवर्टर': 'inverter', 'केबल': 'cable', 'प्राइस': 'price',
            'रेट': 'rate', 'कितना': 'kitna', 'कितने': 'kitne',
            'रुपये': 'rupees', 'पैसे': 'paise'
        }
        
        # Create regex pattern for multi-char sequences (sort by length for correct matching)
        multi_char = {k: v for k, v in self.mapping.items() if len(k) > 1}
        self.multi_pattern = '|'.join(sorted(multi_char.keys(), key=len, reverse=True))
        
    def transliterate(self, text: str) -> str:
        """Convert Hindi text to Hinglish"""
        if not text:
            return ""
        
        result = text
        
        # First, replace multi-character sequences
        if self.multi_pattern:
            result = re.sub(
                self.multi_pattern,
                lambda m: self.mapping[m.group()],
                result
            )
        
        # Then replace single characters
        for hindi, english in self.mapping.items():
            if len(hindi) == 1:
                result = result.replace(hindi, english)
        
        # Clean up multiple spaces
        result = ' '.join(result.split())
        
        return result.strip()
    
    def generate_variations(self, text: str) -> List[str]:
        """Generate variations of the transliterated text"""
        base = self.transliterate(text)
        variations = [base]
        
        # Common variations in spelling
        replacements = [
            ('ee', 'i'),
            ('oo', 'u'),
            ('ai', 'e'),
            ('au', 'o'),
            ('sh', 's'),
            ('chh', 'ch'),
            ('ph', 'f'),
            ('bh', 'b'),
            ('dh', 'd'),
            ('th', 't'),
            ('kh', 'k'),
            ('gh', 'g'),
            ('jh', 'j'),
            
            # Common word variations
            ('mein', 'me'),
            ('hai', 'he'),
            ('hain', 'he'),
            ('kitna', 'kitana'),
            ('price', 'rate'),
            ('rate', 'price'),
            ('ka', 'ki'),
            ('ki', 'ka'),
            ('ke', 'ka'),
        ]
        
        # Generate variations
        current = base
        for old, new in replacements:
            if old in current:
                variation = current.replace(old, new)
                if variation not in variations:
                    variations.append(variation)
        
        return variations[:5]  # Limit to 5 variations

    def normalize_query(self, query: str) -> str:
        """Normalize a query for better matching"""
        # Convert to lowercase
        query = query.lower().strip()
        
        # Remove extra spaces
        query = ' '.join(query.split())
        
        # Transliterate if contains Hindi characters
        if any(ord(char) >= 0x0900 and ord(char) <= 0x097F for char in query):
            query = self.transliterate(query)
        
        # Common normalizations
        normalizations = {
            'kya': 'kya',
            'kyaa': 'kya',
            'kiya': 'kya',
            'price': 'price',
            'rate': 'price',
            'cost': 'price',
            'value': 'price',
            'kitna': 'kitna',
            'kitne': 'kitna',
            'kitan': 'kitna',
            'he': 'hai',
            'hae': 'hai',
            'hain': 'hai',
        }
        
        for old, new in normalizations.items():
            query = query.replace(old, new)
        
        return query

# Global instance
_transliterator = None

def get_transliterator() -> HindiTransliterator:
    """Get singleton transliterator instance"""
    global _transliterator
    if _transliterator is None:
        _transliterator = HindiTransliterator()
    return _transliterator

def transliterate_hindi(text: str) -> str:
    """Convenience function to transliterate Hindi text"""
    return get_transliterator().transliterate(text)

def normalize_hindi_query(query: str) -> str:
    """Convenience function to normalize Hindi/Hinglish query"""
    return get_transliterator().normalize_query(query)

def get_query_variations(query: str) -> List[str]:
    """Get variations of a query for better matching"""
    return get_transliterator().generate_variations(query)