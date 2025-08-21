from flask import Blueprint, render_template

auth = Blueprint('auth', __name__)

@auth.route('/home')
def home():
    return "home"

@auth.route('/login')
def login():
    valid_password = True
    return render_template("auth/login.html", valid_password=valid_password)

@auth.route('/signup')
def signup():
    valid_password = True
    return render_template("auth/signup.html", valid_password=valid_password)

@auth.route('/logout')
def logout():
    return "logout"

