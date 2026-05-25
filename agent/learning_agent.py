"""
AI Learning Companion Agent
Orchestrates tools, memory, and LLM for intelligent responses
"""

import os
import sys
from typing import Dict, Optional
from datetime import datetime

sys.path.append('.')
try:
    from langchain.chat_models import ChatOpenAI
    from langchain.memory import ConversationBufferMemory
    from langchain.agents import initialize_agent, AgentType
    from langchain.tools import Tool
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("LangChain not installed. Running in basic mode.")
from tools.progress_fetcher import ProgressFetcher
from tools.step_suggester import StepSuggester
from memory.conversation_memory import ConversationMemory


class LearningCompanionAgent:
    """Main AI Agent that powers the learning companion"""
    
    def __init__(self, use_llm: bool = False):
        """
        Initialize the agent with all components
        
        Args:
            use_llm: If False, uses rule-based fallback (no API key needed)
                    If True, attempts to use OpenAI GPT (requires API key)
        """
        self.progress_fetcher = ProgressFetcher()
        self.step_suggester = StepSuggester()
        self.memory = ConversationMemory()
        self.use_llm = use_llm and LANGCHAIN_AVAILABLE
        self.agent = None
        self.chat_memory = None
        if self.use_llm:
            self._initialize_llm()
        else:
            print("✅ Running in intelligent rule-based mode (no API key needed)")
    
    def _initialize_llm(self):
        """Initialize LangChain with OpenAI (optional)"""
        
        api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            print("OPENAI_API_KEY not found in environment variables")
            print("Falling back to rule-based mode")
            self.use_llm = False
            return
        
        try:
            self.chat_memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True
            )
            tools = [
                Tool(
                    name="Fetch Student Progress",
                    func=self._fetch_progress_wrapper,
                    description="Get complete learning progress for a student including completed and pending topics"
                ),
                Tool(
                    name="Get Next Step Suggestion",
                    func=self._suggest_step_wrapper,
                    description="Generate personalized next step recommendation based on student's progress"
                )
            ]
            self.llm = ChatOpenAI(
                model="gpt-3.5-turbo",
                temperature=0.7,
                openai_api_key=api_key
            )
            self.agent = initialize_agent(
                tools=tools,
                llm=self.llm,
                agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
                memory=self.chat_memory,
                verbose=False,
                handle_parsing_errors=True,
                max_iterations=3
            )
            
            print("✅ OpenAI integration enabled! Using GPT-3.5 for enhanced responses")
            
        except Exception as e:
            print(f" Failed to initialize OpenAI: {str(e)}")
            print("Falling back to rule-based mode")
            self.use_llm = False
    
    def _fetch_progress_wrapper(self, user_id: str) -> str:
        """Wrapper for LangChain tool to fetch student progress"""
        try:
            data = self.progress_fetcher.fetch_student_data(user_id)
            if data:
                return self.progress_fetcher.format_progress_message(data)
            return "❌ Student not found. Please check the user ID."
        except Exception as e:
            return f"❌ Error fetching progress: {str(e)}"
    
    def _suggest_step_wrapper(self, user_id: str) -> str:
        """Wrapper for LangChain tool to suggest next step"""
        try:
            data = self.progress_fetcher.fetch_student_data(user_id)
            if data:
                suggestion = self.step_suggester.suggest_next_step(data)
                return self.step_suggester.format_suggestion(suggestion)
            return "❌ Unable to generate suggestion: Student not found"
        except Exception as e:
            return f"❌ Error generating suggestion: {str(e)}"
    
    def _handle_greeting(self, query_lower: str) -> Optional[str]:
        """Handle greeting messages"""
        greetings = ['hello', 'hi', 'hey', 'greetings', 'good morning', 'good afternoon', 'good evening']
        if any(greeting in query_lower for greeting in greetings):
            return " Hello! I'm your AI Learning Coach. How can I help you today? Try asking 'What should I do today?' or 'Show my progress'"
        return None
    
    def _handle_farewell(self, query_lower: str) -> Optional[str]:
        """Handle farewell messages"""
        farewells = ['bye', 'goodbye', 'see you', 'exit', 'quit', 'thanks', 'thank you']
        if any(farewell in query_lower for farewell in farewells):
            return " You're welcome! Keep learning and growing. Remember: Every step forward is progress. Goodbye! "
        return None
    
    def _handle_help(self, query_lower: str) -> Optional[str]:
        """Handle help requests"""
        help_keywords = ['help', 'what can you do', 'commands', 'how to use']
        if any(keyword in query_lower for keyword in help_keywords):
            return """
**Available Commands:**

**Questions you can ask:**
  • "What should I do today?" - Get next step recommendation
  • "Show my progress" - View detailed progress report
  • "Motivate me" - Receive encouragement
  • "I'm feeling stuck" - Get helpful suggestions

**Features:**
  • Remembers our conversation
  • Tracks your learning streak
  • Suggests personalized next steps
  • Shows progress percentage

**Tip:** Just ask naturally! I understand context.
"""
        return None
    
    def respond(self, user_id: str, query: str) -> str:
        """
        Generate a contextual response to user query
        
        Args:
            user_id: Student identifier
            query: User's question (e.g., "What should I do today?")
        
        Returns:
            Personalized response
        """
        if not query or not query.strip():
            return "Hi there! What would you like to know about your learning journey?"
        
        query_lower = query.lower().strip()
        greeting_response = self._handle_greeting(query_lower)
        if greeting_response:
            return greeting_response
        
        farewell_response = self._handle_farewell(query_lower)
        if farewell_response:
            return farewell_response
        
        help_response = self._handle_help(query_lower)
        if help_response:
            return help_response
        try:
            progress_data = self.progress_fetcher.fetch_student_data(user_id)
            
            if not progress_data:
                return "❌ Sorry, I couldn't find your learning profile. Please check your user ID."
            context = self.memory.get_context_summary(user_id)
            if any(phrase in query_lower for phrase in ["what should i do", "next step", "what's next", "what to do", "recommend"]):
                suggestion = self.step_suggester.suggest_next_step(progress_data)
                response = self.step_suggester.format_suggestion(suggestion)
            elif any(phrase in query_lower for phrase in ["progress", "how am i doing", "my stats", "show progress", "status"]):
                response = self.progress_fetcher.format_progress_message(progress_data)
            elif any(phrase in query_lower for phrase in ["motivate", "encourage", "inspire", "feeling down", "demotivated"]):
                response = f"""
**You've got this, {progress_data['name']}!**

{self.step_suggester.encouragements[0]}

**Your achievements:**
   • {progress_data['progress_percentage']}% complete
   • {progress_data['streak_days']}-day streak
   • {progress_data['total_hours']} hours invested
   • {progress_data['completed_count']} topics mastered

Remember: Every expert was once a beginner. You're making amazing progress! Keep going! 🚀
"""
            elif any(phrase in query_lower for phrase in ["stuck", "struggling", "difficult", "hard", "not understanding"]):
                next_topic = progress_data.get('next_topic', 'your current topic')
                response = f"""
**I understand {progress_data['name']}! Learning can be challenging.**

**Here's what might help:**
   • Break {next_topic} into smaller chunks
   • Watch video tutorials on YouTube
   • Practice with coding exercises
   • Join study groups or forums
   • Take a short break and come back fresh

**Suggested action:** Try explaining {next_topic} to someone else - teaching reinforces learning!

You've got this! 
"""
            elif self.use_llm and self.agent:
                try:
                    full_query = f"""
Student Context:
- Name: {progress_data['name']}
- Goal: {progress_data['target_role']}
- Current Phase: {progress_data['current_phase']}
- Progress: {progress_data['progress_percentage']}% complete
- Streak: {progress_data['streak_days']} days
- Completed Topics: {len(progress_data['completed_topics'])}
- Pending Topics: {len(progress_data['pending_topics'])}
- Next Topic: {progress_data.get('next_topic', 'None')}

Recent Conversation:
{context}

Student Question: {query}

Please provide a helpful, encouraging, and personalized response as a learning coach.
"""
                    response = self.agent.run(full_query)
                except Exception as e:
                    response = f"I understand you're asking about your learning journey. Could you please rephrase? (Tip: Try 'What should I do today?' or 'Show my progress')"
            else:
                response = f"""
I'm here to help you become a {progress_data['target_role']}!

**Try asking me:**
   • 'What should I do today?' - Get next step
   • 'Show my progress' - View your stats
   • 'Motivate me' - Get encouragement
   • 'I'm feeling stuck' - Get unstuck

You're currently in **{progress_data['current_phase']}** with {progress_data['progress_percentage']}% progress. Keep going!
"""
            self.memory.add_interaction(user_id, query, response)
            
            return response
            
        except Exception as e:
            if "database disk image is malformed" in str(e):
                return """
❌ **Database connection issue detected!**

**Quick fix:**
   1. Run: `python setup_database.py`
   2. Then restart the application

This will recreate the database with fresh data. Don't worry - your learning progress will be restored!
"""
            else:
                return f"""
❌ **Oops! Something went wrong:** {str(e)}

**Try these solutions:**
   1. Restart the application
   2. Run `python setup_database.py` to reset database
   3. Make sure you're in the correct directory

Still having issues? Try asking 'help' for available commands.
"""
    
    def get_agent_status(self) -> Dict:
        """Get current agent status for debugging"""
        return {
            "mode": "LLM Enhanced" if self.use_llm else "Rule-based",
            "langchain_available": LANGCHAIN_AVAILABLE,
            "memory_enabled": True,
            "tools_available": ["ProgressFetcher", "StepSuggester"],
            "database_status": "connected" if self.progress_fetcher.fetch_student_data("user_123") else "error"
        }
if __name__ == "__main__":
    print("Testing LearningCompanionAgent...")
    agent = LearningCompanionAgent(use_llm=False)
    status = agent.get_agent_status()
    print(f"Agent Status: {status}")
    response = agent.respond("user_123", "What should I do today?")
    print(response)