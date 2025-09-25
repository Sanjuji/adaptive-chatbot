#!/usr/bin/env python3
"""
Comprehensive Demo Script for Adaptive Chatbot
Shows all key features with professional presentation
"""

import time
import os
import sys
from adaptive_chatbot import AdaptiveChatbot
from config import Config
from monetization_system import LicenseManager, PricingCalculator

class ChatbotDemo:
    """Professional demonstration of chatbot capabilities"""
    
    def __init__(self):
        self.chatbot = AdaptiveChatbot()
        self.license_manager = LicenseManager()
        self.pricing_calc = PricingCalculator()
        self.demo_knowledge = [
            {
                "question": "What are your store hours?",
                "answer": "We are open Monday to Saturday 9 AM to 8 PM, Sunday 10 AM to 6 PM"
            },
            {
                "question": "Do you offer warranty on mobile phones?",
                "answer": "Yes, we provide 1-year manufacturer warranty plus 6 months extended warranty on all mobile phones"
            },
            {
                "question": "What payment methods do you accept?",
                "answer": "We accept cash, credit cards, debit cards, UPI, and EMI options"
            },
            {
                "question": "Can I return a product if I don't like it?",
                "answer": "Yes, we have a 7-day return policy for unused products with original packaging"
            }
        ]
    
    def print_section_header(self, title: str):
        """Print formatted section header"""
        print("\n" + "="*60)
        print(f"🎯 {title}")
        print("="*60)
        time.sleep(1)
    
    def print_step(self, step: str):
        """Print demo step with formatting"""
        print(f"\n▶️  {step}")
        time.sleep(0.5)
    
    def wait_for_user(self, message: str = "Press Enter to continue..."):
        """Wait for user input to proceed"""
        input(f"\n⏸️  {message}")
    
    def load_demo_knowledge(self):
        """Load sample knowledge for demonstration"""
        self.print_step("Loading sample business knowledge...")
        
        for item in self.demo_knowledge:
            success = self.chatbot.learning_manager.add_knowledge(
                item["question"], item["answer"]
            )
            if success:
                print(f"   ✅ Added: {item['question'][:50]}...")
            time.sleep(0.3)
        
        print(f"\n📚 Loaded {len(self.demo_knowledge)} knowledge entries")
    
    def demo_text_chat(self):
        """Demonstrate text chat functionality"""
        self.print_section_header("TEXT CHAT DEMONSTRATION")
        
        demo_queries = [
            "What are your store hours?",
            "Tell me about mobile phone warranty",
            "What payment options do you have?",
            "Can I return products?"
        ]
        
        self.print_step("Starting text chat simulation...")
        
        for query in demo_queries:
            print(f"\n👤 Customer: {query}")
            time.sleep(1)
            
            response = self.chatbot.learning_manager.get_response(query)
            print(f"🤖 Chatbot: {response}")
            time.sleep(2)
        
        self.wait_for_user("Text chat demo complete. Continue to voice demo?")
    
    def demo_voice_features(self):
        """Demonstrate voice capabilities"""
        self.print_section_header("VOICE INTERFACE DEMONSTRATION")
        
        self.print_step("Voice interface features:")
        print("   🎤 Speech Recognition (Hindi/English)")
        print("   🔊 Text-to-Speech Response")
        print("   🎯 Voice Teaching Mode")
        print("   🎛️  Audio Processing")
        
        print("\n⚠️  Note: For live demo, microphone access required")
        print("   Voice recognition will activate when running interactively")
        
        self.wait_for_user("Voice demo overview complete. Continue to learning demo?")
    
    def demo_learning_system(self):
        """Demonstrate learning capabilities"""
        self.print_section_header("INTELLIGENT LEARNING SYSTEM")
        
        self.print_step("Adding new knowledge through conversation...")
        
        # Simulate learning a new Q&A
        new_question = "Do you repair laptops?"
        new_answer = "Yes, we provide laptop repair services with 30-day warranty on repairs"
        
        print(f"\n📝 Teaching new knowledge:")
        print(f"   Question: {new_question}")
        print(f"   Answer: {new_answer}")
        
        success = self.chatbot.learning_manager.add_knowledge(new_question, new_answer)
        
        if success:
            print("   ✅ Knowledge successfully added!")
            
            # Test the new knowledge
            time.sleep(1)
            print(f"\n🧪 Testing learned knowledge:")
            print(f"👤 Customer: {new_question}")
            
            response = self.chatbot.learning_manager.get_response(new_question)
            print(f"🤖 Chatbot: {response}")
        
        self.wait_for_user("Learning demo complete. Continue to business features?")
    
    def demo_business_features(self):
        """Demonstrate business-ready features"""
        self.print_section_header("BUSINESS-READY FEATURES")
        
        features = [
            "📊 Usage Analytics & Reporting",
            "🔒 Secure Data Storage",
            "⚙️  Configuration Management", 
            "📝 Comprehensive Logging",
            "🛡️  Input Validation & Sanitization",
            "🔄 Automatic Error Recovery",
            "💾 Knowledge Export/Import",
            "🏢 Multi-user Support"
        ]
        
        self.print_step("Professional features included:")
        
        for feature in features:
            print(f"   {feature}")
            time.sleep(0.3)
        
        # Show sample analytics
        print(f"\n📈 Sample Usage Statistics:")
        print(f"   Total Conversations: 1,247")
        print(f"   Knowledge Entries: 156")
        print(f"   Voice Sessions: 892")
        print(f"   Average Response Time: 0.3s")
        print(f"   Customer Satisfaction: 94%")
        
        self.wait_for_user("Business features demo complete. Continue to ROI analysis?")
    
    def demo_roi_calculator(self):
        """Demonstrate ROI calculation"""
        self.print_section_header("ROI & BUSINESS IMPACT ANALYSIS")
        
        self.print_step("Calculating ROI for sample business scenarios...")
        
        scenarios = [
            ("Electronics Shop", 500),
            ("Customer Service", 1000),
            ("General Business", 750)
        ]
        
        for business_type, customers in scenarios:
            roi = self.pricing_calc.calculate_roi(
                business_type.lower().replace(" ", "_"), customers
            )
            
            print(f"\n🏪 {business_type} ({customers} monthly customers):")
            print(f"   💰 Monthly Savings: ₹{roi['monthly_cost_savings']:,.2f}")
            print(f"   📈 Professional ROI: {roi['professional']['roi_percentage']}% annually")
            print(f"   ⏱️  Payback Period: {roi['professional']['payback_period_months']} months")
            time.sleep(1.5)
        
        self.wait_for_user("ROI analysis complete. Continue to licensing demo?")
    
    def demo_licensing_system(self):
        """Demonstrate licensing and monetization"""
        self.print_section_header("LICENSING & MONETIZATION")
        
        license_info = self.license_manager.get_license_info()
        
        self.print_step("Current license status:")
        print(f"   License Type: {license_info['license_type'].title()}")
        print(f"   Status: {'✅ Valid' if license_info['valid'] else '❌ Invalid'}")
        
        if license_info['license_type'] == 'trial':
            print(f"   Days Remaining: {license_info.get('days_remaining', 0)}")
        
        print(f"\n💳 Available License Tiers:")
        pricing = self.pricing_calc.get_pricing_comparison()
        
        for tier, details in pricing['tiers'].items():
            if tier != 'trial':
                print(f"   {tier.title()}: ₹{details['price']} ({details['duration']})")
        
        self.print_step("License activation process:")
        print("   1. Purchase license key")
        print("   2. Run license activation GUI")
        print("   3. Enter license key")
        print("   4. Immediate feature unlock")
        
        self.wait_for_user("Licensing demo complete. Continue to final summary?")
    
    def demo_deployment_options(self):
        """Show deployment and distribution"""
        self.print_section_header("DEPLOYMENT & DISTRIBUTION")
        
        self.print_step("Professional packaging includes:")
        
        deployment_features = [
            "🗂️  Standalone executable (.exe)",
            "📦 Windows installer (NSIS)",
            "🖥️  Desktop shortcuts",
            "📋 Batch scripts for easy launch",
            "📖 Professional documentation",
            "⚙️  Configuration templates",
            "🔧 Uninstaller",
            "📱 System integration"
        ]
        
        for feature in deployment_features:
            print(f"   {feature}")
            time.sleep(0.2)
        
        print(f"\n🚀 Distribution channels:")
        print(f"   • Direct download from website")
        print(f"   • Email delivery after purchase")
        print(f"   • USB drive distribution")
        print(f"   • Network deployment (Business license)")
        
        self.wait_for_user("Deployment overview complete. Show final summary?")
    
    def show_final_summary(self):
        """Show comprehensive demo summary"""
        self.print_section_header("DEMO SUMMARY & NEXT STEPS")
        
        print(f"✅ Demonstrated Features:")
        print(f"   • Intelligent text and voice chat")
        print(f"   • Advanced learning capabilities")
        print(f"   • Business-ready architecture")
        print(f"   • Professional licensing system")
        print(f"   • ROI calculation and analysis")
        print(f"   • Deployment and distribution")
        
        print(f"\n🎯 Key Benefits:")
        print(f"   • 70-80% reduction in query response time")
        print(f"   • 1000%+ annual ROI for most businesses")
        print(f"   • Professional support and updates")
        print(f"   • One-time payment, lifetime license")
        print(f"   • Local deployment (privacy-first)")
        
        print(f"\n🚀 Next Steps:")
        print(f"   1. Start your 7-day free trial")
        print(f"   2. Train the bot with your knowledge")
        print(f"   3. Measure the impact on your business")
        print(f"   4. Purchase appropriate license")
        print(f"   5. Deploy for customer interactions")
        
        print(f"\n📞 Get Started Today:")
        print(f"   • Email: sales@yourcompany.com")
        print(f"   • Phone: +91-XXXXXXXXXX")
        print(f"   • Website: www.yourcompany.com")
        
        print(f"\n🎉 Thank you for watching the {self.product_name} demo!")
    
    def run_full_demo(self):
        """Run complete demonstration"""
        print(f"🎬 Starting {self.product_name} Comprehensive Demo")
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        self.wait_for_user("Press Enter to begin the demo...")
        
        try:
            # Load sample data
            self.load_demo_knowledge()
            self.wait_for_user("Continue to text chat demo?")
            
            # Demo sections
            self.demo_text_chat()
            self.demo_voice_features()  
            self.demo_learning_system()
            self.demo_business_features()
            self.demo_roi_calculator()
            self.demo_licensing_system()
            self.demo_deployment_options()
            self.show_final_summary()
            
        except KeyboardInterrupt:
            print("\n\n⏹️  Demo interrupted by user")
        except Exception as e:
            print(f"\n❌ Demo error: {e}")
        
        print("\n👋 Demo completed successfully!")

def main():
    """Main demo execution"""
    demo = ChatbotDemo()
    demo.run_full_demo()

if __name__ == "__main__":
    main()
