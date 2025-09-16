from flask import Blueprint, render_template

auth = Blueprint('auth', __name__)

@auth.route('/home')
def home():
    return "home"

@auth.route('/login')
def login():
    return render_template("auth/login.html")

@auth.route('/signup')
def signup():
    return render_template("auth/signup.html")

@auth.route('/logout')
def logout():
    return "logout"

