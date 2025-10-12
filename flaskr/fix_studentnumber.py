#!/usr/bin/env python3
"""
Script to fix the studentnumber column and add sample student numbers
"""

from website import create_app
from website.models import db, User
import random


def fix_studentnumber_column():
    app = create_app()

    with app.app_context():
        try:
            # Try to add the studentnumber column if it doesn't exist
            db.engine.execute("ALTER TABLE users ADD COLUMN studentnumber INTEGER")
            print("Added studentnumber column to database")
        except Exception as e:
            print(f"Column might already exist: {e}")

        # Get all users without student numbers
        users_without_numbers = User.query.filter(User.studentnumber.is_(None)).all()

        print(f"Found {len(users_without_numbers)} users without student numbers")

        # Assign random student numbers to users without them
        used_numbers = set()
        existing_numbers = [
            u.studentnumber
            for u in User.query.filter(User.studentnumber.isnot(None)).all()
        ]
        used_numbers.update(existing_numbers)

        for user in users_without_numbers:
            # Generate a unique 8-digit student number
            while True:
                student_number = random.randint(10000000, 99999999)
                if student_number not in used_numbers:
                    used_numbers.add(student_number)
                    break

            user.studentnumber = student_number
            print(f"Assigned student number {student_number} to {user.email}")

        db.session.commit()
        print("Student numbers assigned successfully!")

        # Verify the changes
        all_users = User.query.all()
        for user in all_users:
            print(f"{user.email}: Student Number = {user.studentnumber}")


if __name__ == "__main__":
    fix_studentnumber_column()
