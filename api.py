## test
import dotenv
import requests
import json
import pprint
import os
from tenacity import retry, stop_after_attempt, wait_exponential

config = dotenv.dotenv_values('.env')
API_KEY = config['API_KEY']
headers = {
    'x-api-key': API_KEY
}

@retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(5))
def get_heroes_info():
    url = 'https://marvelrivalsapi.com/api/v1/heroes'
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

# generate hero id to hero name mapping
def get_hero_id_to_name():
    heroes = open('heroes.json')
    heroes = json.load(heroes)
    hero_id_to_name = {}
    for hero in heroes:
        hero_id_to_name[hero['id']] = hero['name']
    return hero_id_to_name

@retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(5))
def update_user(player):
    url = f'https://marvelrivalsapi.com/api/v1/player/{player}/update'

    headers = {
    'X-API-Key': API_KEY
    }   

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    # print(response.json())
    return response.json()

@retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(5))
def get_stats(player):
    url = f'https://marvelrivalsapi.com/api/v1/player/{player}'
    output_file = f'stats_{player}.json'

    # check if output file exists
    if os.path.exists(output_file):
        # return the json data
        with open(output_file, 'r') as f:
            data = json.load(f)
            f.close()
        return data

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    # output to a json file called myData.json
    with open(output_file, 'w') as f:
        f.write(response.text)
        f.close()

    # print(response.json())
    return response.json()


@retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(5))
def get_match_history(player, gamemode='ranked', season=1) -> tuple:
    skip = 0
    output_file = f'match_history_{player}_{gamemode}_season-{season}.json'

    if os.path.exists(output_file):
        # return the json data
        with open(output_file, 'r') as f:
            data = json.load(f)
            f.close()
        return data, output_file
    
    #qp = 1, ranked = 0
    if gamemode == 'ranked':
        game_mode = 2
    else:
        game_mode = 1
    url = f'https://marvelrivalsapi.com/api/v1/player/{player}/match-history?season={season}&skip={skip}&game_mode={game_mode}'

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    return response.json(), output_file

    # print(response.json())

@retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(5))
def get_match_data(match_id) -> dict:
    url = f'https://marvelrivalsapi.com/api/v1/match/{match_id}'
    output_file = f'match_data_{match_id}.json'

    # check if output file exists
    if os.path.exists(output_file):
        # return the json data
        with open(output_file, 'r') as f:
            data = json.load(f)
            f.close()
        return data

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    # output to a json file called myData.json
    with open(output_file, 'w') as f:
        f.write(response.text)
        f.close()

    # print(response.json())
    return response.json()

def hero_to_id(hero_name):
    heroes = open('heroes.json')
    heroes = json.load(heroes)
    for hero in heroes:
        if hero['name'] == hero_name:
            return hero['id']
    return None

def id_to_hero(hero_id):
    heroes = open('heroes.json')
    heroes = json.load(heroes)
    for hero in heroes:
        if hero['id'] == hero_id:
            return hero['name']
    return None

def all_heroes() -> list[int]:
    heroes = open('heroes.json')
    heroes = json.load(heroes)
    hero_ids = []
    for hero in heroes:
        hero_ids.append(hero['id'])
    return hero_ids

def all_hero_names() -> list[str]:
    heroes = open('heroes.json')
    heroes = json.load(heroes)
    hero_names = []
    for hero in heroes:
        hero_names.append(hero['name'])
    return hero_names
