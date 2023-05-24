from flask import Flask, request, render_template
import requests

app = Flask(__name__)


@app.route('/home')
def home():
    return '<h2>Hello, Welcome to the Pokemon Stats Homepage!</h2>'



@app.route('/pokemon', methods=['GET', 'POST'])
def pokemon():
    if request.method == 'POST':
        pokemon_name = request.form.get('pokemon_name')
        pokemon_id = request.form.get('pokemon_id')
        info_list = []

        # pokemon stats
        url = f'https://pokeapi.co/api/v2/pokemon/{pokemon_name.lower()}'
        response = requests.get(url)

        # pokemon sprites
        url2 = f'https://pokeapi.co/api/v2/pokemon-form/{pokemon_id}/'
        response2 = requests.get(url2)

        # try:
        name = response.json()['forms'][0]['name']
        info_list.append(name)

        ability_0 = response.json()['abilities'][0]['ability']['name']
        info_list.append(ability_0)

        ability_1 = response.json()['abilities'][1]['ability']['name']
        info_list.append(ability_1)

        base_xp = response.json()['base_experience']
        info_list.append(base_xp)

        sprite_img = response2.json()['sprites']['front_default']
        info_list.append(sprite_img)

        return render_template('pokemon.html', info_list=info_list)
        # except:
        #     return 'That name or id does not exist'
        
    return render_template('pokemon.html')