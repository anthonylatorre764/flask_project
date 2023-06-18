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
            id = response.json()['id']
            pokemon_dict['id'] = id
            session['pokemon_id'] = id

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



@main.route('/catch_pokemon/<int:pokemon_id>', methods=['GET', 'POST'])
def catch_pokemon(pokemon_id):

    pokemon_match = Pokemon.query.filter_by(id=pokemon_id).all()
    
    if not pokemon_match:
        pokemon_data = {
            'id': pokemon_id,
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



    # query the pokemon from database
    pokemon = Pokemon.query.get(pokemon_id)


    if len(current_user.team) >= 5:
        flash("Your team is full (5 pokemon limit)", "danger")
        return redirect(url_for('main.pokemon'))
    else:
        # add pokemon to team
        current_user.team.append(pokemon)
        db.session.commit()

        flash(f"Successfully added {pokemon.name} to your team", "success")
        

        return redirect(url_for('main.pokemon'))


@main.route('/remove_pokemon/<int:pokemon_id>', methods=['GET', 'POST'])
def remove_pokemon(pokemon_id):
    # query the pokemon from database
    pokemon = Pokemon.query.get(pokemon_id)
  
    # remove pokemon from team
    current_user.team.remove(pokemon)
    db.session.commit()


    flash(f"Successfully removed {pokemon.name} from your team", "success")

    return redirect(url_for('main.team'))


@main.route('/team', methods=['GET', 'POST'])
def team():
    team_list = []

    if current_user.team:
        for i in range(len(current_user.team)):
            team_list.append({})
            team_list[i]['id'] = current_user.team[i].id
            team_list[i]['name'] = current_user.team[i].name
            team_list[i]['sprite'] = current_user.team[i].sprite
            team_list[i]['hp'] = current_user.team[i].hp
            team_list[i]['attack'] = current_user.team[i].attack
            team_list[i]['defense'] = current_user.team[i].defense
        
        return render_template('team.html', team_list=team_list)
    else:
        flash("Your team is empty. Go catch some pokemon!", "warning")
    

    return render_template('team.html')



# team_list [
#     {
#         'name': 'pikachu',
#         'sprite': 'https://testestes7565test',
#         'hp': 50,
#         'attack': 39,
#         'defense': 20
#     },
#     {
#         'name': 'ditto',
#         'sprite': 'https://test8967estestest',
#         'hp': 70,
#         'attack': 38,
#         'defense': 90
#     }
# ]