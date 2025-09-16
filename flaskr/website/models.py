from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from enum import Enum

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
    # medicare Integer
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
    # flatten format in this file, will convert it to JSON format in views.py
    asl_status = db.Column(db.Integer, default=ASLStatus.GRANTED.value)
    consent_last_updated = db.Column(db.String(20), default=lambda: datetime.now().strftime('%d/%m/%Y %I:%M %p'))
    

    is_registered = db.Column(db.Boolean, default=True)

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