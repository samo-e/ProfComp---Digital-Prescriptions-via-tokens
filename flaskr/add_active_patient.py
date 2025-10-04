import sqlite3
import os

# Path to the database
db_path = os.path.join(os.path.dirname(__file__), 'instance', 'asl_simulation.db')

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Check if active_patient_id column already exists
    cursor.execute("PRAGMA table_info(scenarios)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if 'active_patient_id' not in columns:
        # Add the active_patient_id column to scenarios table
        cursor.execute('ALTER TABLE scenarios ADD COLUMN active_patient_id INTEGER REFERENCES patients(id)')
        print("Added active_patient_id column to scenarios table")
    else:
        print("active_patient_id column already exists in scenarios table")
    
    # Commit the changes
    conn.commit()
    print("Database updated successfully!")
    
except Exception as e:
    print(f"Error updating database: {e}")
    conn.rollback()
    
finally:
    conn.close()