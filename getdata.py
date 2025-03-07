# test
import dotenv
import requests
import os
import json
import time
import logging
from pathlib import Path

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
        return None
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

# unique = get_unique(json.load(open('allPlayers.json')))
# print(json.dumps(unique, indent=4))

# # in this directory, there are a bunch of files are stats_playeruid.json

# successes = []
# for player in unique:
#     if os.path.exists(f'stats_{player['player_uid']}.json'):
#         print("Player already found; Skipping...")
#         pass
#     print("Updating Player: ", player['nick_name'])
#     res = update_user(player['player_uid'])
#     if res:
#         successes.append(player)

# for player in successes:
#     print("Getting Stats for Player: ", player['nick_name'])
#     get_stats(player['player_uid'])

# get player match histories from stats files

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def process_stats_files():
    """
    Process all 'stats_*' files in the current directory.
    For each player in the stats file, get their match history and match data.
    """
    for file_path in Path('.').glob('stats_*.json'):  # Matches 'stats_*' files
        time.sleep(1)  # Rate limiting
        player = file_path.stem.split('_')[1]  # Extract player UID from filename

        logging.info(f"Getting Match History for player UID={player}")
        try:
            history = get_match_history(player)
            time.sleep(1)  # Rate limiting
        except Exception as e:
            logging.error(f"Error getting match history for {player}: {e}, skipping")
            continue

        # Extract UIDs from match history
        try:
            uids = get_match_uids_from_match_history(history)
            time.sleep(1)  # Rate limiting
        except Exception as e:
            logging.error(f"Error getting match UIDs for {player}: {e}, skipping")
            continue

        # Fetch match data for each UID
        for uid in uids:
            match_data_file = f"match_data_{uid}.json"
            if Path(match_data_file).exists():
                logging.info(f"Match data for {uid} already exists, skipping.")
                continue

            logging.info(f"Getting Match Data for {uid}")
            try:
                get_match_data(uid)
                time.sleep(1)  # Rate limiting
            except Exception as e:
                logging.error(f"Error getting match data for {uid}: {e}, skipping")
                continue

        logging.info(f"Finished processing {file_path.name}")

if __name__ == "__main__":
    try:
        process_stats_files()
    except Exception as e:
        logging.critical(f"Fatal error: {e}", exc_info=True)
