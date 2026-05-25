"""
Tool 1: Student Progress Fetcher
Retrieves comprehensive learning data from database
"""

import sqlite3
from typing import Dict, List, Optional
from datetime import datetime

class ProgressFetcher:
    """Fetch and format student learning progress"""
    
    def __init__(self, db_path: str = "database/learning.db"):
        self.db_path = db_path
    
    def fetch_student_data(self, user_id: str) -> Optional[Dict]:
        """Fetch complete student profile and progress"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT user_id, full_name, target_role, current_phase, 
                   daily_streak, total_hours_spent
            FROM students 
            WHERE user_id = ?
        """, (user_id,))
        
        student_row = cursor.fetchone()
        
        if not student_row:
            conn.close()
            return None
        cursor.execute("""
            SELECT topic_name, topic_status, difficulty_level, time_spent_hours
            FROM topics 
            WHERE user_id = ?
            ORDER BY 
                CASE topic_status 
                    WHEN 'pending' THEN 1 
                    WHEN 'completed' THEN 2 
                END
        """, (user_id,))
        
        topics = cursor.fetchall()
        completed_topics = [
            {"name": t[0], "difficulty": t[2], "hours": t[3]} 
            for t in topics if t[1] == 'completed'
        ]
        
        pending_topics = [
            {"name": t[0], "difficulty": t[2]} 
            for t in topics if t[1] == 'pending'
        ]
        
        conn.close()
        total_topics = len(completed_topics) + len(pending_topics)
        progress_percentage = (len(completed_topics) / total_topics) * 100 if total_topics > 0 else 0
        return {
            "user_id": student_row[0],
            "name": student_row[1],
            "target_role": student_row[2],
            "current_phase": student_row[3],
            "streak_days": student_row[4],
            "total_hours": student_row[5],
            "completed_topics": completed_topics,
            "pending_topics": pending_topics,
            "progress_percentage": round(progress_percentage, 1),
            "completed_count": len(completed_topics),
            "pending_count": len(pending_topics),
            "next_topic": pending_topics[0]["name"] if pending_topics else None
        }
    
    def format_progress_message(self, data: Dict) -> str:
        """Create a human-readable progress summary"""
        
        if not data:
            return "❌ Student not found"
        
        msg = f"""
**Learning Progress Report**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 **Student:** {data['name']}
 **Goal:** {data['target_role']}
**Current Phase:** {data['current_phase']}
**Streak:** {data['streak_days']} days
**Total Time:** {data['total_hours']} hours

**Progress:** {data['progress_percentage']}% complete
   Completed: {data['completed_count']} topics
   Pending: {data['pending_count']} topics

**Completed Topics:**
{self._format_topic_list(data['completed_topics'], '✅')}

**Pending Topics:**
{self._format_topic_list(data['pending_topics'], '⏳')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        return msg
    
    def _format_topic_list(self, topics: List[Dict], emoji: str) -> str:
        """Format topic list nicely"""
        if not topics:
            return "   None"
        
        lines = []
        for topic in topics[:5]: 
            difficulty = topic.get('difficulty', 'N/A')
            hours = topic.get('hours', '')
            if hours:
                lines.append(f"   {emoji} {topic['name']} ({difficulty}) - {hours} hrs")
            else:
                lines.append(f"   {emoji} {topic['name']} ({difficulty})")
        
        if len(topics) > 5:
            lines.append(f"   ... and {len(topics) - 5} more")
        
        return '\n'.join(lines)