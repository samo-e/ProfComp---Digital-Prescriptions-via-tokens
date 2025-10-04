#!/usr/bin/env python3
"""
Database migration script to add student_id and assigned_at columns to scenario_patients table
"""

import sqlite3
import os
from datetime import datetime

# Path to the database file
DB_PATH = os.path.join(
    os.path.dirname(__file__), "flaskr", "instance", "asl_simulation.db"
)


def migrate_database():
    # print(f"Migrating database at: {DB_PATH}")

    # Connect to the database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Check if student_id column exists
        cursor.execute("PRAGMA table_info(scenario_patients)")
        columns = [column[1] for column in cursor.fetchall()]

        if "student_id" not in columns:
            # print("Adding student_id column to scenario_patients table...")
            cursor.execute(
                "ALTER TABLE scenario_patients ADD COLUMN student_id INTEGER"
            )
            # print("✓ student_id column added")
        else:
            pass
            # print("✓ student_id column already exists")

        if "assigned_at" not in columns:
            # print("Adding assigned_at column to scenario_patients table...")
            cursor.execute(
                "ALTER TABLE scenario_patients ADD COLUMN assigned_at DATETIME"
            )
            # print("✓ assigned_at column added")
        else:
            pass
            # print("✓ assigned_at column already exists")

        # Commit the changes
        conn.commit()
        # print("✅ Database migration completed successfully!")

    except Exception as e:
        # print(f"❌ Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()


if __name__ == "__main__":
    migrate_database()
