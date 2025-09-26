#!/usr/bin/env python3
"""
Electrical Business Domain Enhancer
Specialized knowledge and intent patterns for electrical business chatbot
"""

import re
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

# Import existing systems
try:
    from advanced_nlp import get_nlp_engine
    from unified_learning_manager import UnifiedLearningManager
    from logger import log_info, log_error, log_warning
    NLP_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Some modules unavailable: {e}")
    NLP_AVAILABLE = False

class ElectricalBusinessEnhancer:
    """Domain-specific enhancements for electrical business chatbot"""
    
    def __init__(self):
        self.nlp_engine = get_nlp_engine() if NLP_AVAILABLE else None
        self.business_knowledge = self._initialize_electrical_knowledge()
        self.enhanced_patterns = self._load_electrical_patterns()
        self.product_categories = self._load_product_categories()
        
    def _initialize_electrical_knowledge(self) -> Dict[str, Any]:
        """Initialize electrical business knowledge base"""
        return {
            # Basic electrical items with pricing
            "switch ki price": "Switch का price 50-200 rupees तक है, brand और type के according",
            "wire ka rate": "Wire का rate 45-80 rupees per meter है, copper wire के लिए",
            "socket ka price": "Socket का price 80-150 rupees है, 3-pin या 2-pin के according",
            "mcb price": "MCB का price 150-400 rupees है, ampere rating के according",
            "cable ka rate": "Cable का rate 60-120 rupees per meter है, size और quality के according",
            "fan ka price": "Ceiling fan का price 1500-4000 rupees तक है",
            "bulb ki price": "LED bulb का price 50-300 rupees है, watt के according",
            "inverter price": "Inverter का price 3000-15000 rupees तक है, capacity के according",
            "stabilizer price": "Voltage stabilizer का price 2500-8000 rupees है",
            "geyser ka price": "Water heater का price 5000-25000 rupees तक है",
            
            # Installation services
            "wiring charges": "House wiring का charge 15-25 rupees per point है",
            "installation charges": "Electrical installation charges 200-500 rupees per item",
            "repair charges": "Electrical repair charges 100-300 rupees per visit",
            
            # Technical specifications
            "wire gauge": "House wiring के लिए 2.5mm और 4mm wire use करते हैं",
            "mcb rating": "Normal घर के लिए 16A, 20A, 32A MCB use करते हैं",
            "voltage": "India में standard voltage 220V single phase और 415V three phase है",
            
            # Business information
            "shop timings": "हमारी shop 9 AM से 8 PM तक खुली रहती है",
            "address": "हमारा address local electrical market में है",
            "warranty": "हमारे सभी products पर 1 साल warranty मिलती है",
            "payment": "हम cash, UPI, card सभी payment accept करते हैं"
        }
    
    def _load_electrical_patterns(self) -> Dict[str, List[str]]:
        """Load electrical business specific intent patterns"""
        return {
            'price_inquiry': [
                r'\b(price|rate|cost|kitna|kitne|kya bhav|दाम|कीमत|रेट)\b',
                r'\b(how much|kitne mein|kitne ka|कितने में|कितना है)\b',
                r'\b(quotation|estimate|budget|quote)\b'
            ],
            
            'product_inquiry': [
                r'\b(switch|wire|cable|socket|mcb|bulb|fan|inverter|stabilizer)\b',
                r'\b(geyser|heater|tube|light|led|cfl|panel|board)\b',
                r'\b(conduit|pvc|copper|aluminum|electrical)\b'
            ],
            
            'installation_inquiry': [
                r'\b(install|installation|fitting|लगाना|लगवाना|फिटिंग)\b',
                r'\b(wiring|connection|connect|जोड़ना|वायरिंग)\b',
                r'\b(repair|fix|service|ठीक करना|सर्विस)\b'
            ],
            
            'specification_inquiry': [
                r'\b(specification|spec|size|rating|watt|amp|volt)\b',
                r'\b(gauge|mm|ampere|voltage|power|capacity)\b',
                r'\b(technical|details|जानकारी|तकनीकी)\b'
            ],
            
            'business_inquiry': [
                r'\b(shop|store|address|location|timing|time)\b',
                r'\b(warranty|guarantee|payment|delivery|service)\b',
                r'\b(contact|phone|mobile|दुकान|पता|समय)\b'
            ],
            
            'complaint': [
                r'\b(problem|issue|complaint|defective|faulty)\b',
                r'\b(not working|खराब|समस्या|शिकायत|बिगड़|गलत)\b',
                r'\b(poor quality|bad|waste|बेकार|घटिया)\b'
            ],
            
            'greeting_electrical': [
                r'\b(electrical|electrician|bijli|current|बिजली)\b',
                r'\b(electrical shop|electrical store|electrical work)\b'
            ]
        }
    
    def _load_product_categories(self) -> Dict[str, List[str]]:
        """Load electrical product categories with synonyms"""
        return {
            'switches': [
                'switch', 'switches', 'स्विच', 'button', 'on off',
                'modular switch', 'traditional switch', 'dimmer switch'
            ],
            
            'wires_cables': [
                'wire', 'wires', 'cable', 'cables', 'तार', 'केबल',
                'copper wire', 'aluminium wire', 'house wire', 'flexible wire'
            ],
            
            'sockets_plugs': [
                'socket', 'sockets', 'plug', 'plugs', 'socket outlet',
                '2 pin socket', '3 pin socket', '5A socket', '15A socket'
            ],
            
            'mcb_protection': [
                'mcb', 'breaker', 'circuit breaker', 'miniature circuit breaker',
                'fuse', 'protection', 'safety switch', 'trip switch'
            ],
            
            'lighting': [
                'bulb', 'bulbs', 'led', 'cfl', 'tube light', 'बल्ब',
                'lamp', 'light', 'lighting', 'chandelier', 'panel light'
            ],
            
            'fans': [
                'fan', 'fans', 'ceiling fan', 'table fan', 'exhaust fan',
                'पंखा', 'cooler', 'air circulation', 'ventilation'
            ],
            
            'power_backup': [
                'inverter', 'ups', 'battery', 'stabilizer', 'voltage stabilizer',
                'power backup', 'emergency power', 'battery backup'
            ],
            
            'heating': [
                'geyser', 'water heater', 'immersion rod', 'heater',
                'गीजर', 'hot water', 'electric heater', 'instant geyser'
            ]
        }
    
    def enhance_intent_recognition(self, text: str) -> Dict[str, Any]:
        """Enhanced intent recognition for electrical business"""
        if not self.nlp_engine:
            return {"intent": "general", "confidence": 0.5}
        
        # Get base intent from NLP engine
        base_intent = self.nlp_engine.extract_intent(text)
        text_lower = text.lower()
        
        # Check for electrical business specific intents
        electrical_intents = {}
        
        for intent, patterns in self.enhanced_patterns.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    score += 0.3
            
            if score > 0:
                electrical_intents[intent] = min(score, 1.0)
        
        # Combine base intent with electrical intents
        if electrical_intents:
            # Find highest scoring electrical intent
            top_electrical = max(electrical_intents.items(), key=lambda x: x[1])
            
            # If electrical intent has higher confidence, use it
            if top_electrical[1] > base_intent['confidence']:
                return {
                    "intent": top_electrical[0],
                    "confidence": top_electrical[1],
                    "base_intent": base_intent['intent'],
                    "electrical_specific": True,
                    "all_intents": electrical_intents
                }
        
        # Return base intent with electrical context
        return {
            **base_intent,
            "electrical_specific": bool(electrical_intents),
            "electrical_intents": electrical_intents
        }
    
    def identify_products(self, text: str) -> List[Dict[str, Any]]:
        """Identify electrical products mentioned in text"""
        identified_products = []
        text_lower = text.lower()
        
        for category, products in self.product_categories.items():
            for product in products:
                if product.lower() in text_lower:
                    # Check if not already identified
                    if not any(p['product'] == product for p in identified_products):
                        identified_products.append({
                            "product": product,
                            "category": category,
                            "confidence": 0.8 if len(product) > 3 else 0.6
                        })
        
        return identified_products
    
    def get_electrical_knowledge(self, query: str) -> Optional[str]:
        """Get electrical business specific knowledge"""
        query_normalized = self._normalize_electrical_query(query)
        
        # Direct lookup
        if query_normalized in self.business_knowledge:
            return self.business_knowledge[query_normalized]
        
        # Fuzzy matching for electrical terms
        for known_query, answer in self.business_knowledge.items():
            if self._electrical_queries_match(query_normalized, known_query):
                return answer
        
        return None
    
    def _normalize_electrical_query(self, query: str) -> str:
        """Normalize electrical business queries"""
        query_lower = query.lower().strip()
        
        # Common normalizations for electrical terms
        normalizations = {
            'price': ['rate', 'cost', 'kitna', 'kitne', 'दाम', 'कीमत', 'रेट'],
            'ka': ['ki', 'ke'],
            'switch': ['स्विच', 'button'],
            'wire': ['तार', 'cable', 'केबल'],
            'socket': ['plug point', 'outlet'],
            'bulb': ['बल्ब', 'light', 'lamp'],
            'fan': ['पंखा'],
            'geyser': ['गीजर', 'water heater', 'heater']
        }
        
        # Apply normalizations
        normalized = query_lower
        for standard, variants in normalizations.items():
            for variant in variants:
                if variant in normalized:
                    normalized = normalized.replace(variant, standard)
        
        # Remove common stop words
        stop_words = ['the', 'a', 'an', 'what', 'is', 'kya', 'hai', 'ka', 'ki', 'ke']
        words = normalized.split()
        filtered_words = [w for w in words if w not in stop_words]
        
        return ' '.join(filtered_words).strip()
    
    def _electrical_queries_match(self, query1: str, query2: str) -> bool:
        """Check if two electrical queries match semantically"""
        # Extract key terms
        terms1 = set(query1.split())
        terms2 = set(query2.split())
        
        # Check for significant overlap
        common_terms = terms1.intersection(terms2)
        
        # Must have at least 60% overlap and include a product term
        overlap_ratio = len(common_terms) / max(len(terms1), len(terms2)) if terms1 or terms2 else 0
        
        has_product_term = any(term in self._get_all_product_terms() for term in common_terms)
        
        return overlap_ratio >= 0.6 and has_product_term
    
    def _get_all_product_terms(self) -> set:
        """Get all electrical product terms"""
        all_terms = set()
        for products in self.product_categories.values():
            all_terms.update(p.lower() for p in products)
        return all_terms
    
    def generate_electrical_response(self, query: str, intent_info: Dict) -> str:
        """Generate electrical business specific response"""
        
        intent = intent_info.get('intent', 'general')
        
        # Check for electrical knowledge first
        knowledge_answer = self.get_electrical_knowledge(query)
        if knowledge_answer:
            return knowledge_answer
        
        # Identify products in query
        products = self.identify_products(query)
        
        # Generate responses based on intent
        if intent == 'price_inquiry':
            if products:
                product_name = products[0]['product']
                return f"{product_name} का exact price बताने के लिए size/specification चाहिए। आप shop आकर देख सकते हैं या specific model बताइए।"
            else:
                return "कौन से electrical item का price चाहिए? Switch, wire, socket, MCB, bulb - कुछ specific बताइए।"
        
        elif intent == 'product_inquiry':
            if products:
                product_name = products[0]['product']
                category = products[0]['category']
                return f"{product_name} हमारे पास available है। {category} category में different types हैं। आप specific requirement बताइए।"
            else:
                return "हमारे पास सभी electrical items available हैं - switches, wires, sockets, MCBs, bulbs, fans आदि। क्या चाहिए?"
        
        elif intent == 'installation_inquiry':
            return "हम electrical installation और repair service भी provide करते हैं। Charges depends on work complexity. आप location और work details बताइए।"
        
        elif intent == 'business_inquiry':
            return "हमारी electrical shop में सभी branded items मिलते हैं। Shop timing: 9 AM - 8 PM। Warranty और good service guarantee के साथ।"
        
        elif intent == 'complaint':
            return "अगर कोई problem है तो हम जरूर solve करेंगे। Warranty period में free service मिलती है। आप problem detail में बताइए।"
        
        elif intent == 'greeting_electrical':
            return "नमस्ते! हमारी electrical shop में आपका स्वागत है। सभी electrical items और services available हैं। क्या चाहिए?"
        
        else:
            # Default electrical business response
            if products:
                return f"आपको {products[0]['product']} चाहिए? हमारे पास अलग-अलग brands और prices में available है। आइए shop में देख लीजिए।"
            else:
                return "मैं electrical business के बारे में आपकी help कर सकता हूँ। Products, prices, services के बारे में पूछिए।"
    
    def add_electrical_knowledge(self, learning_manager: UnifiedLearningManager, force_add: bool = False):
        """Add electrical knowledge to learning manager"""
        try:
            added_count = 0
            for question, answer in self.business_knowledge.items():
                if learning_manager.add_knowledge(question, answer):
                    added_count += 1
            
            log_info(f"Added {added_count} electrical knowledge entries")
            return added_count > 0
            
        except Exception as e:
            log_error(f"Failed to add electrical knowledge: {e}")
            return False
    
    def get_electrical_suggestions(self, partial_query: str) -> List[str]:
        """Get electrical query suggestions based on partial input"""
        suggestions = []
        partial_lower = partial_query.lower()
        
        # Check against known queries
        for query in self.business_knowledge.keys():
            if partial_lower in query.lower():
                suggestions.append(query)
        
        # Check against product names
        for products in self.product_categories.values():
            for product in products:
                if partial_lower in product.lower():
                    suggestions.append(f"{product} ka price kya hai?")
                    suggestions.append(f"{product} available hai?")
        
        return suggestions[:5]  # Return top 5 suggestions
    
    def analyze_electrical_conversation(self, conversation_history: List[Dict]) -> Dict[str, Any]:
        """Analyze conversation for electrical business insights"""
        analysis = {
            "total_queries": len(conversation_history),
            "product_inquiries": 0,
            "price_inquiries": 0,
            "installation_inquiries": 0,
            "complaints": 0,
            "popular_products": {},
            "customer_interests": []
        }
        
        for entry in conversation_history:
            query = entry.get('user_input', '')
            intent = entry.get('intent', 'general')
            
            # Count intents
            if intent == 'price_inquiry':
                analysis["price_inquiries"] += 1
            elif intent == 'product_inquiry':
                analysis["product_inquiries"] += 1
            elif intent == 'installation_inquiry':
                analysis["installation_inquiries"] += 1
            elif intent == 'complaint':
                analysis["complaints"] += 1
            
            # Track product mentions
            products = self.identify_products(query)
            for product in products:
                product_name = product['product']
                analysis["popular_products"][product_name] = analysis["popular_products"].get(product_name, 0) + 1
        
        # Determine top interests
        if analysis["popular_products"]:
            sorted_products = sorted(analysis["popular_products"].items(), key=lambda x: x[1], reverse=True)
            analysis["customer_interests"] = [p[0] for p in sorted_products[:3]]
        
        return analysis

