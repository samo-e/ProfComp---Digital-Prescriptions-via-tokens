#!/usr/bin/env python3
"""
Script to reset migration state and fix studentnumber column
"""

from website import create_app
from website.models import db, User
import sqlite3
import os

def reset_migrations_and_fix_column():
    app = create_app()
    
    with app.app_context():
        # Get the database path
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        if not os.path.isabs(db_path):
            db_path = os.path.join(app.instance_path, db_path)
        
        print(f"Working with database: {db_path}")
        
        # Connect directly to SQLite
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            # Check if alembic_version table exists and clear it
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='alembic_version'")
            if cursor.fetchone():
                cursor.execute("DELETE FROM alembic_version")
                print("Cleared alembic version table")
            
            # Check if studentnumber column exists
            cursor.execute("PRAGMA table_info(users)")
            columns = [row[1] for row in cursor.fetchall()]
            
            if 'studentnumber' not in columns:
                print("Adding studentnumber column...")
                cursor.execute("ALTER TABLE users ADD COLUMN studentnumber INTEGER")
                print("Added studentnumber column")
            else:
                print("studentnumber column already exists")
            
            conn.commit()
            
        except Exception as e:
            print(f"Error: {e}")
            conn.rollback()
        finally:
            conn.close()
        
        print("Database schema updated successfully!")
        
        # Now test if we can query users
        try:
            users = User.query.all()
            print(f"Found {len(users)} users in database")
            for user in users:
                print(f"  {user.email}: Student Number = {getattr(user, 'studentnumber', 'N/A')}")
        except Exception as e:
            print(f"Error querying users: {e}")

if __name__ == "__main__":
    reset_migrations_and_fix_column()