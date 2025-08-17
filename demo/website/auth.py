from flask import Blueprint 

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return "login"

@auth.route('/home')
def home():
    return "home"

@auth.route('/logout')
def logout():
    return "logout"