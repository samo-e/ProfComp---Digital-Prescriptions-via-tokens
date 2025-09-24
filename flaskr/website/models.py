from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from enum import Enum
import enum

db = SQLAlchemy()

# Enums stored as integers (0,1,2,3), we can add more in the future if needed
class PrescriptionStatus(Enum): # haven't user this yet
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

class Patient(db.Model):
    __tablename__ = 'patients'
    
    id = db.Column(db.Integer, primary_key=True)
    medicare = db.Column(db.String(11))
    medicare_issue = db.Column(db.Integer, nullable=True)  # individual reference number
    pharmaceut_ben_entitlement_no = db.Column(db.String(20))
    sfty_net_entitlement_cardholder = db.Column(db.Boolean, default=False)
    rpbs_ben_entitlement_cardholder = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(100))
    dob = db.Column(db.String(10))  # format is DD/MM/YYYY
    preferred_contact = db.Column(db.String(20))
    address = db.Column(db.String(100))
    script_date = db.Column(db.String(10))
    pbs = db.Column(db.String(50), nullable=True) # set pbs and rpbs (for now their value are 'none')
    rpbs = db.Column(db.String(50), nullable=True)
    # Extended patient profile (for edit-pt and registration flows)
    last_name = db.Column(db.String(100), nullable=True)
    given_name = db.Column(db.String(100), nullable=True)
    title = db.Column(db.String(50), nullable=True)
    sex = db.Column(db.String(20), nullable=True)  # Male/Female
    pt_number = db.Column(db.String(50), nullable=True)
    suburb = db.Column(db.String(100), nullable=True)
    state = db.Column(db.String(10), nullable=True)  # act, nt, nsw, qld, sa, tas, vic, wa
    postcode = db.Column(db.Integer, nullable=True)
    phone = db.Column(db.String(30), nullable=True)
    mobile = db.Column(db.String(30), nullable=True)
    licence = db.Column(db.String(50), nullable=True)
    sms_repeats = db.Column(db.Boolean, default=False)
    sms_owing = db.Column(db.Boolean, default=False)
    email = db.Column(db.String(120), nullable=True)
    medicare_valid_to = db.Column(db.String(10), nullable=True)  # mm/yyyy
    medicare_surname = db.Column(db.String(100), nullable=True)
    medicare_given_name = db.Column(db.String(100), nullable=True)
    concession_number = db.Column(db.String(50), nullable=True)
    concession_valid_to = db.Column(db.String(10), nullable=True)
    safety_net_number = db.Column(db.String(50), nullable=True)
    repatriation_number = db.Column(db.String(50), nullable=True)
    repatriation_valid_to = db.Column(db.String(10), nullable=True)
    repatriation_type = db.Column(db.String(50), nullable=True)
    ndss_number = db.Column(db.String(50), nullable=True)
    ihi_number = db.Column(db.String(16), nullable=True)
    ihi_status = db.Column(db.String(50), nullable=True)
    ihi_record_status = db.Column(db.String(50), nullable=True)
    doctor = db.Column(db.String(100), nullable=True)  # could be ID reference later
    ctg_registered = db.Column(db.Boolean, default=False)
    generics_only = db.Column(db.Boolean, default=False)
    repeats_held = db.Column(db.Boolean, default=False)
    pt_deceased = db.Column(db.Boolean, default=False)
    carer = db.Column(db.JSON, nullable=True)
    consented_to_asl = db.Column(db.Boolean, default=False)
    consented_to_upload = db.Column(db.Boolean, default=False)
    
    # Combined status=
    asl_status = db.Column(db.Integer, default=ASLStatus.GRANTED.value)
    consent_last_updated = db.Column(db.String(20), default=lambda: datetime.utcnow().strftime('%d/%m/%Y %H:%M'))
    
    def get_asl_status(self):
        return ASLStatus(self.asl_status)
    
    # check if pharmacy can view ASL data
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
    prescriber_id = db.Column(db.String(10))
    hpii = db.Column(db.String(16)) # HPI-individual
    hpio = db.Column(db.String(16)) #HPI - organisation
    phone = db.Column(db.String(20))
    fax = db.Column(db.String(20), nullable=True)

class Prescription(db.Model):
    __tablename__ = 'prescriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    prescriber_id = db.Column(db.Integer, db.ForeignKey('prescribers.id'), nullable=False)
    DSPID = db.Column(db.String(50), nullable=True) #DSP id (digital script prescription)
    
    # Status stored as integer enum
    status = db.Column(db.Integer, default=PrescriptionStatus.AVAILABLE.value)
    
    brand_sub_not_prmt = db.Column(db.Boolean, default=False) # brand not permitted
    drug_name = db.Column(db.String(200))
    drug_code = db.Column(db.String(10))
    dose_instr = db.Column(db.String(200))  # dosage instructions
    dose_qty = db.Column(db.Integer)   # quantity
    dose_rpt = db.Column(db.Integer)   # repeats
    prescribed_date = db.Column(db.String(10))
    dispensed_date = db.Column(db.String(10), nullable=True)
    paperless = db.Column(db.Boolean, default=True)
    
    # Fields for ALR functionality
    remaining_repeats = db.Column(db.Integer, nullable=True)  # How many repeats left after dispensing?
    dispensed_at_this_pharmacy = db.Column(db.Boolean, default=False)  # was this dispensed at current pharmacy?
    
    # DB Relationships
    patient = db.relationship('Patient', backref='prescriptions')
    prescriber = db.relationship('Prescriber', backref='prescriptions')
    
    def get_status(self):
        return PrescriptionStatus(self.status)
      
     # Enum for roles
     
class ASL(db.Model):
    __tablename__ = "asls"
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    consent_status = db.Column(db.Integer, default=ASLStatus.PENDING.value)  
    carer_name = db.Column(db.String(100))
    carer_relationship = db.Column(db.String(100))
    notes = db.Column(db.Text)
    
    patient = db.relationship("Patient", backref="asls")
    
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

