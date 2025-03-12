from api.api_client import make_request

def get_match_history(player_uid, gamemode='ranked', season=1):
    """Get match history for a player."""
    game_mode = 2 if gamemode == 'ranked' else 1
    url = f'https://marvelrivalsapi.com/api/v1/player/{player_uid}/match-history?season={season}&game_mode={game_mode}'
    return make_request(url)

def get_match_data(match_id):
    """Get match data for a match."""
    url = f'https://marvelrivalsapi.com/api/v1/match/{match_id}'
    return make_request(url)
