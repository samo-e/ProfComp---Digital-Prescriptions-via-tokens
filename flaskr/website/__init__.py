from flask import Flask
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'  # Change this in production!
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///asl_simulation.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
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
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from .views import views
    from .auth import auth

    # for view/auth.py routes
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/') 
    
    with app.app_context():
        db.create_all()
    
    return app