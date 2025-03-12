import json
from pathlib import Path

RAW_DATA_DIR = Path("data/raw/")
PROCESSED_DATA_DIR = Path("data/processed/")

def read_json(file_name):
    """Reads a JSON file from the raw data directory."""
    file_path = RAW_DATA_DIR / file_name
    if file_path.exists():
        with open(file_path, 'r') as file:
            return json.load(file)
    return None

def write_json(file_name, data, processed=False):
    """Writes JSON data to either raw or processed directory."""
    directory = PROCESSED_DATA_DIR if processed else RAW_DATA_DIR
    file_path = directory / file_name
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)