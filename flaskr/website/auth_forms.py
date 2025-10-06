from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    EmailField,
    PasswordField,
    SubmitField
)
from wtforms.validators import (
    Email,
    DataRequired,
    Optional,
    Length
)

class LoginForm(FlaskForm):
    email = EmailField(
        "Email Address",
        validators=[
            DataRequired(message="Email is required."),
            Email(message="Enter a valid email address.")
        ],
        render_kw={"placeholder": "you@example.com"}
    )
    
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(message="Password is required."),
            Length(min=6, message="Password must be at least 6 characters long.")
        ],
        render_kw={"placeholder": "Enter your password"}
    )
    
    remember = BooleanField(
        "Remember Me",
        validators=[Optional()]
    )
    
    submit = SubmitField("Login")


class ForgotPasswordForm(FlaskForm):
    email = EmailField(
        "Email Address",
        validators=[
            DataRequired(message="Please enter your email address."),
            Email(message="Enter a valid email address.")
        ],
        render_kw={"placeholder": "you@example.com"}
    )
    
    submit = SubmitField("Send Reset Link")
