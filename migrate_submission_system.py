#!/usr/bin/env python3
"""
Database migration script to add submission system fields to existing database.
Run this script to update your database schema for the submission and grading system.
"""

import sqlite3
import os
from datetime import datetime


def migrate_database():
    """Add new columns for the submission system to existing database"""

    # Path to the database
    db_path = os.path.join("flaskr", "instance", "asl_simulation.db")

    if not os.path.exists(db_path):
        # print(f"Database not found at {db_path}")
        # print("Make sure you're running this from the project root directory.")
        return False

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # print("Starting database migration for submission system...")

        # Check if student_scenarios table exists
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='student_scenarios';"
        )
        if not cursor.fetchone():
            # print("student_scenarios table not found. Creating tables...")
            create_missing_tables(cursor)
        else:
            # print("student_scenarios table found. Adding missing columns...")
            add_missing_columns(cursor)

        # Check if submissions table exists
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='submissions';"
        )
        if not cursor.fetchone():
            # print("Creating submissions table...")
            cursor.execute(
                """
                CREATE TABLE submissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_scenario_id INTEGER NOT NULL,
                    patient_id INTEGER NOT NULL,
                    submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    submission_data TEXT,
                    notes TEXT,
                    FOREIGN KEY (student_scenario_id) REFERENCES student_scenarios (id),
                    FOREIGN KEY (patient_id) REFERENCES patients (id)
                )
            """
            )
            # print("submissions table created")

        conn.commit()
        # print("Database migration completed successfully!")
        return True

    except sqlite3.Error as e:
        # print(f"Database error: {e}")
        return False
    except Exception as e:
        # print(f"Unexpected error: {e}")
        return False
    finally:
        if conn:
            conn.close()


def add_missing_columns(cursor):
    """Add missing columns to existing student_scenarios table"""

    # Get current columns
    cursor.execute("PRAGMA table_info(student_scenarios)")
    existing_columns = [row[1] for row in cursor.fetchall()]
    # print(f"Existing columns: {existing_columns}")

    # Add missing columns one by one
    columns_to_add = [
        ("submitted_at", "DATETIME"),
        ("feedback", "TEXT"),
        ("status", "VARCHAR(20) DEFAULT 'assigned'"),
    ]

    for column_name, column_type in columns_to_add:
        if column_name not in existing_columns:
            try:
                cursor.execute(
                    f"ALTER TABLE student_scenarios ADD COLUMN {column_name} {column_type}"
                )
                # print(f"Added column: {column_name}")
            except sqlite3.Error as e:
                pass
                # print(f" Could not add {column_name}: {e}")
        else:
            pass
            # print(f"Column {column_name} already exists")


def create_missing_tables(cursor):
    """Create missing tables if they don't exist"""

    # Create student_scenarios table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS student_scenarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            scenario_id INTEGER NOT NULL,
            assigned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            submitted_at DATETIME,
            completed_at DATETIME,
            score REAL,
            feedback TEXT,
            status VARCHAR(20) DEFAULT 'assigned',
            FOREIGN KEY (student_id) REFERENCES users (id),
            FOREIGN KEY (scenario_id) REFERENCES scenarios (id)
        )
    """
    )
    # print("student_scenarios table created")

    # Create scenario_patients table if it doesn't exist
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS scenario_patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scenario_id INTEGER NOT NULL,
            student_id INTEGER,
            patient_id INTEGER NOT NULL,
            assigned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (scenario_id) REFERENCES scenarios (id),
            FOREIGN KEY (student_id) REFERENCES users (id),
            FOREIGN KEY (patient_id) REFERENCES patients (id)
        )
    """
    )
    # print("scenario_patients table created")


def verify_migration(cursor):
    """Verify the migration was successful"""
    try:
        # Test the problematic query from the error
        cursor.execute("SELECT submitted_at FROM student_scenarios LIMIT 1")
        # print("submitted_at column is accessible")
        return True
    except sqlite3.Error as e:
        # print(f"Migration verification failed: {e}")
        return False


if __name__ == "__main__":
    # print("Database Migration Tool for Submission System")
    # print("=" * 50)

    success = migrate_database()

    # if success:
        # print("\nMigration completed! You can now:")
        # print("1. Restart your Flask application")
        # print("2. Test the submission system")
        # print("3. Students can submit work and teachers can grade it")
    # else:
        # print("\nMigration failed. Please check the errors above.")
        # print("You may need to:")
        # print("1. Check database permissions")
        # print("2. Ensure Flask app is not running")
        # print("3. Run this script from the project root directory")
