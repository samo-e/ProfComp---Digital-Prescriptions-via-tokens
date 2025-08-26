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

class ConsentStatus(Enum):
    GRANTED = 0
    REVOKED = 1


class ASLStatus(Enum):  #can't display this one for now (need to modify the front end later)
    REGISTERED = 0
    ACCESS_REQUESTED = 1
    ACCESS_GRANTED = 2

class Patient(db.Model):
    __tablename__ = 'patients'
    
    id = db.Column(db.Integer, primary_key=True)
    medicare = db.Column(db.String(11))
    pharmaceut_ben_entitlement_no = db.Column(db.String(20))
    sfty_net_entitlement_cardholder = db.Column(db.Boolean, default=False)
    rpbs_ben_entitlement_cardholder = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(100))
    dob = db.Column(db.String(10))  # format is DD/MM/YYYY
    preferred_contact = db.Column(db.String(20))
    address_1 = db.Column(db.String(100))
    address_2 = db.Column(db.String(100))
    script_date = db.Column(db.String(10))
    pbs = db.Column(db.String(50), nullable=True) # set pbs and rpbs (for now their value are 'none')
    rpbs = db.Column(db.String(50), nullable=True)
    
    # status stored as integer enum
    consent_status = db.Column(db.Integer, default=ConsentStatus.GRANTED.value)
    asl_status = db.Column(db.Integer, default=ASLStatus.REGISTERED.value)
    consent_last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_consent_status(self):
        return ConsentStatus(self.consent_status)
    
    def get_asl_status(self):
        return ASLStatus(self.asl_status)

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
    
    # DB Relationships
    patient = db.relationship('Patient', backref='prescriptions')
    prescriber = db.relationship('Prescriber', backref='prescriptions')
    
    def get_status(self):
        return PrescriptionStatus(self.status)