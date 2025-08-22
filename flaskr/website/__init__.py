from flask import Flask 
from flask_sqlalchemy import SQLAlchemy
from os import path
import os 

db = SQLAlchemy()
DB_NAME = "database.bd"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'temporary'
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///site.db')
    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/') 

    from .models import User

    create_database(app)    

    return app

def create_database(app): 
    # checks if db exists
    if not path.exists('website/' + DB_NAME):
            with app.app_context():
                db.create_all()
     