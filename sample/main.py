from bs4 import BeautifulSoup
import requests
import pandas as pd
import time
from url import DOG_FOOD, CAT_FOOD

def main():
    user_agent = {'User-agent': 'Mozilla/5.0'}
    for i in range(5):
        time.sleep(3)
        resp = requests.get(DOG_FOOD + str(i + 1), headers=user_agent)
        with open(f"dog_food_{i + 1}.html", "wb+") as wfile:
            wfile.write(resp.content)



if __name__ == "__main__":
    main()