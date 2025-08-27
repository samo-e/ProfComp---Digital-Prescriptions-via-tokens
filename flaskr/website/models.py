from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin):
    def __init__(self, id, email, password_hash, role='student', name=''):
        self.id = id
        self.email = email
        self.password_hash = password_hash
        self.role = role
        self.name = name
        self.is_active = True
        self.created_at = datetime.utcnow()
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @staticmethod
    def create_password_hash(password):
        return generate_password_hash(password)
    
    def is_teacher(self):
        return self.role == 'teacher'
    
    def is_student(self):
        return self.role == 'student'

# In-memory user storage (replace with database later)
users_db = {}
user_id_counter = 1

def create_user(email, password, role='student', name=''):
    global user_id_counter
    user_id = str(user_id_counter)
    password_hash = User.create_password_hash(password)
    user = User(user_id, email, password_hash, role, name)
    users_db[user_id] = user
    user_id_counter += 1
    return user

def get_user_by_email(email):
    for user in users_db.values():
        if user.email == email:
            return user
    return None

def get_user_by_id(user_id):
    return users_db.get(user_id)

# Create some default users for testing
def init_default_users():
    # Create a teacher account
    if not get_user_by_email('teacher@example.com'):
        create_user('teacher@example.com', 'teacher123', 'teacher', 'Dr. Smith')
    
    # Create a student account
    if not get_user_by_email('student@example.com'):
        create_user('student@example.com', 'student123', 'student', 'John Doe')