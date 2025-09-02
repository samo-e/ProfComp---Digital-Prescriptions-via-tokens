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
        self.active = True
        self.created_at = datetime.utcnow()
    
    def check_password(self, password):
        """Check if provided password matches the hash"""
        return check_password_hash(self.password_hash, password)
    
    def set_password(self, password):
        """Set a new password (updates the hash)"""
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
    
    @staticmethod
    def create_password_hash(password):
        """Create a password hash from plain text"""
        return generate_password_hash(password, method='pbkdf2:sha256')
    
    def is_teacher(self):
        return self.role == 'teacher'
    
    def is_student(self):
        return self.role == 'student'
    
    def is_active(self):
        return self.active
    
    def is_anonymous(self):
        return False
    
    def is_authenticated(self):
        return True
    
    def get_id(self):
        return str(self.id)

# In-memory user storage (replace with database later)
users_db = {}
user_id_counter = 1

def create_user(email, password, role='student', name=''):
    """Create a new user with hashed password"""
    global user_id_counter
    user_id = str(user_id_counter)
    
    # Hash the password before storing
    password_hash = User.create_password_hash(password)
    
    user = User(user_id, email, password_hash, role, name)
    users_db[user_id] = user
    user_id_counter += 1
    
    print(f"Created user: {email} with ID: {user_id}")  # Debug
    return user

def get_user_by_email(email):
    """Find a user by their email address"""
    for user in users_db.values():
        if user.email.lower() == email.lower():  # Case-insensitive email matching
            return user
    return None

def get_user_by_id(user_id):
    """Find a user by their ID"""
    return users_db.get(str(user_id))  # Ensure ID is string

def init_default_users():
    """Initialize default test users if they don't exist"""
    # Check if default users already exist
    if not get_user_by_email('teacher@example.com'):
        user = create_user(
            email='teacher@example.com',
            password='teacher123',
            role='teacher',
            name='Dr. Smith'
        )
        print(f"Created default teacher: {user.email}")
    
    if not get_user_by_email('student@example.com'):
        user = create_user(
            email='student@example.com',
            password='student123',
            role='student',
            name='John Doe'
        )
        print(f"Created default student: {user.email}")
    
    # Additional test users
    if not get_user_by_email('teacher2@example.com'):
        create_user(
            email='teacher2@example.com',
            password='teacher456',
            role='teacher',
            name='Prof. Johnson'
        )
    
    if not get_user_by_email('student2@example.com'):
        create_user(
            email='student2@example.com',
            password='student456',
            role='student',
            name='Jane Smith'
        )

def verify_user_credentials(email, password):
    """Verify user credentials - helper function for login"""
    user = get_user_by_email(email)
    if user and user.check_password(password):
        return user
    return None

def update_user_password(user_id, new_password):
    """Update a user's password"""
    user = get_user_by_id(user_id)
    if user:
        user.set_password(new_password)
        return True
    return False

def list_all_users():
    """List all users (for debugging)"""
    users = []
    for user in users_db.values():
        users.append({
            'id': user.id,
            'email': user.email,
            'name': user.name,
            'role': user.role
        })
    return users