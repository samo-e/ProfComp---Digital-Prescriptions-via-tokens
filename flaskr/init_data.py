def init_asl_database():
    """Initialize DB with ASL data"""
    from website import create_app

    # Import ASLStatus for creating different scenarios
    from website.models import (
        db,
        Patient,
        Prescriber,
        Prescription,
        PrescriptionStatus,
        ASLStatus,
    )

    application = create_app()
    app = application
    with app.app_context():
        db.drop_all()
        db.create_all()

        # GRANTED status test
        patient = Patient(
            id=1,
            medicare=49502864011,  # int
            pharmaceut_ben_entitlement_no="NA318402K(W)",
            sfty_net_entitlement_cardholder=True,
            rpbs_ben_entitlement_cardholder=False,
            name="Draga Diaz",
            dob="26/01/1998",
            preferred_contact=401234567,
            address="33 JIT DR CHARAM VIC 3318",
            script_date="30/11/2020",
            pbs=None,
            rpbs=None,
            is_registered=True,  # Added
        )

        # pending status
        patient2 = Patient(
            id=2,
            medicare=12345678901,  # int
            pharmaceut_ben_entitlement_no="TEST123456(X)",
            sfty_net_entitlement_cardholder=False,
            rpbs_ben_entitlement_cardholder=True,
            name="John Smith",
            dob="15/03/1985",
            preferred_contact=412345678,
            address="123 Main St MELBOURNE VIC 3000",
            script_date="15/12/2023",
            pbs=None,
            rpbs=None,
            asl_status=ASLStatus.PENDING.value,
            is_registered=True,  # Added
        )

        # REJECTED status
        patient3 = Patient(
            id=3,
            medicare=98765432109,  # int
            pharmaceut_ben_entitlement_no="REJ789012(Z)",
            sfty_net_entitlement_cardholder=True,
            rpbs_ben_entitlement_cardholder=False,
            name="Sarah Johnson",
            dob="10/07/1992",
            preferred_contact=455123456,
            address="456 Oak Ave PERTH WA 6000",
            script_date="20/01/2024",
            pbs=None,
            rpbs=None,
            asl_status=ASLStatus.REJECTED.value,
            is_registered=True,  # Added
        )

        # NO_CONSENT status
        patient4 = Patient(
            id=4,
            medicare=11122233344,  # int
            pharmaceut_ben_entitlement_no="NEW456789(A)",
            sfty_net_entitlement_cardholder=False,
            rpbs_ben_entitlement_cardholder=False,
            name="Michael Brown",
            dob="05/09/1975",
            preferred_contact=433987654,
            address="789 Pine St SYDNEY NSW 2000",
            script_date="15/02/2024",
            pbs=None,
            rpbs=None,
            asl_status=ASLStatus.NO_CONSENT.value,
            is_registered=True,  # Added
        )

        # Create test prescriber
        prescriber = Prescriber(
            id=1,
            fname="Phillip",
            lname="Davis",
            title="( MBBS; FRACGP )",
            address_1="Level 3  60 Albert Rd",
            address_2="SOUTH MELBOURNE VIC 3205",
            prescriber_id=987774,
            hpii=8003619900026805,
            hpio=8003626566692846,
            phone="03 9284 3300",
            fax=None,
        )

        # Create ASL prescriptions with different status for Patient 1 (lines 79-118)
        asl_prescriptions = [
            # prescription - shows in ASL table
            Prescription(
                patient_id=1,
                prescriber_id=1,
                DSPID="asl",
                status=PrescriptionStatus.AVAILABLE.value,
                drug_name="Coversyl 5mg tablet, 30 5 mg 30 Tablets",
                drug_code="9007C",
                dose_instr="ONCE A DAY",
                dose_qty=30,
                dose_rpt=6,
                prescribed_date="10/06/2021",
                paperless=True,
                brand_sub_not_prmt=False,
                remaining_repeats=6,
                dispensed_at_this_pharmacy=False,
            ),
            # prescription PENDING status - prescribed but not yet visible in ASL table
            Prescription(
                patient_id=1,
                prescriber_id=1,
                DSPID="asl",
                status=PrescriptionStatus.PENDING.value,
                drug_name="Diabex 1 g tablet, 90 1000 mg 90 Tablets",
                drug_code="8607B",
                dose_instr="ONCE A DAY",
                dose_qty=90,
                dose_rpt=6,
                prescribed_date="10/06/2021",
                paperless=True,
                brand_sub_not_prmt=False,
                remaining_repeats=6,
                dispensed_at_this_pharmacy=False,
            ),
            Prescription(
                patient_id=1,
                prescriber_id=1,
                DSPID="asl",
                status=PrescriptionStatus.AVAILABLE.value,
                drug_name="Lipitor 10mg tablet, 30 10 mg 30 Tablets",
                drug_code="8213G",
                dose_instr="ONCE A DAY",
                dose_qty=30,
                dose_rpt=5,
                prescribed_date="10/06/2021",
                paperless=False,
                brand_sub_not_prmt=False,
                remaining_repeats=5,
                dispensed_at_this_pharmacy=False,
            ),
            Prescription(
                patient_id=1,
                prescriber_id=1,
                DSPID="asl",
                status=PrescriptionStatus.CANCELLED.value,
                drug_name="Panadol Extra 500mg tablet, 20 tablets",
                drug_code="1234A",
                dose_instr="AS REQUIRED FOR PAIN",
                dose_qty=20,
                dose_rpt=2,
                prescribed_date="15/06/2021",
                paperless=True,
                brand_sub_not_prmt=False,
                remaining_repeats=2,
                dispensed_at_this_pharmacy=False,
            ),
        ]

        # prescriptions for other patients (won't show due to ASL status)
        other_patient_prescriptions = [
            # Patient 2 (PENDING status) - has prescriptions, can't see it due to ASL status
            Prescription(
                patient_id=2,
                prescriber_id=1,
                DSPID="asl",
                status=PrescriptionStatus.AVAILABLE.value,
                drug_name="Ventolin HFA 100mcg inhaler",
                drug_code="2345B",
                dose_instr="TWO PUFFS TWICE DAILY",
                dose_qty=1,
                dose_rpt=4,
                prescribed_date="15/12/2023",
                paperless=True,
                brand_sub_not_prmt=False,
                remaining_repeats=4,
                dispensed_at_this_pharmacy=False,
            ),
            # Patient 3 (REJECTED status) - has prescriptions,  can't see it due to ASL status
            Prescription(
                patient_id=3,
                prescriber_id=1,
                DSPID="asl",
                status=PrescriptionStatus.AVAILABLE.value,
                drug_name="Nexium 20mg tablet, 28 tablets",
                drug_code="3456C",
                dose_instr="ONCE DAILY BEFORE BREAKFAST",
                dose_qty=28,
                dose_rpt=3,
                prescribed_date="20/01/2024",
                paperless=True,
                brand_sub_not_prmt=False,
                remaining_repeats=3,
                dispensed_at_this_pharmacy=False,
            ),
            # Patient 4 (NO_CONSENT status) - has prescriptions,  can't see it due to ASL status
            Prescription(
                patient_id=4,
                prescriber_id=1,
                DSPID="asl",
                status=PrescriptionStatus.AVAILABLE.value,
                drug_name="Atorvastatin 40mg tablet, 30 tablets",
                drug_code="4567D",
                dose_instr="ONCE DAILY AT NIGHT",
                dose_qty=30,
                dose_rpt=5,
                prescribed_date="15/02/2024",
                paperless=True,
                brand_sub_not_prmt=False,
                remaining_repeats=5,
                dispensed_at_this_pharmacy=False,
            ),
        ]

        # ALR prescriptions
        alr_prescriptions = [
            # DISPENSED with remaining repeats
            Prescription(
                patient_id=1,
                prescriber_id=1,
                DSPID="alr",
                status=PrescriptionStatus.DISPENSED.value,
                drug_name="Levlen ED Tablets, 150mcg-30mcg(28)",
                drug_code="1394J",
                dose_instr="ONCE DAILY",
                dose_qty=4,
                dose_rpt=6,
                prescribed_date="05/07/2021",
                dispensed_date="05/07/2021",
                paperless=False,
                brand_sub_not_prmt=False,
                remaining_repeats=3,  # has 3 repeats left
                dispensed_at_this_pharmacy=True,  # Was dispensed at current pharmacy: Y/N
            ),
            # second ALR example
            Prescription(
                patient_id=1,
                prescriber_id=1,
                DSPID="alr",
                status=PrescriptionStatus.DISPENSED.value,
                drug_name="Nexium 20mg tablet, 28 tablets",
                drug_code="8888X",
                dose_instr="ONCE DAILY BEFORE BREAKFAST",
                dose_qty=28,
                dose_rpt=5,
                prescribed_date="10/06/2021",
                dispensed_date="23/06/2021",
                paperless=True,
                brand_sub_not_prmt=False,
                remaining_repeats=2,  # has 2 repeats left
                dispensed_at_this_pharmacy=True,
            ),
        ]

        # Add all patients to db
        db.session.add(patient)
        db.session.add(patient2)
        db.session.add(patient3)
        db.session.add(patient4)
        db.session.add(prescriber)

        # Add all prescription types
        for prescription in (
            asl_prescriptions + alr_prescriptions + other_patient_prescriptions
        ):
            db.session.add(prescription)

        db.session.commit()
        # print("ASL database initialized successfully")
        # Update message
        # print(
        #     f"Created: 4 patients, 1 prescriber, {len(asl_prescriptions + alr_prescriptions + other_patient_prescriptions)} prescriptions"
        # )
        # print("Patient ASL statuses:")
        # print("- Patient 1 (Draga): GRANTED - can view ASL")
        # print("- Patient 2 (John): PENDING - waiting for SMS/email reply")
        # print("- Patient 3 (Sarah): REJECTED - patient denied access")
        # print("- Patient 4 (Michael): NO_CONSENT - never requested access before")
        #

if __name__ == "__main__":
    init_asl_database()
