# File: models/database.py
# Database models and operations for SQLite

import sqlite3
import json
from datetime import datetime
from config.settings import DATABASE_PATH

def init_database():
    """Initialize SQLite database for storing leads and audit results"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            url TEXT NOT NULL,
            overall_score INTEGER,
            technical_score INTEGER,
            content_score INTEGER,
            performance_score INTEGER,
            accessibility_score INTEGER,
            audit_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def save_audit_data(email: str, url: str, audit_data: dict):
    """Save audit data to database"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO audits (email, url, overall_score, technical_score, content_score, 
                          performance_score, accessibility_score, audit_data)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        email,
        url,
        audit_data.get('overall_score', 0),
        audit_data.get('category_scores', {}).get('technical_seo', 0),
        audit_data.get('category_scores', {}).get('content_quality', 0),
        audit_data.get('category_scores', {}).get('ai_readiness', 0),
        audit_data.get('category_scores', {}).get('voice_search', 0),
        json.dumps(audit_data)
    ))
    
    conn.commit()
    conn.close()