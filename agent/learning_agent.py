"""
AI Learning Companion Agent
Orchestrates tools, memory, and LLM for intelligent responses
"""

import os
from typing import Dict, Optional
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
import sys
sys.path.append('.')
from tools.progress_fetcher import ProgressFetcher
from tools.step_suggester import StepSuggester
from memory.conversation_memory import ConversationMemory

class LearningCompanionAgent:
    """Main AI Agent that powers the learning companion"""
    
    def __init__(self, use_llm: bool = True):
        """
        Initialize the agent with all components
        
        Args:
            use_llm: If False, uses rule-based fallback (no API key needed)
        """
        self.progress_fetcher = ProgressFetcher()
        self.step_suggester = StepSuggester()
        self.memory = ConversationMemory()
        self.chat_memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        self.tools = [
            Tool(
                name="Fetch Student Progress",
                func=self._fetch_progress_wrapper,
                description="Get complete learning progress for a student"
            ),
            Tool(
                name="Get Next Step Suggestion",
                func=self._suggest_step_wrapper,
                description="Generate personalized next step recommendation"
            )
        ]
        
        self.use_llm = use_llm
        
        if use_llm:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                print("Warning: OPENAI_API_KEY not found. Falling back to rule-based mode.")
                self.use_llm = False
            else:
                self.llm = ChatOpenAI(
                    model="gpt-3.5-turbo",
                    temperature=0.7,
                    openai_api_key=api_key
                )
                
                self.agent = initialize_agent(
                    tools=self.tools,
                    llm=self.llm,
                    agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
                    memory=self.chat_memory,
                    verbose=False,
                    handle_parsing_errors=True
                )
    
    def _fetch_progress_wrapper(self, user_id: str) -> str:
        """Wrapper for LangChain tool"""
        data = self.progress_fetcher.fetch_student_data(user_id)
        if data:
            return self.progress_fetcher.format_progress_message(data)
        return "Student not found"
    
    def _suggest_step_wrapper(self, user_id: str) -> str:
        """Wrapper for LangChain tool"""
        data = self.progress_fetcher.fetch_student_data(user_id)
        if data:
            suggestion = self.step_suggester.suggest_next_step(data)
            return self.step_suggester.format_suggestion(suggestion)
        return "Unable to generate suggestion"
    
    def respond(self, user_id: str, query: str) -> str:
        """
        Generate a contextual response to user query
        
        Args:
            user_id: Student identifier
            query: User's question (e.g., "What should I do today?")
        
        Returns:
            Personalized response
        """
        progress_data = self.progress_fetcher.fetch_student_data(user_id)
        
        if not progress_data:
            return "❌ Sorry, I couldn't find your learning profile."
        context = self.memory.get_context_summary(user_id)
        query_lower = query.lower()
        if "what should i do" in query_lower or "next step" in query_lower:
            suggestion = self.step_suggester.suggest_next_step(progress_data)
            response = self.step_suggester.format_suggestion(suggestion)
            
        elif "progress" in query_lower or "how am i doing" in query_lower:
            response = self.progress_fetcher.format_progress_message(progress_data)
            
        elif "motivate" in query_lower or "encourage" in query_lower:
            response = f"""
**You've got this, {progress_data['name']}!** 

{self.step_suggester.encouragements[0]}
You've already spent {progress_data['total_hours']} hours learning!
Your {progress_data['streak_days']}-day streak is proof of your dedication.

Remember: Every expert was once a beginner. Keep going! 
"""
        else:
            if self.use_llm:
                try:
                    full_query = f"""
Student: {progress_data['name']}
Goal: {progress_data['target_role']}
Current progress: {progress_data['progress_percentage']}%
Context: {context}

Student asks: {query}

Please provide a helpful, encouraging response.
"""
                    response = self.agent.run(full_query)
                except Exception as e:
                    response = f"I understand you're asking about learning. Could you rephrase? (Error: {str(e)})"
            else:
                response = f"I'm here to help you learn {progress_data['target_role']}! Try asking: 'What should I do today?' or 'Show my progress'"
        self.memory.add_interaction(user_id, query, response)
        
        return response