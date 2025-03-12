from data.file_io import read_json

def extract_match_uids(match_history_json):
    return [match['match_uid'] for match in match_history_json.get('match_history', [])]

def get_players_from_match(match_json):
    return [{'player_uid': p['player_uid'], 'nick_name': p['nick_name']} for p in match_json['match_details']['match_players']]