import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

def get_db_connection():
    conn = sqlite3.connect('intervio.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    # Users table (Standard Creation)
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            resume_path TEXT,
            readiness_percent INTEGER DEFAULT 0
        )
    ''')
    
    # Schema Migration for Users: Ensure columns exist
    for col_name, col_type in [("resume_path", "TEXT"), ("readiness_percent", "INTEGER DEFAULT 0")]:
        try:
            c.execute(f'SELECT {col_name} FROM users LIMIT 1')
        except sqlite3.OperationalError:
            try:
                c.execute(f'ALTER TABLE users ADD COLUMN {col_name} {col_type}')
            except:
                pass
    
    # Premium Recruiter Tables (Stable Creation)
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recruiter_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            role TEXT,
            image_url TEXT,
            score_tech INTEGER,
            score_comm INTEGER,
            score_conf INTEGER,
            insight TEXT,
            summary TEXT,
            tags TEXT, 
            status TEXT, 
            FOREIGN KEY (recruiter_id) REFERENCES users (id)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS interviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id INTEGER NOT NULL,
            recruiter_id INTEGER NOT NULL,
            date TEXT,
            type TEXT, 
            score INTEGER,
            conf_score INTEGER,
            comm_score INTEGER,
            tech_score INTEGER,
            summary TEXT,
            rubric_json TEXT, 
            star_feedback TEXT,
            filler_word_count INTEGER,
            speech_clarity TEXT,
            FOREIGN KEY (candidate_id) REFERENCES candidates (id),
            FOREIGN KEY (recruiter_id) REFERENCES users (id)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS ai_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recruiter_id INTEGER NOT NULL,
            type TEXT, 
            title TEXT,
            message TEXT,
            timestamp TEXT,
            FOREIGN KEY (recruiter_id) REFERENCES users (id)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS sourcing_agents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recruiter_id INTEGER NOT NULL,
            query TEXT,
            results_count INTEGER,
            status TEXT, 
            FOREIGN KEY (recruiter_id) REFERENCES users (id)
        )
    ''')
    
    # NEW: Mock Interview Modes
    c.execute('''
        CREATE TABLE IF NOT EXISTS mock_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            mode TEXT, -- 'Technical', 'Behavioral', 'HR'
            score INTEGER,
            date TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def create_user(name, email, password_hash):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)',
              (name, email, password_hash))
    user_id = c.lastrowid
    conn.commit()
    conn.close()
    return user_id

def get_user_by_email(email):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    conn.close()
    return user

def get_user_by_id(user_id):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return user

def get_candidates(recruiter_id):
    conn = get_db_connection()
    candidates = conn.execute('SELECT * FROM candidates WHERE recruiter_id = ? ORDER BY score_tech DESC', (recruiter_id,)).fetchall()
    conn.close()
    return candidates

def get_ai_logs(recruiter_id):
    conn = get_db_connection()
    logs = conn.execute('SELECT * FROM ai_logs WHERE recruiter_id = ? ORDER BY id DESC LIMIT 10', (recruiter_id,)).fetchall()
    conn.close()
    return logs

def get_interview_pulse(recruiter_id):
    conn = get_db_connection()
    pulse = conn.execute('SELECT * FROM interviews WHERE recruiter_id = ? ORDER BY id DESC LIMIT 5', (recruiter_id,)).fetchall()
    conn.close()
    return pulse

def get_mock_sessions(user_id):
    conn = get_db_connection()
    sessions = conn.execute('SELECT * FROM mock_sessions WHERE user_id = ? ORDER BY date DESC LIMIT 5', (user_id,)).fetchall()
    conn.close()
    return [dict(row) for row in sessions]

def get_user_stats(user_id):
    conn = get_db_connection()
    # Fetch averages from interviews (more granular) and mock_sessions
    stats = conn.execute('''
        SELECT 
            AVG(tech_score) as avg_tech,
            AVG(comm_score) as avg_comm,
            AVG(conf_score) as avg_conf
        FROM interviews 
        WHERE recruiter_id = ?
    ''', (user_id,)).fetchone()
    
    # Fallback to mock_sessions if interviews is empty (or blend them)
    if not stats or stats['avg_tech'] is None:
        mock_stats = conn.execute('SELECT AVG(score) as avg_score FROM mock_sessions WHERE user_id = ?', (user_id,)).fetchone()
        avg = mock_stats['avg_score'] if mock_stats and mock_stats['avg_score'] else 0
        stats = {'avg_tech': avg, 'avg_comm': avg * 0.95, 'avg_conf': avg * 0.9}
        
    conn.close()
    return {
        'tech': int(stats['avg_tech'] or 0),
        'comm': int(stats['avg_comm'] or 0),
        'conf': int(stats['avg_conf'] or 0)
    }

def get_performance_history(user_id):
    conn = get_db_connection()
    # Get last 7 scores for the graph
    sessions = conn.execute('''
        SELECT score, date FROM mock_sessions WHERE user_id = ? 
        UNION ALL 
        SELECT score, date FROM interviews WHERE recruiter_id = ?
        ORDER BY date ASC LIMIT 10
    ''', (user_id, user_id)).fetchall()
    conn.close()
    return [dict(row) for row in sessions]

def get_latest_interview(user_id):
    conn = get_db_connection()
    interview = conn.execute('SELECT * FROM interviews WHERE recruiter_id = ? ORDER BY id DESC LIMIT 1', (user_id,)).fetchone()
    conn.close()
    return interview

def get_interview_by_id(interview_id):
    conn = get_db_connection()
    interview = conn.execute('SELECT * FROM interviews WHERE id = ?', (interview_id,)).fetchone()
    conn.close()
    return interview

def save_interview(user_id, data):
    conn = get_db_connection()
    c = conn.cursor()
    # Create a dummy candidate if needed or use a default
    c.execute('INSERT INTO candidates (recruiter_id, name, role, status) VALUES (?, ?, ?, ?)',
              (user_id, user_id, 'Self-Practice', 'Completed'))
    candidate_id = c.lastrowid
    
    c.execute('''INSERT INTO interviews 
        (candidate_id, recruiter_id, date, type, score, conf_score, comm_score, tech_score, summary, rubric_json, star_feedback, filler_word_count, speech_clarity) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (candidate_id, user_id, data['date'], data['type'], data['score'], data['conf'], data['comm'], data['tech'], 
               data['summary'], data['rubric'], data['star'], data['fillers'], data['clarity']))
    conn.commit()
    conn.close()

