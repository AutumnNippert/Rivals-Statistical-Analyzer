import requests
import json
from tenacity import retry, stop_after_attempt, wait_exponential
from config import HEADERS

@retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(5))
def make_request(url):
    """Make a request to the Marvel Rivals API."""
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()