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
            # print(
            #     f"Users already exist in database ({len(existing_users)} users found)"
            # )
            response = input(
                "Do you want to delete existing users and create new ones? (y/n): "
            )
            if response.lower() != "y":
                # print("Skipping user creation")
                return
            else:
                # Delete existing users
                User.query.delete()
                db.session.commit()
                # print("Existing users deleted")

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
                "studentnumber": 24219288,
                "email": "student1@test.com",
                "password": "student123",
                "role": "student",
                "first_name": "Emily",
                "last_name": "Davis",
            },
            {
                "studentnumber": 21882973,
                "email": "student2@test.com",
                "password": "student123",
                "role": "student",
                "first_name": "James",
                "last_name": "Wilson",
            },
            {
                "studentnumber": 27842373,
                "email": "student3@test.com",
                "password": "student123",
                "role": "student",
                "first_name": "Olivia",
                "last_name": "Martinez",
            },
            {
                "studentnumber": 23456789,
                "email": "student4@test.com",
                "password": "student123",
                "role": "student",
                "first_name": "Alexander",
                "last_name": "Thompson",
            },
            {
                "studentnumber": 29871234,
                "email": "student5@test.com",
                "password": "student123",
                "role": "student",
                "first_name": "Sophia",
                "last_name": "Anderson",
            },
            {
                "studentnumber": 26543210,
                "email": "student6@test.com",
                "password": "student123",
                "role": "student",
                "first_name": "Benjamin",
                "last_name": "Garcia",
            },
            {
                "studentnumber": 28765432,
                "email": "student7@test.com",
                "password": "student123",
                "role": "student",
                "first_name": "Isabella",
                "last_name": "Rodriguez",
            },
            {
                "studentnumber": 22345678,
                "email": "student8@test.com",
                "password": "student123",
                "role": "student",
                "first_name": "Ethan",
                "last_name": "Lee",
            },
            {
                "studentnumber": 27654321,
                "email": "student9@test.com",
                "password": "student123",
                "role": "student",
                "first_name": "Mia",
                "last_name": "Taylor",
            },
            {
                "studentnumber": 25432167,
                "email": "student10@test.com",
                "password": "student123",
                "role": "student",
                "first_name": "Noah",
                "last_name": "White",
            },
            {
                "studentnumber": 29876543,
                "email": "student11@test.com",
                "password": "student123",
                "role": "student",
                "first_name": "Charlotte",
                "last_name": "Harris",
            },
            {
                "studentnumber": 26789012,
                "email": "student12@test.com",
                "password": "student123",
                "role": "student",
                "first_name": "Liam",
                "last_name": "Clark",
            },
            {
                "studentnumber": 28901234,
                "email": "student13@test.com",
                "password": "student123",
                "role": "student",
                "first_name": "Amelia",
                "last_name": "Lewis",
            },
            # Admin teacher
            {
                "email": "admin@test.com",
                "password": "admin123",
                "role": "admin",
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
            if "studentnumber" in user_data:
                print(f"  Student Number: {user_data['studentnumber']}")

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
        print("  - student4@test.com / student123")
        print("  - student5@test.com / student123")
        print("  - student6@test.com / student123")
        print("  - student7@test.com / student123")
        print("  - student8@test.com / student123")
        print("  - student9@test.com / student123")
        print("  - student10@test.com / student123")
        print("  - student11@test.com / student123")
        print("  - student12@test.com / student123")
        print("  - student13@test.com / student123")
        print("\nYou can now login with any of these accounts.")
        print("=" * 50)
        # print(
        #     f"Created {user_data['role']}: {user_data['email']} (password: {user_data['password']})"
        # )

        db.session.commit()

        # print("\n" + "=" * 50)
        # print("Test users created successfully!")
        # print("=" * 50)
        # print("\nTeacher accounts:")
        # print("  - teacher1@test.com / teacher123")
        # print("  - teacher2@test.com / teacher123")
        # print("  - admin@test.com / admin123 (admin teacher)")
        # print("\nStudent accounts:")
        # print("  - student1@test.com / student123")
        # print("  - student2@test.com / student123")
        # print("  - student3@test.com / student123")
        # print("\nYou can now login with any of these accounts.")
        # print("=" * 50)


if __name__ == "__main__":
    init_users()
