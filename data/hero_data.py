import json
from pathlib import Path

HEROES_FILE = Path("data/heroes.json")

def load_heroes():
    """Loads the list of heroes from heroes.json."""
    if HEROES_FILE.exists():
        with open(HEROES_FILE, "r") as f:
            return json.load(f)
    raise FileNotFoundError(f"Hero file not found: {HEROES_FILE}")

def all_hero_ids():
    """Returns a list of all hero IDs."""
    heroes = load_heroes()
    return [hero['id'] for hero in heroes]

def all_hero_names():
    """Returns a list of all hero names."""
    heroes = load_heroes()
    return [hero['name'] for hero in heroes]

def hero_to_id(hero_name):
    """Converts a hero name to its corresponding ID."""
    heroes = load_heroes()
    for hero in heroes:
        if hero['name'].lower() == hero_name.lower():
            return hero['id']
    return None

def id_to_hero(hero_id):
    """Converts a hero ID to its corresponding name."""
    heroes = load_heroes()
    for hero in heroes:
        if hero['id'] == hero_id:
            return hero['name']
    return None
