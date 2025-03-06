# test
import dotenv
import requests
import os
import json

config = dotenv.dotenv_values('.env')
API_KEY = config['API_KEY']
headers = {
    'x-api-key': API_KEY
}

def update_user(player):
    url = f'https://marvelrivalsapi.com/api/v1/player/{player}/update'

    headers = {
    'X-API-Key': API_KEY
    }   

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
        return None

    # print(response.json())
    return response.json()

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

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
        return None
    
    # output to a json file called myData.json
    with open(output_file, 'w') as f:
        f.write(response.text)
        f.close()

    # print(response.json())
    return response.json()

def get_match_history(player, gamemode='ranked', season=1):
    skip = 0
    output_file = f'match_history_{player}_{gamemode}_season-{season}.json'

    if os.path.exists(output_file):
        # return the json data
        with open(output_file, 'r') as f:
            data = json.load(f)
            f.close()
        return data
    
    #qp = 1, ranked = 0
    if gamemode == 'ranked':
        game_mode = 0
    else:
        game_mode = 1
    url = f'https://marvelrivalsapi.com/api/v1/player/{player}/match-history?season={season}&skip={skip}&game_mode={game_mode}'

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
        return None
        
    # output to a json file called myData.json
    with open(output_file, 'w') as f:
        f.write(response.text)
        f.close()

    return response.json()

    # print(response.json())

def get_match_data(match_id):
    url = f'https://marvelrivalsapi.com/api/v1/match/{match_id}'
    output_file = f'match_data_{match_id}.json'

    # check if output file exists
    if os.path.exists(output_file):
        # return the json data
        with open(output_file, 'r') as f:
            data = json.load(f)
            f.close()
        return data

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
        exit(1)
    # output to a json file called myData.json
    with open(output_file, 'w') as f:
        f.write(response.text)
        f.close()

    # print(response.json())
    return response.json()

"""
 "match_details": {
        "match_uid": "6713456_1740417082_272_11001_10",
        "game_mode": {
            "game_mode_id": 1,
            "game_mode_name": "Quick Play"
        },
        "replay_id": "10892130651",
        "mvp_uid": 237881571,
        "mvp_hero_id": 1047,
        "svp_uid": 132003806,
        "svp_hero_id": 1027,
        "dynamic_fields": {},
        "match_players": [
        """


def get_players_from_match(match_json):
    players = []
    for player in match_json['match_details']['match_players']:
        players.append({'player_uid': player['player_uid'], 'nick_name': player['nick_name']})
    return players

def get_match_uids_from_match_history(match_history_json):
    match_uids = []
    for match in match_history_json['match_history']:
        match_uids.append(match['match_uid'])
    return match_uids


# PLAYER = '1403392757'
# update_user(PLAYER)
# get_stats(PLAYER, 'stats2.json')
# get_match_history(PLAYER)
# get_match_data('6713456_1740417082_272_11001_10', 'match_data.json')



# json_data = json.load(open('match_data.json'))
# players = get_players_from_match(json_data)
# print(json.dumps(players, indent=4))

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

def get_unique(json):
    unique = []
    for match in json:
        for player in match:
            if player not in unique:
                unique.append(player)
    return unique

unique = get_unique(json.load(open('allPlayers.json')))
print(json.dumps(unique, indent=4))

# in this directory, there are a bunch of files are stats_playeruid.json

successes = []
for player in unique:
    if os.path.exists(f'stats_{player['player_uid']}.json'):
        print("Player already found; Skipping...")
        pass
    print("Updating Player: ", player['nick_name'])
    res = update_user(player['player_uid'])
    if res:
        successes.append(player)

for player in successes:
    print("Getting Stats for Player: ", player['nick_name'])
    get_stats(player['player_uid'])