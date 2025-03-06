# test
import dotenv
import requests

config = dotenv.dotenv_values('.env')
API_KEY = config['API_KEY']

#hit GET https://public-api.tracker.gg/v2/rivals/standard/profile/steam/Card1gan
url = 'https://marvelrivalsapi.com/api/v1/player/Card1gan'

headers = {
    'X-API-Key': API_KEY
}

response = requests.get(url, headers=headers)
print(response.json())