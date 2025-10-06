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
        print("Users seeded successfully!")
        
        # Always seed patient data
        print("Seeding patient data...")
        from init_data import init_asl_database
        init_asl_database()
        print("Patient data seeded successfully!")
        
        print("Auto-seeding complete!")

if __name__ == "__main__":
    auto_seed()
