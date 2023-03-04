import time 
import requests
from url import DOG_FOOD

def download_catalogue_page(url, no_pages):
    user_agent = {'User-agent': 'Mozilla/5.0'}
    for i in range(5):
        time.sleep(3)
        resp = requests.get(url + str(i + 1), headers=user_agent)
        with open(f"dog_food_{i + 1}.html", "wb+") as wfile:
            wfile.write(resp.content)
