from flask import request, render_template, flash, session, redirect, url_for
import requests
from app.blueprints.main.forms import PokemonForm
from . import main
from flask_login import login_required, current_user
from app.models import Pokemon, Team
from app import db


@main.route('/')
@main.route('/home')
def home():
    return render_template('home.html')


@main.route('/pokemon', methods=['GET', 'POST'])
@login_required
def pokemon():
    form = PokemonForm()
    if request.method == 'POST':
        pokemon_name = request.form.get('pokemon_name')
        pokemon_dict = {}

        url = f'https://pokeapi.co/api/v2/pokemon/{pokemon_name.lower()}'
        response = requests.get(url)

        try:
            session['pokemon_id'] = response.json()['id']

            name = response.json()['forms'][0]['name']
            pokemon_dict['name'] = name
            session['pokemon_name'] = name

            sprite = response.json()['sprites']['front_default']
            pokemon_dict['sprite'] = sprite
            session['pokemon_sprite'] = sprite

            hp = response.json()['stats'][0]['base_stat']
            pokemon_dict['hp'] = hp
            session['pokemon_hp'] = hp

            attack = response.json()['stats'][1]['base_stat']
            pokemon_dict['attack'] = attack
            session['pokemon_attack'] = attack

            defense = response.json()['stats'][2]['base_stat']
            pokemon_dict['defense'] = defense
            session['pokemon_defense'] = defense


            caught_flag = False
            # query the pokemon from database
            current_pokemon = Pokemon.query.filter_by(id=session['pokemon_id']).first()

            if current_pokemon in current_user.team:
                caught_flag = True

            return render_template('pokemon.html', pokemon_dict=pokemon_dict, form=form, caught_flag=caught_flag)
        except:
            flash("That name does not exist", 'danger')
            return render_template('pokemon.html', form=form)
        
    return render_template('pokemon.html', form=form)



@main.route('/catch_pokemon', methods=['GET', 'POST'])
def catch_pokemon():
    # query the pokemon from database
    current_pokemon = Pokemon.query.filter_by(id=session['pokemon_id']).first()


    pokemon_match = Pokemon.query.filter_by(id=session['pokemon_id']).all()
    
    if not pokemon_match:
        pokemon_data = {
            'id': session['pokemon_id'],
            'name': session['pokemon_name'],
            'sprite': session['pokemon_sprite'],
            'hp': session['pokemon_hp'],
            'attack': session['pokemon_attack'],
            'defense': session['pokemon_defense']
        }

        # Create pokemon instance
        new_pokemon = Pokemon()

        # Set pokemon_data to our Pokemon attributes
        new_pokemon.from_dict(pokemon_data)

        # save to database
        db.session.add(new_pokemon)
        db.session.commit()


    if len(current_user.team) >= 5:
        flash("Your team is full (5 pokemon limit)", "danger")
        return redirect(url_for('main.pokemon'))
    elif current_pokemon in current_user.team:
        flash(f"{session['pokemon_name']} is already on your team", "danger")
        return redirect(url_for('main.pokemon'))
    else:
        # query the pokemon from database
        current_pokemon = Pokemon.query.filter_by(id=session['pokemon_id']).first()

        # add pokemon to team
        current_user.team.append(current_pokemon)
        db.session.commit()

        flash(f"Successfully added {session['pokemon_name']} to your team", "success")
        

        return redirect(url_for('main.pokemon'))


@main.route('/remove_pokemon', methods=['GET', 'POST'])
def remove_pokemon():
    pass