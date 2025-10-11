"""
Script to inject a single admin account if it doesn't exist.
Usage: python inject_admin.py
"""

def inject_admin():
    from website import create_app
    from website.models import db, User

    app = create_app()
    with app.app_context():
        email = "admin@test.com"
        existing = User.query.filter_by(email=email).first()
        if existing:
            print(f"Admin account with email {email} already exists.")
            return
        admin = User(
            email=email,
            role="admin",
            first_name="admin",
            last_name="admin",
            is_active=True
        )
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()
        print(f"Admin account {email} created with password 'admin123'.")

if __name__ == "__main__":
    inject_admin()
