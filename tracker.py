# hit https://api.tracker.gg/api/v2/marvel-rivals/standard/matches/ign/Card1gan?mode=competitive&season=3&next=2

import requests
import json

try:
    res = requests.get('https://api.tracker.gg/api/v2/marvel-rivals/standard/matches/ign/Card1gan?mode=competitive&season=3&next=2')
    res.raise_for_status()
except requests.exceptions.HTTPError as err:
    print(err)
    exit(1)
data = res.json()
print(json.dumps(data, indent=4))