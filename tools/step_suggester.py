"""
Tool 2: Intelligent Step Suggester
Provides personalized learning recommendations
"""

from typing import Dict
import random

class StepSuggester:
    """Generate contextual learning suggestions"""
    
    def __init__(self):
        self.practice_ideas = [
            "Build a small project using",
            "Create flashcards for",
            "Solve 5 coding challenges about",
            "Explain to a friend how",
            "Write a blog post explaining",
            "Record a 2-minute video tutorial on"
        ]
        
        self.encouragements = [
            "You're doing great!",
            "Keep up the momentum!",
            "Almost there!",
            "Your streak is impressive!",
            "Learning at your own pace is key!"
        ]
    
    def suggest_next_step(self, progress_data: Dict) -> Dict:
        """
        Generate intelligent next step recommendations
        based on student's current state
        """
        
        suggestion = {
            "action": "",
            "reason": "",
            "estimated_time": "",
            "encouragement": ""
        }
        if progress_data['pending_count'] > 0:
            next_topic = progress_data['next_topic']
            is_advanced = any(
                topic.get('difficulty') == 'Advanced' 
                for topic in progress_data['pending_topics']
                if topic['name'] == next_topic
            )
            
            if is_advanced:
                suggestion["action"] = f"Deep Dive: Master {next_topic}"
                suggestion["reason"] = "This advanced topic is crucial for your career path"
                suggestion["estimated_time"] = "2-3 hours"
            else:
                suggestion["action"] = f"Study Session: Complete {next_topic}"
                suggestion["reason"] = "This is your next milestone in the learning path"
                suggestion["estimated_time"] = "1-2 hours"

        elif progress_data['progress_percentage'] == 100:
            suggestion["action"] = "Practice Project: Build a real application"
            suggestion["reason"] = "You've mastered the concepts! Time to apply them"
            suggestion["estimated_time"] = "4-6 hours"

        elif progress_data['progress_percentage'] >= 80:
            remaining = progress_data['pending_count']
            suggestion["action"] = "Final Push: Review and practice"
            suggestion["reason"] = f"Just {remaining} more topic(s) to complete this phase!"
            suggestion["estimated_time"] = "1-2 hours"

        elif progress_data['streak_days'] < 3:
            suggestion["action"] = "Quick Win: Review your favorite completed topic"
            suggestion["reason"] = "Let's rebuild your learning momentum"
            suggestion["estimated_time"] = "30 minutes"

        else:
            random_practice = random.choice(self.practice_ideas)
            completed_topics = progress_data['completed_topics']
            if completed_topics:
                topic = random.choice(completed_topics)['name']
                suggestion["action"] = f"{random_practice} {topic}"
            else:
                suggestion["action"] = "Start with your first topic"
            suggestion["reason"] = "Practice reinforces learning"
            suggestion["estimated_time"] = "45 minutes"
        suggestion["encouragement"] = random.choice(self.encouragements)
        suggestion["tip"] = self._get_study_tip(progress_data)
        
        return suggestion
    
    def _get_study_tip(self, progress_data: Dict) -> str:
        
        tips = [
            "Tip: Take a 5-minute break every 25 minutes (Pomodoro technique)",
            "Tip: Active recall > Passive reading. Test yourself!",
            "Tip: Join a study group or find a learning buddy",
            "Tip: Use multiple resources (videos, docs, practice)",
            "Tip: Write down key concepts in your own words"
        ]
        
        if progress_data['streak_days'] > 7:
            tips.append("Tip: You're on fire! Consider increasing your daily goal")
        elif progress_data['pending_count'] > 5:
            tips.append("Tip: Break down large topics into smaller chunks")
        
        return random.choice(tips)
    
    def format_suggestion(self, suggestion: Dict) -> str:
        """Format suggestion in a beautiful, motivational way"""
        
        return f"""
╔══════════════════════════════════════════════════════════╗
║                      YOUR NEXT STEP                      ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║  {suggestion['action']}                                  ║
║                                                          ║
║     Why? {suggestion['reason']}                          ║
║                                                          ║
║  Estimated: {suggestion['estimated_time']}               ║
║                                                          ║
║   {suggestion['encouragement']}                          ║
║                                                          ║
║  {suggestion['tip']}                                     ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
"""