import time 
import requests

def download_catalogue_page(animal, no_pages):
    user_agent = {'User-agent': 'Mozilla/5.0'}
    for i in range(no_pages):
        time.sleep(3)
        resp = requests.get(animal.get("url") + str(i + 1), headers=user_agent)
        with open(f"{animal.get('htmfilename')}{i + 1}.html", "wb+") as wfile:
            print(f"Writing file: {i}")
            wfile.write(resp.content)
