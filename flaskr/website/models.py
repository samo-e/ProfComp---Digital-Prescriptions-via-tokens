from . import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import enum


# Enum for roles
class Role(enum.Enum):
    STUDENT = "student"
    TEACHER = "teacher"

class User(UserMixin, db.Model):
    __tablename__ = "users"


    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    role = db.Column(db.Enum(Role), nullable=False)

    # Relationships (optional, if you’ll add more tables later)
    # teacher_profile = db.relationship('Teacher', backref='user', uselist=False)
    # student_profile = db.relationship('Student', backref='user', uselist=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_teacher(self):
        return self.role == Role.TEACHER

    def is_student(self):
        return self.role == Role.STUDENT





