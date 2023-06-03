from flask import request, render_template, url_for, redirect, flash
import requests
from app.forms import PokemonForm, LoginForm, SignUpForm
from app import app, db
from app.models import User
from werkzeug.security import check_password_hash
from flask_login import login_user, logout_user, current_user, login_required


@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/pokemon', methods=['GET', 'POST'])
@login_required
def pokemon():
    form = PokemonForm()
    if request.method == 'POST':
        pokemon_name = request.form.get('pokemon_name')
        pokemon_dict = {}

        url = f'https://pokeapi.co/api/v2/pokemon/{pokemon_name.lower()}'
        response = requests.get(url)

        try:
            name = response.json()['forms'][0]['name']
            pokemon_dict['name'] = name

            abilities_list = response.json()['abilities']

            index = 0
            while index < len(abilities_list):
                if index == 2:
                    break
                ability_name = response.json()['abilities'][index]['ability']['name']
                pokemon_dict['ability_' + str(index+1)] = ability_name
                index += 1
            
            if index == 1:
                pokemon_dict['ability_2'] = 'None'

            base_xp = response.json()['base_experience']
            pokemon_dict['base_xp'] = base_xp

            sprite = response.json()['sprites']['front_default']
            pokemon_dict['sprite'] = sprite

            return render_template('pokemon.html', pokemon_dict=pokemon_dict, form=form)
        except:
            return 'That name does not exist'
        
    return render_template('pokemon.html', form=form)


# AUTHENTICATION
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        email = form.email.data.lower()
        password = form.password.data
        queried_user = User.query.filter(User.email == email).first()
        if queried_user and check_password_hash(queried_user.password, password):
            login_user(queried_user)
            flash("You have successfully logged in!", "success")
            return redirect(url_for('home'))
        else:
            error = 'Invalid email or password'
            return render_template('login.html', form=form, error=error)
    else:
        return render_template('login.html', form=form)


@app.route('/signup', methods=['GET', 'POST'])
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
            return redirect(url_for('login'))

    
    return render_template('signup.html', form=form)
    


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Successfully logged out!', 'warning')
    return redirect(url_for('home'))