import dotenv
import os

config = dotenv.dotenv_values('.env')
API_KEY = config.get('API_KEY', '')
HEADERS = {'x-api-key': API_KEY}
RATE_LIMIT = 2  # seconds
