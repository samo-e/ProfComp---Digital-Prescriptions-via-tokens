from flask import Blueprint, render_template

views = Blueprint('views', __name__)

@views.route('/')
def home():
    return "index"

@views.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')