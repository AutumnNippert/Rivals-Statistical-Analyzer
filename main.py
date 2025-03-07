from api import *
from data_manipulation import *
import time
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
RATE_LIMIT = 2  # seconds

def get_match_uids():
    player_uids = get_uids_from_player_files()

    match_uids_set= set()
    match_data_file = 'match_uids.json' # stores just a list of match_uids and if it was ranked or not
    # { 'match_uid': '1234_1234_1234_1234_1234', 'gamoemode': 2 } # 2 is ranked, 1 is quick play

    curr_uids = []
    # if doesnt exist, create it
    if Path(match_data_file).exists():
        with open(match_data_file, 'r') as f:
            try:
                curr_uids = json.load(f)
                match_uids_set.update(entry['match_uid'] for entry in curr_uids)  # Extract existing match_uids
            except json.JSONDecodeError:
                logging.error("Failed to parse JSON file, resetting...")
                curr_uids = []

    gamemode = 'ranked'

    try:
        for player in player_uids:
            logging.info(f"Getting Match History for player UID={player}")
            try:
                res, output_file = get_match_history(player, gamemode)
            except Exception as e:
                logging.error(f"Error getting match history for {player}: {e}, skipping")
                continue
            if res:
                logging.info(f"Got Match History for player UID={player}")
                new_match_uids = get_match_uids_from_match_history(res)
                
                # Only add new UIDs
                unique_new_uids = [uid for uid in new_match_uids if uid not in match_uids_set]
                match_uids_set.update(unique_new_uids)

                # Append new entries
                for uid in unique_new_uids:
                    curr_uids.append({'match_uid': uid, 'gamemode': gamemode})

            time.sleep(RATE_LIMIT)  # Respect rate limit
    except Exception as e:
        logging.error(f"Error getting match history for {player}: {e}, skipping")
    finally:
        # Write the updated match UIDs to the file
        with open(match_data_file, 'w') as f:
            json.dump(curr_uids, f, indent=4)

    # Print the final list of match UIDs
    print(json.dumps(list(match_uids_set), indent=4))

def get_match_data_files(uids:list[int]):
    for uid in uids:
        continued = False
        logging.info(f"Getting Match Data for match UID={uid}")
        try:
            output_file = f'match_data_{uid}.json'
            if Path(output_file).exists():
                logging.info(f"Match data for {uid} already exists, skipping.")
                continued = True
                continue
            res = get_match_data(uid)
            #write to file
            with open(output_file, 'w') as f:
                json.dump(res, f, indent=4)
        except Exception as e:
            logging.error(f"Error getting match data for {uid}: {e}, skipping")
            continue
        finally:
            if not continued:
                time.sleep(RATE_LIMIT)

if __name__ == '__main__':
    # match_uids = set()
    # with open('match_uids.json', 'r') as f:
    #     data = json.load(f)
    #     match_uids.update(entry['match_uid'] for entry in data)
    # get_match_data_files(list(match_uids))

