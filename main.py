import time
import logging
import argparse
from pathlib import Path

from config import RATE_LIMIT
from api.player_api import update_user, get_stats
from api.match_api import get_match_history, get_match_data
from data.file_io import read_json, write_json
from data.match_extraction import get_match_uids_from_match_history
from utils.logging_config import setup_logging

setup_logging()

def process_stats_files():
    """Processes all 'stats_*' files in the current directory."""
    for file_path in Path('.').glob('stats_*.json'):
        time.sleep(RATE_LIMIT)
        player_uid = file_path.stem.split('_')[1]

        logging.info(f"Fetching match history for player UID={player_uid}")
        history = get_match_history(player_uid)
        if not history:
            logging.error(f"Failed to retrieve match history for {player_uid}")
            continue
        
        match_uids = get_match_uids_from_match_history(history)
        for match_uid in match_uids:
            match_data_file = f"match_data_{match_uid}.json"
            if Path(match_data_file).exists():
                logging.info(f"Skipping {match_data_file}, already exists.")
                continue

            logging.info(f"Fetching match data for {match_uid}")
            match_data = get_match_data(match_uid)
            if match_data:
                write_json(match_data_file, match_data)

def update_single_player(player_uid):
    """Updates a single player's stats and retrieves match history."""
    logging.info(f"Updating data for player UID={player_uid}")

    update_user(player_uid)
    stats = get_stats(player_uid)
    if not stats:
        logging.error(f"Failed to retrieve stats for {player_uid}")
        return

    history = get_match_history(player_uid)
    if not history:
        logging.error(f"Failed to retrieve match history for {player_uid}")
        return

    match_uids = get_match_uids_from_match_history(history)
    for match_uid in match_uids:
        match_data_file = f"match_data_{match_uid}.json"
        if Path(match_data_file).exists():
            logging.info(f"Skipping {match_data_file}, already exists.")
            continue

        logging.info(f"Fetching match data for {match_uid}")
        match_data = get_match_data(match_uid)
        if match_data:
            write_json(match_data_file, match_data)

def main():
    """Main function to handle CLI arguments and execute commands."""
    parser = argparse.ArgumentParser(description="Process player stats and match data.")
    parser.add_argument("--player", "-p", type=str, help="Process a specific player UID.")
    parser.add_argument("--all", "-a", action="store_true", help="Process all player stats files.")

    args = parser.parse_args()

    if args.player:
        update_single_player(args.player)
    elif args.all:
        process_stats_files()
    else:
        parser.print_help()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.critical(f"Fatal error: {e}", exc_info=True)