# Global instance
_electrical_enhancer = None

def get_electrical_enhancer() -> ElectricalBusinessEnhancer:
    """Get global electrical business enhancer instance"""
    global _electrical_enhancer
    if _electrical_enhancer is None:
        _electrical_enhancer = ElectricalBusinessEnhancer()
    return _electrical_enhancer

def enhance_electrical_query(query: str) -> Dict[str, Any]:
    """Enhance query with electrical business intelligence"""
    enhancer = get_electrical_enhancer()
    
    intent_info = enhancer.enhance_intent_recognition(query)
    products = enhancer.identify_products(query)
    knowledge_answer = enhancer.get_electrical_knowledge(query)
    
    return {
        "enhanced_intent": intent_info,
        "identified_products": products,
        "knowledge_answer": knowledge_answer,
        "suggestions": enhancer.get_electrical_suggestions(query)
    }

if __name__ == "__main__":
    # Test the electrical enhancer
    enhancer = ElectricalBusinessEnhancer()
    
    test_queries = [
        "switch ka price kya hai?",
        "wire kitne ka hai?", 
        "MCB available hai?",
        "bulb installation charges",
        "fan repair karna hai",
        "electrical shop ka address?"
    ]
    
    print("🔌 Electrical Business Enhancer Test")
    print("=" * 50)
    
    for query in test_queries:
        print(f"\n📝 Query: {query}")
        
        intent_info = enhancer.enhance_intent_recognition(query)
        print(f"🎯 Intent: {intent_info['intent']} ({intent_info['confidence']:.2f})")
        
        products = enhancer.identify_products(query)
        if products:
            print(f"🔌 Products: {[p['product'] for p in products]}")
        
        knowledge = enhancer.get_electrical_knowledge(query)
        if knowledge:
            print(f"💡 Knowledge: {knowledge[:100]}...")
        
        response = enhancer.generate_electrical_response(query, intent_info)
        print(f"🤖 Response: {response[:100]}...")
        
        print("-" * 30)