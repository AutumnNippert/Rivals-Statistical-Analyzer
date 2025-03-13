def get_match_uids_from_match_history(match_history_json):
    """Extracts match UIDs from match history JSON."""
    return [match['match_uid'] for match in match_history_json.get('match_history', [])]

def get_match_composition(match_json):
    """Extracts match composition and determines if team 1 won."""
    players = []
    for player in match_json['match_details']['match_players']:
        player_heroes = sorted(player['player_heroes'], key=lambda x: x['play_time'], reverse=True)
        if player_heroes:
            players.append({'player_uid': player['player_uid'], 'nick_name': player['nick_name'], 'hero_id': player_heroes[0]['hero_id']})

    team_1_won = match_json['match_details']['match_players'][0]['is_win']
    return players, team_1_won

def get_players_from_match(match_json):
    """Extracts all players from a match JSON."""
    return [{'player_uid': p['player_uid'], 'nick_name': p['nick_name']} for p in match_json['match_details']['match_players']]
