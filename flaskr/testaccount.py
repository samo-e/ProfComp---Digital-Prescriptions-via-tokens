from flask import current_app
from werkzeug.security import generate_password_hash
from website.models import db, User, Role

def inject_test_accounts(app):
    with app.app_context():
        # Student account
        student = User.query.filter_by(email="student1@gmail.com").first()
        if not student:
            student = User(
                username="student1",
                email="student1@gmail.com",
                password=generate_password_hash("12345678", method="pbkdf2:sha256", salt_length=16),
                role=Role.STUDENT
            )
            db.session.add(student)
            print("Injected student1 account.")
        else:
            print("student1 account already exists.")

        # Teacher account
        teacher = User.query.filter_by(email="teacher1@gmail.com").first()
        if not teacher:
            teacher = User(
                username="teacher1",
                email="teacher1@gmail.com",
                password=generate_password_hash("12345678", method="pbkdf2:sha256", salt_length=16),
                role=Role.TEACHER
            )
            db.session.add(teacher)
            print("Injected teacher1 account.")
        else:
            print("teacher1 account already exists.")

        db.session.commit()