def seed_super_dashboard(recruiter_id):
    conn = get_db_connection()
    c = conn.cursor()
    
    # Safety Check: Don't seed if user already has real history
    existing = c.execute('SELECT COUNT(*) FROM mock_sessions WHERE user_id = ?', (recruiter_id,)).fetchone()[0]
    if existing > 0:
        # Just update readiness if it's 0
        c.execute('UPDATE users SET readiness_percent = 85 WHERE id = ? AND readiness_percent = 0', (recruiter_id,))
        conn.commit()
        conn.close()
        return

    # Update user readiness
    c.execute('UPDATE users SET readiness_percent = 85, resume_path = "resume_anas.pdf" WHERE id = ?', (recruiter_id,))
    
    # Mock Candidates with Super Scores
    candidates = [
        ('Alex Chen', 'Senior SWE', 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=400&q=80', 92, 88, 94, 'High narrative flow', 'Architectural specialist with 8 years exp.', 'React,Node,Cloud', 'Vetted'),
        ('Elena Rodriguez', 'Product Lead', 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=400&q=80', 85, 95, 89, 'Strong cultural markers', 'Collaborative expert in Agile workflows.', 'Product,Strategy,Leadership', 'Applied'),
        ('Jordan Smith', 'DevOps Eng', 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?auto=format&fit=crop&w=400&q=80', 88, 82, 91, 'Bias-reduced high performer', 'Infrastructure-as-code veteran.', 'AWS,Terraform,K8s', 'Offer')
    ]
    for cand in candidates:
        c.execute('INSERT INTO candidates (recruiter_id, name, role, image_url, score_tech, score_comm, score_conf, insight, summary, tags, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                  (recruiter_id, *cand))
    
    # Mock Interviews (Super Pulse + STAR Method)
    interviews = [
        (1, 'Feb 26', 'Technical', 94, 92, 88, 94, 'Deep-dive success.', '{"Logic": 98, "Star": 94}', 'Great STAR usage. Improved system design clarity.', 12, 'Clear'),
        (2, 'Feb 26', 'EQ Round', 88, 95, 82, 88, 'Strong empathy.', '{"Empathy": 95, "Comm": 82}', 'Communicated conflict resolution effectively.', 4, 'Highly Clear'),
        (1, 'Feb 25', 'Culture Fit', 90, 86, 94, 90, 'Highly recommended.', '{"Vision": 94, "Value": 86}', 'Alignment with core company vision is 98%.', 8, 'Normal')
    ]
    for i, (cand_id, date, type, score, conf, comm, tech, summary, rubric, star, fillers, speech) in enumerate(interviews):
        c.execute('''INSERT INTO interviews 
            (candidate_id, recruiter_id, date, type, score, conf_score, comm_score, tech_score, summary, rubric_json, star_feedback, filler_word_count, speech_clarity) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (i+1, recruiter_id, date, type, score, conf, comm, tech, summary, rubric, star, fillers, speech))

    # Mock AI Logs (Advanced)
    logs = [
        ('sourcing', 'Discovery Agent Active', 'Scanning 100M+ profiles for Senior SWEs...', '14:20'),
        ('scoring', 'Technical Analysis Complete', 'Alex Chen scored 94% on System Design.', '14:45'),
        ('audit', 'Anti-Cheat Triggered', 'Trust score verified at 99.2% for local candidate.', '15:10'),
        ('sourcing', 'Shortlisting Complete', 'Built target list of 12 React Developers.', '15:30')
    ]
    for ltype, title, msg, ts in logs:
        c.execute('INSERT INTO ai_logs (recruiter_id, type, title, message, timestamp) VALUES (?, ?, ?, ?, ?)',
                  (recruiter_id, ltype, title, msg, ts))
                  
    # Mock Sessions
    sessions = [
        (recruiter_id, 'Technical', 94, 'Feb 26'),
        (recruiter_id, 'Behavioral', 88, 'Feb 26'),
        (recruiter_id, 'HR Round', 90, 'Feb 25')
    ]
    for user_id, mode, score, date in sessions:
        c.execute('INSERT INTO mock_sessions (user_id, mode, score, date) VALUES (?, ?, ?, ?)', (user_id, mode, score, date))

    conn.commit()
    conn.close()
