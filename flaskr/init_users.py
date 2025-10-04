"""
Script to initialize test users in the database
Run this after init_data.py to add teacher and student accounts
"""


def init_users():
    """Initialize test users for the application"""
    from website import create_app
    from website.models import db, User, UserRole

    app = create_app()
    with app.app_context():
        # Check if users already exist
        existing_users = User.query.all()
        if existing_users:
            print(
                f"Users already exist in database ({len(existing_users)} users found)"
            )
            response = input(
                "Do you want to delete existing users and create new ones? (y/n): "
            )
            if response.lower() != "y":
                print("Skipping user creation")
                return
            else:
                # Delete existing users
                User.query.delete()
                db.session.commit()
                print("Existing users deleted")

        # Create test users
        test_users = [
            # Teachers
            {
                "email": "teacher1@test.com",
                "password": "teacher123",
                "role": "teacher",
                "first_name": "Sarah",
                "last_name": "Johnson",
            },
            {
                "email": "teacher2@test.com",
                "password": "teacher123",
                "role": "teacher",
                "first_name": "Michael",
                "last_name": "Brown",
            },
            # Students
            {
                "email": "student1@test.com",
                "password": "student123",
                "role": "student",
                "first_name": "Emily",
                "last_name": "Davis",
            },
            {
                "email": "student2@test.com",
                "password": "student123",
                "role": "student",
                "first_name": "James",
                "last_name": "Wilson",
            },
            {
                "email": "student3@test.com",
                "password": "student123",
                "role": "student",
                "first_name": "Olivia",
                "last_name": "Martinez",
            },
            # Admin teacher
            {
                "email": "admin@test.com",
                "password": "admin123",
                "role": "teacher",
                "first_name": "Admin",
                "last_name": "User",
            },
        ]

        created_users = []
        for user_data in test_users:
            user = User(
                email=user_data["email"],
                role=user_data["role"],
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
            )
            user.set_password(user_data["password"])
            db.session.add(user)
            created_users.append(user)
            print(
                f"Created {user_data['role']}: {user_data['email']} (password: {user_data['password']})"
            )

        db.session.commit()

        print("\n" + "=" * 50)
        print("Test users created successfully!")
        print("=" * 50)
        print("\nTeacher accounts:")
        print("  - teacher1@test.com / teacher123")
        print("  - teacher2@test.com / teacher123")
        print("  - admin@test.com / admin123 (admin teacher)")
        print("\nStudent accounts:")
        print("  - student1@test.com / student123")
        print("  - student2@test.com / student123")
        print("  - student3@test.com / student123")
        print("\nYou can now login with any of these accounts.")
        print("=" * 50)


if __name__ == "__main__":
    init_users()
