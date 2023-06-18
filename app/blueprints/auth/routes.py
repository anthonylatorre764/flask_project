from flask import request, render_template, url_for, redirect, flash
from app.blueprints.auth.forms import LoginForm, SignUpForm
from app import db
from . import auth
from app.models import User
from werkzeug.security import check_password_hash
from flask_login import login_user, logout_user, login_required
from sqlalchemy import func


# AUTHENTICATION
@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        email = form.email.data.lower()
        password = form.password.data
        queried_user = User.query.filter(User.email == email).first()
        if queried_user and check_password_hash(queried_user.password, password):
            login_user(queried_user)
            flash("You have successfully logged in!", "success")
            return redirect(url_for('main.home'))
        else:
            error = 'Invalid email or password'
            return render_template('login.html', form=form, error=error)
    else:
        return render_template('login.html', form=form)


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()
    if request.method == 'POST' and form.validate_on_submit():
        if form.password.data != form.confirm_pwd.data:
            flash("Those passwords do not match", "danger")
            error = 'Those passwords do not match'
            return render_template('signup.html', form=form, error=error)
        else:
            # This data is coming from the signup form
            user_data = {
                'first_name': form.first_name.data,
                'last_name': form.last_name.data,
                'email': form.email.data.lower(),
                'password': form.password.data
            }
            
            
            # Create user instance
            new_user = User()

            # Set user_data to our User attributes
            new_user.from_dict(user_data)

            # save to database
            db.session.add(new_user)
            db.session.commit()


            flash(f"Thank you for signing up {user_data['first_name']}!", 'success')
            return redirect(url_for('auth.login'))

    
    return render_template('signup.html', form=form)
    

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Successfully logged out!', 'success')
    return redirect(url_for('main.home'))