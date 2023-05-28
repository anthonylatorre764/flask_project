from flask import request, render_template
import requests
from app.forms import PokemonForm
from app import app


@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/pokemon', methods=['GET', 'POST'])
def pokemon():
    form = PokemonForm()
    if request.method == 'POST':
        pokemon_name = request.form.get('pokemon_name')
        pokemon_dict = {}

        url = f'https://pokeapi.co/api/v2/pokemon/{pokemon_name.lower()}'
        response = requests.get(url)

        # try:
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
        # except:
        #     return 'That name does not exist'
        
    return render_template('pokemon.html', form=form)