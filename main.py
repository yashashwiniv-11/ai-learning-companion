"""
AI Learning Companion - Main Application
A beautiful, interactive CLI for personalized learning assistance
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from agent.learning_agent import LearningCompanionAgent

def print_banner():
    """Display beautiful welcome banner"""
    banner = """ AI_LEARNING """
    print(banner)
    print("\n" + "=" * 70)
    print("Welcome! I'm here to help you on your learning journey")
    print("=" * 70 + "\n")

def main():
    """Main application loop"""
    
    print_banner()
    print("Initializing AI Learning Companion...")
    agent = LearningCompanionAgent(use_llm=False) 
    print("Ready! (Using intelligent rule-based mode)\n")
    user_id = "user_123"
    
    print(f"Hello! I'm your learning companion for {user_id}")
    print("Try asking me things like:")
    print("   • 'What should I do today?'")
    print("   • 'Show me my progress'")
    print("   • 'Motivate me'")
    print("   • 'I'm feeling stuck'")
    print("\nType 'exit', 'quit', or 'bye' to end the session\n")
    print("-" * 70)
    while True:
        try:
            user_input = input("\nYou: ").strip()
            if user_input.lower() in ['exit', 'quit', 'bye', 'goodbye']:
                print("\nKeep learning! Remember: Every step forward is progress. Goodbye!\n")
                break
            if not user_input:
                continue
            print("\nCoach: ", end="")
            response = agent.respond(user_id, user_input)
            print(response)
            
        except KeyboardInterrupt:
            print("\n\nThanks for learning with me! Until next time!\n")
            break
        except Exception as e:
            print(f"\n❌ Oops! Something went wrong: {str(e)}")
            print("Please try again or restart the application.\n")

if __name__ == "__main__":
    main()