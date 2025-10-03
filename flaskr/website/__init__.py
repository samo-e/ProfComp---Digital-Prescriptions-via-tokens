
import os
from flask import Flask
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_wtf.csrf import generate_csrf

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'  # Change this in production!
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///asl_simulation.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Session configuration for better security
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour session timeout
    
    # CSRF Protection
    csrf = CSRFProtect(app)
    
    # import the database
    from .models import db, User
    db.init_app(app)
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # Expose csrf_token() in all templates
    @app.context_processor
    def inject_csrf_token():
        return dict(csrf_token=generate_csrf)
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from .views import views
    from .auth import auth

    # Register blueprints
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    # Check and initialize database if needed
    initialize_database(app)
    apply_light_migrations(app)

    return app

# Function to check for existing database and initialize if missing
def initialize_database(app):
    db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
    if not os.path.exists(db_path):
        from .models import db
        with app.app_context():
            db.create_all()

    return app


def apply_light_migrations(app):
    """Best-effort, idempotent column adds for SQLite dev DBs.
    Safe to run repeatedly; only adds columns if missing.
    """
    from sqlalchemy import text
    from .models import db
    with app.app_context():
        engine = db.engine
        with engine.begin() as conn:
            def column_exists(table_name: str, column_name: str) -> bool:
                rows = conn.execute(text(f"PRAGMA table_info({table_name})")).fetchall()
                # PRAGMA table_info returns: cid, name, type, notnull, dflt_value, pk
                return any(row[1] == column_name for row in rows)

            def add_column_if_missing(table_name: str, column_name: str, column_sql_type: str, default_value=None):
                if not column_exists(table_name, column_name):
                    conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_sql_type}"))
                    if default_value is not None:
                        conn.execute(text(f"UPDATE {table_name} SET {column_name} = :val"), {"val": default_value})

            # scenarios.question (TEXT)
            add_column_if_missing('scenarios', 'question', 'TEXT')
            # scenarios.is_active (INTEGER as boolean), default 1
            add_column_if_missing('scenarios', 'is_active', 'INTEGER', default_value=1)



