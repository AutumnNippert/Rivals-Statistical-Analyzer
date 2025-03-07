## test
import dotenv
import requests
import json
import pprint

config = dotenv.dotenv_values('.env')
API_KEY = config['API_KEY']
headers = {
    'x-api-key': API_KEY
}


def get_heroes_info():
    url = 'https://marvelrivalsapi.com/api/v1/heroes'
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
        return None
    
    return response.json()

# generate hero id to hero name mapping
def get_hero_id_to_name():
    heroes = open('heroes.json')
    heroes = json.load(heroes)
    hero_id_to_name = {}
    for hero in heroes:
        hero_id_to_name[hero['id']] = hero['name']
    return hero_id_to_name

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

# print(all_heroes())