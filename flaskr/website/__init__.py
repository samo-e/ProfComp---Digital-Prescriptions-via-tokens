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
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'asl_simulation.db'))
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    print(f"DEBUG: Database path configured as: {db_path}")
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

    # Create database tables on startup
    with app.app_context():
        db.create_all()
        print(f"DEBUG: Database tables created at: {app.config['SQLALCHEMY_DATABASE_URI']}")

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
