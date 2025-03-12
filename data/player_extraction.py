def get_unique_players(matches):
    """Extracts unique players from a list of matches."""
    unique_players = set()
    for match in matches:
        for player in match:
            unique_players.add(player['player_uid'])
    return list(unique_players)

def get_players_from_match(match_json):
    """Extracts all players from a match JSON."""
    return [{'player_uid': p['player_uid'], 'nick_name': p['nick_name']} for p in match_json['match_details']['match_players']]
