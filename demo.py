"""
Quick demo showcasing the agent's capabilities
"""

from agent.learning_agent import LearningCompanionAgent

def run_demo():
    print("\nRunning AI Learning Companion Demo\n")
    print("=" * 60)
    
    agent = LearningCompanionAgent(use_llm=False)
    user_id = "user_123"
    
    test_queries = [
        "What should I do today?",
        "Show me my progress",
        "Motivate me"
    ]
    
    for query in test_queries:
        print(f"\nUser: {query}")
        print("Coach: ", end="")
        response = agent.respond(user_id, query)
        print(response)
        print("-" * 60)
    
    print("\n✅ Demo complete!\n")

if __name__ == "__main__":
    run_demo()