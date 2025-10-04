import sqlite3
import os

# Path to the database
db_path = os.path.join(os.path.dirname(__file__), "instance", "asl_simulation.db")

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Check if question_text column already exists
    cursor.execute("PRAGMA table_info(scenarios)")
    columns = [row[1] for row in cursor.fetchall()]

    if "question_text" not in columns:
        # Add the question_text column to scenarios table
        cursor.execute("ALTER TABLE scenarios ADD COLUMN question_text TEXT")
        # print("Added question_text column to scenarios table")
    else:
        pass
        # print("question_text column already exists in scenarios table")

    # Check if scenario_questions table exists (it might need to be dropped)
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='scenario_questions'"
    )
    # if cursor.fetchone():
        # print(
        #     "scenario_questions table still exists (you might want to migrate data first)"
        # )
    # else:
        # print("scenario_questions table does not exist")

    # Commit the changes
    conn.commit()
    # print("Database updated successfully!")

except Exception as e:
    # print(f"Error updating database: {e}")
    conn.rollback()

finally:
    conn.close()
