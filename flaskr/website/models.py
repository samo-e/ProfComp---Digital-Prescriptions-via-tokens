from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from enum import Enum
import enum

db = SQLAlchemy()

# Enums stored as integers (0,1,2,3), we can add more in the future if needed
class PrescriptionStatus(Enum): 
    PENDING = 0
    AVAILABLE = 1
    DISPENSED = 2
    CANCELLED = 3

# Updated ASL Status combining consent and access status
class ASLStatus(Enum):
    NO_CONSENT = 0    
    PENDING = 1      
    GRANTED = 2       
    REJECTED = 3

# User roles enum
class UserRole(Enum):
    TEACHER = "teacher"
    STUDENT = "student"

class User(db.Model, UserMixin):
    """User model for authentication - supports both teachers and students"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'teacher' or 'student'
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.now)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    created_scenarios = db.relationship('Scenario', backref='creator', lazy=True, 
                                       foreign_keys='Scenario.teacher_id')
    assigned_scenarios = db.relationship('Scenario', secondary='student_scenarios', 
                                        backref='assigned_students', lazy=True)
    
    def set_password(self, password):
        """Hash and set the user's password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches the hash"""
        return check_password_hash(self.password_hash, password)
    
    def is_teacher(self):
        """Check if user is a teacher"""
        return self.role == UserRole.TEACHER.value
    
    def is_student(self):
        """Check if user is a student"""
        return self.role == UserRole.STUDENT.value
    
    def get_full_name(self):
        """Get user's full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.email
    
    def __repr__(self):
        return f'<User {self.email} ({self.role})>'


class Scenario(db.Model):
    """Scenario model for managing teaching scenarios"""
    __tablename__ = 'scenarios'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    password = db.Column(db.String(50))  # Optional password protection
    version = db.Column(db.Integer, default=1)
    parent_scenario_id = db.Column(db.Integer, db.ForeignKey('scenarios.id'))
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    is_archived = db.Column(db.Boolean, default=False)
    
    # Patient data for this scenario
    patient_data = db.relationship('ScenarioPatient', backref='scenario', 
                                  cascade='all, delete-orphan', lazy=True)
    
    def __repr__(self):
        return f'<Scenario {self.name} v{self.version}>'


class StudentScenario(db.Model):
    """Association table for student-scenario assignments"""
    __tablename__ = 'student_scenarios'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    scenario_id = db.Column(db.Integer, db.ForeignKey('scenarios.id'), nullable=False)
    assigned_at = db.Column(db.DateTime, default=datetime.now)
    completed_at = db.Column(db.DateTime)
    score = db.Column(db.Float)
    

class ScenarioPatient(db.Model):
    """Patient data specific to a scenario"""
    __tablename__ = 'scenario_patients'
    
    id = db.Column(db.Integer, primary_key=True)
    scenario_id = db.Column(db.Integer, db.ForeignKey('scenarios.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    # Any scenario-specific overrides for patient data can go here
    

class Patient(db.Model):
    __tablename__ = 'patients'
    
    id = db.Column(db.Integer, primary_key=True)
    medicare = db.Column(db.BigInteger)  # Contract specifies int
    pharmaceut_ben_entitlement_no = db.Column(db.String(20))
    sfty_net_entitlement_cardholder = db.Column(db.Boolean, default=False)
    rpbs_ben_entitlement_cardholder = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(100))
    dob = db.Column(db.String(10))  # DD/MM/YYYY format
    preferred_contact = db.Column(db.BigInteger)
    address_1 = db.Column(db.String(100))
    address_2 = db.Column(db.String(100))
    script_date = db.Column(db.String(10))
    pbs = db.Column(db.String(50), nullable=True)
    rpbs = db.Column(db.String(50), nullable=True)
    asl_status = db.Column(db.Integer, default=ASLStatus.GRANTED.value)
    consent_last_updated = db.Column(db.String(20), default=lambda: datetime.now().strftime('%d/%m/%Y %I:%M %p'))
    is_registered = db.Column(db.Boolean, default=True)

    def get_asl_status(self):
        return ASLStatus(self.asl_status)
    
    def can_view_asl(self):
        return self.asl_status == ASLStatus.GRANTED.value


class Prescriber(db.Model):
    __tablename__ = 'prescribers'
    
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(50))
    lname = db.Column(db.String(50))
    title = db.Column(db.String(100))
    address_1 = db.Column(db.String(100))
    address_2 = db.Column(db.String(100))
    prescriber_id = db.Column(db.Integer)  # int
    hpii = db.Column(db.BigInteger)  # int
    hpio = db.Column(db.BigInteger)  # int
    phone = db.Column(db.String(20))  # str
    fax = db.Column(db.String(20), nullable=True)


class Prescription(db.Model):
    __tablename__ = 'prescriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    prescriber_id = db.Column(db.Integer, db.ForeignKey('prescribers.id'), nullable=False)
    DSPID = db.Column(db.String(50), nullable=True)
    status = db.Column(db.Integer, default=PrescriptionStatus.AVAILABLE.value)
    brand_sub_not_prmt = db.Column(db.Boolean, default=False)
    drug_name = db.Column(db.String(200))
    drug_code = db.Column(db.String(10))
    dose_instr = db.Column(db.String(200))
    dose_qty = db.Column(db.Integer)
    dose_rpt = db.Column(db.Integer)
    prescribed_date = db.Column(db.String(10))
    dispensed_date = db.Column(db.String(10), nullable=True)
    paperless = db.Column(db.Boolean, default=True)
    remaining_repeats = db.Column(db.Integer, nullable=True)
    dispensed_at_this_pharmacy = db.Column(db.Boolean, default=False)
    
    # DB Relationships
    patient = db.relationship('Patient', backref='prescriptions')
    prescriber = db.relationship('Prescriber', backref='prescriptions')
    
    def get_status(self):
        return PrescriptionStatus(self.status)
      
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
