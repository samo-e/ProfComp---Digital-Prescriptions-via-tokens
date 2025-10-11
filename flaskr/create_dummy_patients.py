from datetime import datetime, timedelta
import random

def create_dummy_patients():
    """Create and insert dummy patient records"""
   
    # Sample data for generating realistic records
    first_names = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
                  "William", "Elizabeth", "David", "Susan", "Richard", "Jessica", "Thomas", "Sarah"]
   
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
                 "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas"]
   
    suburbs = ["Sydney", "Melbourne", "Brisbane", "Perth", "Adelaide", "Canberra", "Darwin", "Hobart"]
    states = ["nsw", "vic", "qld", "wa", "sa", "act", "nt", "tas"]
   
    doctors = ["Dr. Wilson", "Dr. Thompson", "Dr. Chen", "Dr. Patel", "Dr. Taylor", "Dr. Roberts"]
   
    # Create 10 dummy patients
    for i in range(10):
        # Generate random but valid data
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        state = random.choice(states)
        suburb = random.choice(suburbs)
       
        # Generate valid Medicare number (format: 8 digits, 1 digit, 3 digits)
        medicare_num = f"{random.randint(1000, 9999)} {random.randint(10000, 99999)} {random.randint(1, 9)}"
       
        # Generate random date of birth (ages between 18-90)
        birth_year = random.randint(1935, 2006)
        birth_month = random.randint(1, 12)
        birth_day = random.randint(1, 28)
        dob = f"{birth_day:02d}/{birth_month:02d}/{birth_year}"
       
        # Generate script date (recent dates)
        script_year = 2024
        script_month = random.randint(1, 12)
        script_day = random.randint(1, 28)
        script_date = f"{script_day:02d}/{script_month:02d}/{script_year}"
       
        # Medicare expiry (future date)
        medicare_valid_to = f"{random.randint(1, 12):02d}/{random.randint(2025, 2030)}"
       
        patient = Patient(
            medicare=medicare_num,
            pharmaceut_ben_entitlement_no=f"PB{random.randint(100000, 999999)}",
            sfty_net_entitlement_cardholder=random.choice([True, False]),
            rpbs_ben_entitlement_cardholder=random.choice([True, False]),
            name=f"{first_name} {last_name}",
            dob=dob,
            preferred_contact=random.choice(["phone", "mobile", "email"]),
            address=f"{random.randint(1, 999)} {random.choice(['Main', 'Oak', 'Pine', 'Maple'])} St",
            script_date=script_date,
            pbs=f"PBS{random.randint(1000, 9999)}" if random.choice([True, False]) else None,
            rpbs=f"RPBS{random.randint(1000, 9999)}" if random.choice([True, False]) else None,
            last_name=last_name,
            given_name=first_name,
            title=random.choice(["Mr", "Ms", "Mrs", "Dr"]),
            sex=random.choice(["Male", "Female"]),
            pt_number=f"PT{random.randint(10000, 99999)}",
            suburb=suburb,
            state=state,
            postcode=random.randint(2000, 7999),
            phone=f"0{random.randint(2,9)}{random.randint(10000000, 99999999)}",
            mobile=f"04{random.randint(10000000, 99999999)}",
            licence=f"DL{random.randint(1000000, 9999999)}",
            sms_repeats=random.choice([True, False]),
            sms_owing=random.choice([True, False]),
            email=f"{first_name.lower()}.{last_name.lower()}@example.com",
            medicare_valid_to=medicare_valid_to,
            medicare_surname=last_name,
            medicare_given_name=first_name,
            concession_number=f"CN{random.randint(100000, 999999)}" if random.choice([True, False]) else None,
            concession_valid_to=f"{random.randint(1, 12):02d}/{random.randint(2024, 2026)}" if random.choice([True, False]) else None,
            safety_net_number=f"SN{random.randint(100000, 999999)}" if random.choice([True, False]) else None,
            repatriation_number=f"RP{random.randint(100000, 999999)}" if random.choice([True, False]) else None,
            ndss_number=f"NDSS{random.randint(10000, 99999)}" if random.choice([True, False]) else None,
            ihi_number=f"{random.randint(800, 899)}{random.randint(1000000000, 9999999999)}" if random.choice([True, False]) else None,
            ihi_status=random.choice(["Active", "Inactive", "Pending"]),
            ihi_record_status=random.choice(["Verified", "Unverified"]),
            doctor=random.choice(doctors),
            ctg_registered=random.choice([True, False]),
            generics_only=random.choice([True, False]),
            repeats_held=random.choice([True, False]),
            pt_deceased=False,  # Keep them alive for testing
            carer=None,  # or add carer data if needed
            consented_to_asl=random.choice([True, False]),
            consented_to_upload=random.choice([True, False]),
            asl_status=random.choice([1, 2, 3]),  # Assuming 1,2,3 are valid ASLStatus values
            is_registered=True
        )
       
        db.session.add(patient)
   
    try:
        db.session.commit()
        print("Successfully added 10 dummy patients!")
    except Exception as e:
        db.session.rollback()
        print(f"Error adding dummy patients: {e}")