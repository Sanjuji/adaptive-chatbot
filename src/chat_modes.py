#!/usr/bin/env python3
"""
Chat Modes - Choose between Voice Chat and Text Chat
"""

import sys
import os
import subprocess

def main():
    print("🤖 Adaptive Chatbot - Chat Mode Selection")
    print("=" * 50)
    
    print("\nChoose your chat mode:")
    print("1️⃣  Interactive Voice Teaching (Step-by-step सिखाएं)")
    print("2️⃣  Voice Chat (बोलकर बात करें)")
    print("3️⃣  Text Chat (टाइप करके बात करें)")
    print("4️⃣  Exit (बाहर निकलें)")
    
    while True:
        try:
            choice = input("\nEnter your choice (1/2/3/4): ").strip()
            
            if choice == "1":
                print("\n🎓 Starting Interactive Voice Teaching...")
                print("Perfect teaching system:")
                print("1. Say 'teach' to start")
                print("2. Bot will ask for QUESTION")
                print("3. Bot will ask for ANSWER")
                print("4. Bot will learn immediately!")
                input("Press Enter to continue...")
                
                # Start interactive teaching
                subprocess.run([sys.executable, "interactive_voice_teaching.py"])
                break
                
            elif choice == "2":
                print("\n🎤 Starting Voice Chat...")
                print("You can teach by saying: 'teach [topic] [details]'")
                print("Example: 'teach LED bulb ki power LED 9 watt mein aata hai'")
                input("Press Enter to continue...")
                
                # Start voice chat
                subprocess.run([sys.executable, "-m", "src.cli", "voice-chat", "--domain", "shop"])
                break
                
            elif choice == "3":
                print("\n💬 Starting Text Chat...")
                print("You can teach by typing: 'teach: [question] | [answer]'")
                print("Example: 'teach: LED bulb ki power | LED 9 watt mein aata hai'")
                input("Press Enter to continue...")
                
                # Start text chat
                subprocess.run([sys.executable, "-m", "src.cli", "chat", "--domain", "shop"])
                break
                
            elif choice == "4":
                print("👋 Goodbye! धन्यवाद!")
                break
                
            else:
                print("❌ Invalid choice! Please enter 1, 2, 3, or 4.")
                continue
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            continue

if __name__ == "__main__":
    main()