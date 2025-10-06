import os
from flask import Flask
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_minify import Minify


def create_app():
    app = Flask(__name__)

    Minify(app=app, html=True, js=True, cssless=True)

    app.config["SECRET_KEY"] = (
        "dev-secret-key-change-in-production"  # Change this in production!
    )
    import os
    db_path = os.path.join(os.path.dirname(__file__), '..', 'asl_simulation.db')
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    print(f"DEBUG: Database path configured as: {db_path}")
    print(f"DEBUG: Absolute database path: {os.path.abspath(db_path)}")
    print(f"DEBUG: Database file exists: {os.path.exists(db_path)}")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Session configuration for better security
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["PERMANENT_SESSION_LIFETIME"] = 3600  # 1 hour session timeout

    # CSRF Protection
    csrf = CSRFProtect(app)

    # import the database
    from .models import db, User, Patient

    db.init_app(app)

    # Auto-seed database on startup (simplified approach)
    with app.app_context():
        # Create all database tables first
        db.create_all()
        
        # Check if database is empty and seed if needed
        print(f"DEBUG: Seeding process - Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
        print(f"DEBUG: Seeding process - Working directory: {os.getcwd()}")
        user_count = User.query.count()
        print(f"DEBUG: Seeding process - User count: {user_count}")
        
        if user_count == 0:
            print("Database is empty, auto-seeding...")
            try:
                # Seed users
                from init_users import init_users
                init_users(auto_mode=True)
                
                # Verify users were created
                user_count = User.query.count()
                if user_count > 0:
                    print(f"Auto-seeding successful! ({user_count} users created)")
                else:
                    print("ERROR: Auto-seeding failed - no users created!")
                    
                # Seed patient data
                from init_data import init_asl_database
                init_asl_database()
                
                patient_count = Patient.query.count()
                if patient_count > 0:
                    print(f"Patient data seeded! ({patient_count} patients created)")
                else:
                    print("ERROR: No patients created!")
                    
            except Exception as e:
                print(f"Auto-seeding error: {e}")
        else:
            print(f"Database already has {user_count} users, skipping auto-seed")

    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "info"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from .views import views
    from .auth import auth

    # Register blueprints
    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")

    # Check and initialize database if needed
    initialize_database(app)

    # Add custom template filters
    @app.template_filter("nl2br")
    def nl2br_filter(text):
        """Convert newlines to HTML breaks"""
        if not text:
            return text
        return text.replace("\n", "<br>")

    return app


# Function to check for existing database and initialize if missing
def initialize_database(app):
    db_path = app.config["SQLALCHEMY_DATABASE_URI"].replace("sqlite:///", "")
    if not os.path.exists(db_path):
        from .models import db

        with app.app_context():
            db.create_all()

    return app
