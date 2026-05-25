"""
Conversation Memory Handler
Stores and retrieves chat history for context-aware responses
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional

class ConversationMemory:
    """Manages conversation history with SQLite storage"""
    
    def __init__(self, db_path: str = "database/learning.db"):
        self.db_path = db_path
    
    def add_interaction(self, user_id: str, query: str, response: str):
        """Store a conversation exchange"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO learning_sessions (user_id, query, response, timestamp)
            VALUES (?, ?, ?, ?)
        """, (user_id, query, response, datetime.now()))
        
        conn.commit()
        conn.close()
    
    def get_recent_history(self, user_id: str, limit: int = 5) -> List[Dict]:
        """Retrieve recent conversation history"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT query, response, timestamp 
            FROM learning_sessions 
            WHERE user_id = ?
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (user_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        history = []
        for row in rows:
            history.append({
                "query": row[0],
                "response": row[1],
                "timestamp": row[2]
            })
        
        return history
    
    def get_context_summary(self, user_id: str) -> str:
        """Generate a summary of recent interactions for context"""
        
        history = self.get_recent_history(user_id, limit=3)
        
        if not history:
            return "No previous conversation"
        
        summary = "Recent interactions:\n"
        for i, interaction in enumerate(history, 1):
            summary += f"{i}. You asked: '{interaction['query']}'\n"
            summary += f"   I suggested: '{interaction['response'][:100]}...'\n"
        
        return summary