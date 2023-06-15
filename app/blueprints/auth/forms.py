from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, SubmitField, StringField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()], render_kw={'autofocus': True})
    password = PasswordField('Password', validators=[DataRequired()])
    submit_btn = SubmitField('Login')


class SignUpForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()], render_kw={'autofocus': True})
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_pwd = PasswordField('Confirm Pwd', validators=[DataRequired()])
    submit_btn = SubmitField('Sign Up')