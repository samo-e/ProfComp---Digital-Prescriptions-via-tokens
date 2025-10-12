import getpass
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from website.models import db, User
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///asl_simulation.db"
db.init_app(app)

with app.app_context():
    email = input("Enter admin email: ")
    first_name = input("Enter first name: ")
    last_name = input("Enter last name: ")
    password = getpass.getpass("Enter admin password: ")
    admin = User(email=email, first_name=first_name, last_name=last_name, role="admin", is_active=True)
    admin.set_password(password)
    db.session.add(admin)
    db.session.commit()
    print("Admin account created successfully.")