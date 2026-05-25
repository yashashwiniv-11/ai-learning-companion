"""
Database Setup Script with Enhanced SQLite Schema
Version: 3.0 - Optimized for AI Learning Companion
"""

import sqlite3
import os
from datetime import datetime
import hashlib

DB_PATH = "database/learning.db"
BACKUP_PATH = "database/learning.db.backup"

def create_database():
    """Create database with optimized schema and indexes"""

    os.makedirs("database", exist_ok=True)

    if os.path.exists(DB_PATH):
        print("Existing database found. Creating backup...")
        import shutil
        shutil.copy2(DB_PATH, f"{BACKUP_PATH}.{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        print(f"✅ Backup created")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
 
    cursor.execute("PRAGMA foreign_keys = ON;")
    cursor.execute("PRAGMA journal_mode = WAL;")
    cursor.execute("PRAGMA synchronous = NORMAL;")
    cursor.execute("PRAGMA cache_size = -2000;") 

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            user_id TEXT PRIMARY KEY,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE,
            target_role TEXT NOT NULL,
            current_phase TEXT NOT NULL,
            daily_streak INTEGER DEFAULT 0,
            total_hours_spent REAL DEFAULT 0,
            joined_date DATE DEFAULT CURRENT_DATE,
            last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            preferred_learning_style TEXT DEFAULT 'visual',
            difficulty_level TEXT DEFAULT 'intermediate',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            topic_name TEXT NOT NULL,
            topic_status TEXT CHECK(topic_status IN ('completed', 'pending', 'in_progress', 'review')) DEFAULT 'pending',
            difficulty_level TEXT CHECK(difficulty_level IN ('beginner', 'intermediate', 'advanced')) DEFAULT 'beginner',
            priority INTEGER DEFAULT 1,
            time_spent_hours REAL DEFAULT 0,
            completed_date DATE,
            attempts INTEGER DEFAULT 0,
            quiz_score REAL,
            notes TEXT,
            resources TEXT,
            order_index INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES students(user_id) ON DELETE CASCADE,
            UNIQUE(user_id, topic_name)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS learning_sessions (
            session_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            query TEXT NOT NULL,
            response TEXT NOT NULL,
            intent TEXT,
            sentiment REAL,
            response_time_ms INTEGER,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES students(user_id) ON DELETE CASCADE
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_activity (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            activity_date DATE NOT NULL,
            minutes_spent INTEGER DEFAULT 0,
            topics_reviewed INTEGER DEFAULT 0,
            quizzes_taken INTEGER DEFAULT 0,
            streak_continued BOOLEAN DEFAULT FALSE,
            notes TEXT,
            FOREIGN KEY(user_id) REFERENCES students(user_id) ON DELETE CASCADE,
            UNIQUE(user_id, activity_date)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            achievement_name TEXT NOT NULL,
            achievement_type TEXT CHECK(achievement_type IN ('streak', 'completion', 'speed', 'consistency')),
            earned_date DATE DEFAULT CURRENT_DATE,
            points INTEGER DEFAULT 0,
            FOREIGN KEY(user_id) REFERENCES students(user_id) ON DELETE CASCADE
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS learning_path (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role_title TEXT NOT NULL,
            phase_name TEXT NOT NULL,
            phase_order INTEGER DEFAULT 0,
            topics JSON,
            estimated_hours REAL,
            prerequisites TEXT,
            UNIQUE(role_title, phase_name)
        )
    """)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_students_email ON students(email);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_students_target ON students(target_role);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_students_streak ON students(daily_streak);")
 
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_topics_user_status ON topics(user_id, topic_status);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_topics_difficulty ON topics(difficulty_level);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_topics_priority ON topics(priority);")

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_user_time ON learning_sessions(user_id, timestamp);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_intent ON learning_sessions(intent);")

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_activity_user_date ON daily_activity(user_id, activity_date);")

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_achievements_user ON achievements(user_id);")

    cursor.execute("""
        INSERT OR REPLACE INTO students (
            user_id, full_name, email, target_role, current_phase, 
            daily_streak, total_hours_spent, joined_date, last_active,
            preferred_learning_style, difficulty_level
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        'user_123', 
        'Alex Johnson', 
        'alex.johnson@example.com',
        'Frontend Developer', 
        'JavaScript Basics', 
        5, 
        24.5, 
        '2026-01-15', 
        datetime.now().isoformat(),
        'visual',
        'intermediate'
    ))
    topics_data = [
        ('user_123', 'Variables', 'completed', 'beginner', 1, 2.5, '2026-01-20', 2, 85.0, 'Understanding data storage', 'MDN Docs'),
        ('user_123', 'Data Types', 'completed', 'beginner', 1, 1.5, '2026-01-22', 1, 90.0, 'Strings, numbers, booleans', 'W3Schools'),
        ('user_123', 'Loops', 'completed', 'beginner', 1, 3.0, '2026-01-25', 3, 75.0, 'For, while, do-while', 'YouTube tutorials'),
        ('user_123', 'Functions', 'completed', 'intermediate', 1, 4.0, '2026-01-28', 2, 88.0, 'Declarations, expressions, arrow functions', 'FreeCodeCamp'),
        ('user_123', 'Promises', 'pending', 'advanced', 2, 0, None, 0, 0.0, 'Async operations', 'MDN Web Docs'),
        ('user_123', 'Async/Await', 'pending', 'advanced', 2, 0, None, 0, 0.0, 'Modern async patterns', 'JavaScript.info'),
        ('user_123', 'Error Handling', 'pending', 'intermediate', 1, 0, None, 0, 0.0, 'Try-catch, error objects', 'Stack Overflow'),
    ]
    
    for topic in topics_data:
        cursor.execute("""
            INSERT OR REPLACE INTO topics (
                user_id, topic_name, topic_status, difficulty_level, priority,
                time_spent_hours, completed_date, attempts, quiz_score, notes, resources
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, topic)
    cursor.execute("""
        INSERT OR REPLACE INTO daily_activity (user_id, activity_date, minutes_spent, topics_reviewed, streak_continued)
        VALUES (?, ?, ?, ?, ?)
    """, ('user_123', date.today().isoformat(), 90, 2, True))
    learning_paths = [
        ('Frontend Developer', 'HTML/CSS Basics', 1, '["HTML Tags", "CSS Selectors", "Flexbox"]', 10.0, None),
        ('Frontend Developer', 'JavaScript Basics', 2, '["Variables", "Functions", "DOM"]', 15.0, 'HTML/CSS Basics'),
        ('Frontend Developer', 'React Fundamentals', 3, '["Components", "Props", "State", "Hooks"]', 20.0, 'JavaScript Basics'),
        ('Frontend Developer', 'Advanced React', 4, '["Context API", "Redux", "Performance"]', 15.0, 'React Fundamentals'),
    ]
    
    for path in learning_paths:
        cursor.execute("""
            INSERT OR REPLACE INTO learning_path (role_title, phase_name, phase_order, topics, estimated_hours, prerequisites)
            VALUES (?, ?, ?, ?, ?, ?)
        """, path)
    cursor.execute("""
        CREATE VIEW IF NOT EXISTS v_student_progress AS
        SELECT 
            s.user_id,
            s.full_name,
            s.target_role,
            s.current_phase,
            s.daily_streak,
            s.total_hours_spent,
            COUNT(CASE WHEN t.topic_status = 'completed' THEN 1 END) as completed_topics,
            COUNT(CASE WHEN t.topic_status = 'pending' THEN 1 END) as pending_topics,
            ROUND(100.0 * COUNT(CASE WHEN t.topic_status = 'completed' THEN 1 END) / COUNT(*), 1) as completion_percentage
        FROM students s
        LEFT JOIN topics t ON s.user_id = t.user_id
        GROUP BY s.user_id
    """)
    cursor.execute("""
        CREATE VIEW IF NOT EXISTS v_recent_activity AS
        SELECT 
            user_id,
            DATE(timestamp) as activity_date,
            COUNT(*) as queries_count,
            AVG(response_time_ms) as avg_response_time
        FROM learning_sessions
        WHERE timestamp >= DATE('now', '-7 days')
        GROUP BY user_id, DATE(timestamp)
    """)
    cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS update_streak
        AFTER INSERT ON daily_activity
        WHEN NEW.streak_continued = 1
        BEGIN
            UPDATE students 
            SET daily_streak = daily_streak + 1,
                updated_at = CURRENT_TIMESTAMP
            WHERE user_id = NEW.user_id;
        END
    """)
    cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS update_topic_completion
        AFTER UPDATE OF topic_status ON topics
        WHEN NEW.topic_status = 'completed' AND OLD.topic_status != 'completed'
        BEGIN
            UPDATE topics 
            SET completed_date = CURRENT_DATE,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = NEW.id;
        END
    """)
    conn.commit()
    
    cursor.execute("PRAGMA integrity_check;")
    integrity = cursor.fetchone()[0]
    
    if integrity == "ok":
        print("Database created successfully!")
        print(f"Location: {DB_PATH}")
        print(f"Size: {os.path.getsize(DB_PATH)} bytes")
        print("\nTables Created:")
        tables = ['students', 'topics', 'learning_sessions', 'daily_activity', 'achievements', 'learning_path']
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"   • {table}: {count} records")
        
        print("\nSample Student Data:")
        cursor.execute("SELECT user_id, full_name, target_role, daily_streak FROM students")
        for row in cursor.fetchall():
            print(f"   👤 {row[1]} ({row[0]}) - {row[2]} - {row[3]} day streak")
        
        print("\nTopic Distribution:")
        cursor.execute("""
            SELECT topic_status, difficulty_level, COUNT(*) 
            FROM topics 
            GROUP BY topic_status, difficulty_level
        """)
        for row in cursor.fetchall():
            print(f"   • {row[0]}: {row[1]} - {row[2]} topics")
    
    else:
        print(f"❌ Database integrity check failed: {integrity}")
    
    conn.close()

def get_db_info():
    """Get database information"""
    if not os.path.exists(DB_PATH):
        print("❌ Database not found. Run setup first.")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("\n" + "="*50)
    print("DATABASE INFORMATION")
    print("="*50)

    cursor.execute("SELECT sqlite_version();")
    version = cursor.fetchone()[0]
    print(f"\nSQLite Version: {version}")

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    tables = cursor.fetchall()
    
    print(f"\nTables ({len(tables)} total):")
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
        count = cursor.fetchone()[0]
        print(f"   • {table[0]}: {count} rows")

    size_bytes = os.path.getsize(DB_PATH)
    size_kb = size_bytes / 1024
    print(f"\nDatabase Size: {size_kb:.2f} KB")
    
    conn.close()

def repair_database():
    """Repair or recreate database"""
    if os.path.exists(DB_PATH):
        print("🔧 Attempting to repair database...")
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute("BEGIN IMMEDIATE;")
            conn.execute("PRAGMA integrity_check;")
            conn.commit()
            print("Database is healthy")
            conn.close()
        except sqlite3.Error as e:
            print(f"Database corrupted. Recreating...")
            os.remove(DB_PATH)
            create_database()

if __name__ == "__main__":
    from datetime import date
    
    print("🗄️ AI Learning Companion - Database Setup")
    print("="*50)
    if os.path.exists(DB_PATH):
        repair_database()
    else:
        create_database()
    get_db_info()
    
    print("\nDatabase setup complete!")
    print("You can now run: python main.py")