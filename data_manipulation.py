import json

from api import get_match_data

def get_unique_players(json):
    unique = []
    for match in json:
        for player in match:
            if player not in unique:
                unique.append(player)
    return unique


def get_players_from_match_history(match_history_json):
    match_uids = get_match_uids_from_match_history(match_history_json)
    print(json.dumps(match_uids, indent=4))

    # for each match, get the match data
    allPlayers = []
    for match in match_uids:
        data = get_match_data(match)
        players = get_players_from_match(data)
        allPlayers.append(players)

    write_file = 'allPlayers.json'
    with open(write_file, 'w') as f:
        f.write(json.dumps(allPlayers, indent=4))
        f.close()
    print(f'Wrote all players to {write_file}')

    return allPlayers

def get_players_from_match(match_json):
    players = []
    for player in match_json['match_details']['match_players']:
        players.append({'player_uid': player['player_uid'], 'nick_name': player['nick_name']})
    return players

def get_uids_from_player_files():
    # get all stats_uid.json files
    import os
    files = os.listdir()
    stats_files = []
    for file in files:
        if 'stats_' in file:
            stats_files.append(file)
    uids = []
    for file in stats_files:
        with open(file, 'r') as f:
            data = json.load(f)
            f.close()
        uids.append(data['uid'])
    return uids
    

def get_match_uids_from_match_history(match_history_json):
    match_uids = []
    for match in match_history_json['match_history']:
        match_uids.append(match['match_uid'])
    return match_uids
