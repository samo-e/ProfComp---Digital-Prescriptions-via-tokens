"""
Auto-seeding script that seeds the database only if it's empty.
This prevents duplicate data on redeploys while ensuring the database is always seeded.
"""

def auto_seed():
    """Automatically seed the database if it's empty"""
    from website import create_app
    from website.models import db, User, Patient, Prescriber, Prescription, Scenario
    
    app = create_app()
    with app.app_context():
        # Check if users exist
        user_count = User.query.count()
        
        if user_count == 0:
            print("Database is empty, seeding users...")
            from init_users import init_users
            init_users(auto_mode=True)
            print("Users seeded successfully!")
        else:
            print(f"Database already has {user_count} users, skipping user seeding")
        
        # Check if patients exist
        patient_count = Patient.query.count()
        
        if patient_count == 0:
            print("Database is empty, seeding patient data...")
            from init_data import init_asl_database
            init_asl_database()
            print("Patient data seeded successfully!")
        else:
            print(f"Database already has {patient_count} patients, skipping patient data seeding")
        
        print("Auto-seeding complete!")

if __name__ == "__main__":
    auto_seed()
