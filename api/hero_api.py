from api.api_client import make_request
import json

def get_heroes_info():
    """Fetches hero data from API."""
    url = 'https://marvelrivalsapi.com/api/v1/heroes'
    return make_request(url)
