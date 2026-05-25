"""
Database Setup Script
Creates and initializes the SQLite database with sample student data
"""

import sqlite3
import os
from datetime import datetime
DB_PATH = "database/learning.db"
os.makedirs("database", exist_ok=True)

def create_database():
    """Create database tables and insert sample data"""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS students")
    cursor.execute("DROP TABLE IF EXISTS topics")
    cursor.execute("DROP TABLE IF EXISTS learning_sessions")
    cursor.execute("""
        CREATE TABLE students (
            user_id TEXT PRIMARY KEY,
            full_name TEXT,
            target_role TEXT,
            current_phase TEXT,
            daily_streak INTEGER,
            total_hours_spent REAL,
            joined_date DATE,
            last_active TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            topic_name TEXT,
            topic_status TEXT,
            difficulty_level TEXT,
            time_spent_hours REAL,
            FOREIGN KEY(user_id) REFERENCES students(user_id)
        )
    """)
    cursor.execute("""
        CREATE TABLE learning_sessions (
            session_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            query TEXT,
            response TEXT,
            timestamp TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES students(user_id)
        )
    """)
    cursor.execute("""
        INSERT INTO students VALUES (
            'user_123', 
            'Alex Johnson', 
            'Frontend Developer', 
            'JavaScript Basics', 
            5, 
            24.5, 
            '2026-01-15', 
            CURRENT_TIMESTAMP
        )
    """)
    topics_data = [
        ('user_123', 'Variables', 'completed', 'Beginner', 2.5),
        ('user_123', 'Data Types', 'completed', 'Beginner', 1.5),
        ('user_123', 'Loops', 'completed', 'Beginner', 3.0),
        ('user_123', 'Functions', 'completed', 'Intermediate', 4.0),
        ('user_123', 'Promises', 'pending', 'Advanced', 0),
        ('user_123', 'Async/Await', 'pending', 'Advanced', 0),
        ('user_123', 'Error Handling', 'pending', 'Intermediate', 0),
    ]
    
    cursor.executemany("""
        INSERT INTO topics (user_id, topic_name, topic_status, difficulty_level, time_spent_hours)
        VALUES (?, ?, ?, ?, ?)
    """, topics_data)
    
    conn.commit()
    conn.close()
    
    print("✅ Database created successfully!")
    print(f"Location: {DB_PATH}")
    print("\nSample Data:")
    print("Student: Alex Johnson")
    print("Target: Frontend Developer")
    print("Phase: JavaScript Basics")
    print("Completed: 4 topics")
    print("Pending: 3 topics")

if __name__ == "__main__":
    create_database()