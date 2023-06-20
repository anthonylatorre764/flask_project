from flask import request, render_template, flash, session, redirect, url_for
import random as r
import requests
from app.blueprints.main.forms import PokemonForm
from . import main
from flask_login import login_required, current_user
from app.models import Pokemon, User
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



@main.route('/catch_pokemon/<int:pokemon_id>')
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


@main.route('/remove_pokemon/<int:pokemon_id>')
def remove_pokemon(pokemon_id):
    # query the pokemon from database
    pokemon = Pokemon.query.get(pokemon_id)
  
    # remove pokemon from team
    current_user.team.remove(pokemon)
    db.session.commit()


    flash(f"Successfully removed {pokemon.name} from your team", "success")

    return redirect(url_for('main.team'))


@main.route('/team')
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


@main.route('/search_users')
def search_users():
    user_list = User.query.all()

    user_list.remove(current_user)

    return render_template('users.html', user_list=user_list)


@main.route('/battle/<int:user_id>')
def battle(user_id):
    opponent = User.query.get(user_id)
    session['opponent_id'] = user_id
    
    if opponent.team:
        away_pokemon = opponent.team[r.randint(0, (len(opponent.team)-1))]
    else:
        flash("Your opponent's team is empty. You can battle them once they catch a pokemon.", "danger")
        return redirect(url_for('main.search_users'))
    
    if current_user.team:
        home_pokemon = current_user.team[r.randint(0, (len(current_user.team)-1))]
    else:
        flash("Your team is empty. You can battle another user once you catch a pokemon.", "danger")
        return redirect(url_for('main.pokemon'))
    


    return render_template('battle.html', away_pokemon=away_pokemon, home_pokemon=home_pokemon, opponent=opponent)



@main.route('/do_battle/<int:home_id>/<int:away_id>')
def do_battle(home_id, away_id):
    opponent = User.query.get(session['opponent_id'])

    home_pokemon = Pokemon.query.get(home_id)
    away_pokemon = Pokemon.query.get(away_id)

    # Battle Calculation
    home_hp = home_pokemon.hp
    away_hp = away_pokemon.hp

    while home_hp > 0 and away_hp > 0:
        # away attacks first
        attack_outcome = home_pokemon.defense - away_pokemon.attack
        if attack_outcome < 0:
            home_hp -= abs(attack_outcome)

        attack_outcome = away_pokemon.defense - home_pokemon.attack
        if attack_outcome < 0:
            away_hp -= abs(attack_outcome)

    
    if home_hp <= 0:
        flash(f"{away_pokemon.name} won the battle!", "success")
    elif away_hp <= 0:
        flash(f"{home_pokemon.name} won the battle!", "success")


    battled_flag = True

    return render_template('battle.html', away_pokemon=away_pokemon, home_pokemon=home_pokemon, opponent=opponent, battled_flag=battled_flag)
