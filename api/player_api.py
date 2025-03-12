from api.api_client import make_request

def update_user(player_uid):
    """Updates player data."""
    url = f'https://marvelrivalsapi.com/api/v1/player/{player_uid}/update'
    return make_request(url)

def get_stats(player_uid):
    """Gets player statistics."""
    url = f'https://marvelrivalsapi.com/api/v1/player/{player_uid}'
    return make_request(url)
