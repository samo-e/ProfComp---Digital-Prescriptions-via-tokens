from flask import Flask 

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'temporary'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///asl_simulation.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # import the database
    from .models import db
    db.init_app(app)

    from .views import views
    from .auth import auth

    # for view/auth.py routes
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/') 
    
    with app.app_context():
        db.create_all()
    
    return app

