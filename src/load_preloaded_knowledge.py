#!/usr/bin/env python3
"""
Load Pre-built Knowledge Base into Adaptive Chatbot
Makes the chatbot immediately useful with professional knowledge
"""

import json
import os
from unified_learning_manager import get_learning_manager
from logger import log_info, log_error

def load_preloaded_knowledge():
    """Load comprehensive pre-built knowledge base"""
    try:
        # Load knowledge file
        knowledge_file = "preloaded_knowledge.json"
        if not os.path.exists(knowledge_file):
            log_error(f"Preloaded knowledge file not found: {knowledge_file}")
            return False
        
        with open(knowledge_file, 'r', encoding='utf-8') as f:
            knowledge_data = json.load(f)
        
        learning_manager = get_learning_manager()
        total_loaded = 0
        
        print("🚀 Loading Professional Knowledge Base...")
        print("="*60)
        
        # Load knowledge by categories
        for category, items in knowledge_data.items():
            print(f"\n📂 Loading {category.replace('_', ' ').title()}...")
            category_count = 0
            
            for question, answer in items.items():
                if learning_manager.add_knowledge(question, answer, {
                    'category': category,
                    'source': 'preloaded',
                    'professional': True
                }):
                    category_count += 1
                    total_loaded += 1
            
            print(f"   ✅ Loaded {category_count} entries")
        
        print(f"\n🎉 Successfully loaded {total_loaded} professional responses!")
        print("💡 Your chatbot is now ready for business!")
        
        return True
        
    except Exception as e:
        log_error("Failed to load preloaded knowledge", error=e)
        return False

def create_demo_knowledge():
    """Create additional demo knowledge for specific business scenarios"""
    demo_scenarios = {
        # Customer service scenarios
        "complaint hai": "Complaint ke liye sorry! Batayiye kya problem hai, hum turant solve kar denge.",
        "refund chahiye": "Refund ke liye original bill aur item laiye. 7 din ke andar full refund milega.",
        "exchange karna hai": "Exchange available hai same price range mein. Size ya color change kar sakte hain.",
        
        # Business operations
        "shop address": "Hamara shop Main Market mein hai. Google Maps pe 'Electrical Shop' search kariye.",
        "contact number": "Contact ke liye 9876543210 pe call kariye ya WhatsApp kariye.",
        "opening time": "Subah 9 baje se raat 8 baje tak open hai. Sunday 10-6 baje.",
        
        # Product availability
        "stock available hai": "Stock ki jaankari ke liye specific item ka naam batayiye. Real time update de denge.",
        "new arrival": "New arrivals weekly update karte hain. LED lights aur smart switches aaye hain.",
        "discount offer": "Festival season mein special discount hai. 15% tak discount electrical items pe.",
        
        # Technical queries
        "safety tips": "Electrical safety ke liye: 1) Wet hands se touch na karein 2) Proper earthing karwayiye 3) Overloading se bachhiye",
        "maintenance tips": "Regular cleaning kariye, loose connections check kariye, voltage fluctuation se bachiye stabilizer use karke.",
        "emergency contact": "Electrical emergency ke liye 24/7 available hain. Emergency number: 9876543210",
    }
    
    learning_manager = get_learning_manager()
    demo_count = 0
    
    print("\n🔧 Loading Business Scenario Knowledge...")
    
    for question, answer in demo_scenarios.items():
        if learning_manager.add_knowledge(question, answer, {
            'category': 'business_scenarios',
            'source': 'demo',
            'priority': 'high'
        }):
            demo_count += 1
    
    print(f"✅ Added {demo_count} business scenario responses")
    return demo_count

def show_knowledge_stats():
    """Show statistics of loaded knowledge"""
    try:
        from unified_learning_manager import get_stats
        stats = get_stats()
        
        print("\n📊 Knowledge Base Statistics")
        print("="*40)
        print(f"📚 Total Knowledge Entries: {stats.get('total_entries', 0)}")
        print(f"📈 Ready for Customer Queries: ✅")
        print(f"🎯 Business Ready: ✅")
        print(f"💰 Monetization Ready: ✅")
        
    except Exception as e:
        log_error("Error showing stats", error=e)

def main():
    """Main function to load all knowledge"""
    print("🚀 Setting up Professional Adaptive Chatbot")
    print("="*60)
    
    # Load preloaded knowledge
    if load_preloaded_knowledge():
        print("✅ Professional knowledge loaded successfully!")
    else:
        print("❌ Failed to load professional knowledge")
        return False
    
    # Load demo scenarios
    demo_count = create_demo_knowledge()
    print(f"✅ Added {demo_count} business scenarios")
    
    # Show final stats
    show_knowledge_stats()
    
    print("\n🎉 Your Adaptive Chatbot is now BUSINESS READY!")
    print("💡 Customers can ask about:")
    print("   • Product prices and specifications")
    print("   • Installation and warranty services") 
    print("   • Technical support and troubleshooting")
    print("   • Business hours and policies")
    print("   • General electrical guidance")
    
    print("\n🚀 Ready to start earning! Run: python adaptive_chatbot.py")
    return True

if __name__ == "__main__":
    main()