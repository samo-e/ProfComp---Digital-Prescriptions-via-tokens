def init_asl_database():
    """Initialize DB with ASL data"""
    from website import create_app
    from website.models import db, Patient, Prescriber, Prescription, PrescriptionStatus
    
    application = create_app()
    app = application
    with app.app_context():
        db.drop_all()
        db.create_all()
        
        # Create test patient
        patient = Patient(
            id=1,
            medicare="49502864011",
            pharmaceut_ben_entitlement_no="NA318402K(W)",
            sfty_net_entitlement_cardholder=True,
            rpbs_ben_entitlement_cardholder=False,
            name="Draga Diaz",
            dob="26/01/1998",
            preferred_contact="0401 234 567",
            address_1="33 JIT DR",
            address_2="CHARAM VIC 3318",
            script_date="30/11/2020",
            pbs=None,
            rpbs=None
        )
        # Create second test patient (but didn't add any prescription for him/her, we can change it later)
        patient2 = Patient(
            id=2,
            medicare="12345678901",
            pharmaceut_ben_entitlement_no="TEST123456(X)",
            sfty_net_entitlement_cardholder=False,
            rpbs_ben_entitlement_cardholder=True,
            name="John Smith",
            dob="15/03/1985",
            preferred_contact="0412 345 678",
            address_1="123 Main St",
            address_2="MELBOURNE VIC 3000",
            script_date="15/12/2023",
            pbs=None,
            rpbs=None
        )
        
        # Create test prescriber
        prescriber = Prescriber(
            id=1,
            fname="Phillip",
            lname="Davis",
            title="( MBBS; FRACGP )",
            address_1="Level 3  60 Albert Rd",
            address_2="SOUTH MELBOURNE VIC 3205",
            prescriber_id="987774",
            hpii="8003619900026805",
            hpio="8003626566692846",
            phone="03 9284 3300",
            fax=None
        )
        
        # Create ASL
        asl_prescriptions = [
            Prescription(
                patient_id=1, prescriber_id=1,
                DSPID="MPK00009002011563",
                status=PrescriptionStatus.AVAILABLE.value,
                drug_name="Coversyl 5mg tablet, 30 5 mg 30 Tablets",
                drug_code="9007C", dose_instr="ONCE A DAY",
                dose_qty=30, dose_rpt=6, prescribed_date="10/06/2021",
                paperless=True, brand_sub_not_prmt=False
            ),
            Prescription(
                patient_id=1, prescriber_id=1,
                DSPID="MPK00009002020646", 
                status=PrescriptionStatus.AVAILABLE.value,
                drug_name="Diabex 1 g tablet, 90 1000 mg 90 Tablets",
                drug_code="8607B", dose_instr="ONCE A DAY",
                dose_qty=90, dose_rpt=6, prescribed_date="10/06/2021",
                paperless=True, brand_sub_not_prmt=False
            ),
            Prescription(
                patient_id=1, prescriber_id=1,
                DSPID="MPK00009002033457",
                status=PrescriptionStatus.AVAILABLE.value,
                drug_name="Lipitor 10mg tablet, 30 10 mg 30 Tablets",
                drug_code="8213G", dose_instr="ONCE A DAY",
                dose_qty=30, dose_rpt=5, prescribed_date="10/06/2021",
                paperless=False, brand_sub_not_prmt=False
            )
        ]
        
        # Create ALR
        alr_prescriptions = [
            Prescription(
                patient_id=1, prescriber_id=1,
                DSPID=None,
                status=PrescriptionStatus.DISPENSED.value,
                drug_name="Levlen ED Tablets, 150mcg-30mcg(28)",
                drug_code="1394J", dose_instr="",
                dose_qty=4, dose_rpt=2, 
                prescribed_date="05/07/2021", dispensed_date="05/07/2021",
                paperless=False, brand_sub_not_prmt=False
            ),
            Prescription(
                patient_id=1, prescriber_id=1,
                DSPID=None,
                status=PrescriptionStatus.DISPENSED.value,
                drug_name="Diabex 1 g tablet, 90 1000 mg 90 Tablets",
                drug_code="8607B", 
                dose_instr="Shake well and inhale TWO puffs by mouth TWICE a day as directed by your physician",
                dose_qty=1, dose_rpt=3,
                prescribed_date="10/06/2021", dispensed_date="23/06/2021",
                paperless=True, brand_sub_not_prmt=False
            )
        ]
        
        # Add those info to database
        db.session.add(patient)
        db.session.add(patient2)
        db.session.add(prescriber)
        
        for prescription in asl_prescriptions + alr_prescriptions:
            db.session.add(prescription)
        
        db.session.commit()
        print("ASL database initialized successfully")
        print(f"Created: 2 patient, 1 prescriber, {len(asl_prescriptions + alr_prescriptions)} prescriptions")

if __name__ == '__main__':
    init_asl_database()