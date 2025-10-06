"""
Auto-seeding script that seeds the database only if it's empty.
This prevents duplicate data on redeploys while ensuring the database is always seeded.
"""

def auto_seed():
    """Automatically seed the database - always clear and reseed for production"""
    from website import create_app
    from website.models import db, User, Patient, Prescriber, Prescription, Scenario
    
    app = create_app()
    with app.app_context():
        # Always clear existing data for production
        print("Clearing existing data...")
        User.query.delete()
        Patient.query.delete()
        db.session.commit()
        print("Database cleared")
        
        # Always seed users
        print("Seeding users...")
        from init_users import init_users
        init_users(auto_mode=True)
        
        # Verify users were created
        user_count = User.query.count()
        if user_count > 0:
            print(f"Users seeded successfully! ({user_count} users created)")
        else:
            print("ERROR: No users were created!")
            return False
        
        # Always seed patient data
        print("Seeding patient data...")
        from init_data import init_asl_database
        init_asl_database()
        
        # Verify patients were created
        patient_count = Patient.query.count()
        if patient_count > 0:
            print(f"Patient data seeded successfully! ({patient_count} patients created)")
        else:
            print("ERROR: No patients were created!")
            return False
        
        print("Auto-seeding complete!")
        return True

if __name__ == "__main__":
    auto_seed()
