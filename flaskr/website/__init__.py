# Import db for use in create_database
from .models import db
from flask import Flask 
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from os import path
import os 

DB_NAME = "database.bd"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'temporary'
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL', f'sqlite:///{DB_NAME}'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # import the database
    from .models import db

    db.init_app(app)

    from .views import views
    from .auth import auth

    # for view/auth.py routes
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/') 


    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
      
    create_database(app) 
       
    return app

def create_database(app): 
    # checks if db exists
    if not path.exists('website/' + DB_NAME):
            with app.app_context():
                db.create_all()
