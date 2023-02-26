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
    # Logic for accessing all product links from catalogue
    with open("../dog_food_1.html", "rb") as rfile:
        soup = BeautifulSoup(rfile.read(), 'html.parser')
        url_list = soup.select("div.kib-product-card__canvas > a[href]")
        for url in url_list:
            print(url['href'])
    soup = BeautifulSoup(requests.get("https://www.chewy.com/purina-pro-plan-adult-sensitive-skin/dp/128666", headers=user_agent).content, 'html.parser')
    print(soup.find("h1").text)
    # Category
    for item in soup.select("li.kib-breadcrumbs-item"):
        print(item.find("a").text)
    # Prices
    print(soup.select("div[data-testid=advertised-price]")[0].find(string=True))
    print(soup.select("div[data-testid=strike-through-price]")[0].find(string=True))
    # Ingredients
    print(soup.select("section#INGREDIENTS-section > p")[0].find(string=True))
    # Nutritional Information
    print(soup.select("section#GUARANTEED_ANALYSIS-section > div.styles_markdownTable__Mtq7h")[0].text)
    print(soup.select("a.styles_brandLink__MdoyO")[0].find(string=True))



if __name__ == "__main__":
    main()