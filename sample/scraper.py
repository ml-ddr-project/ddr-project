# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import requests
from pymongo import MongoClient
from pymongo.errors import BulkWriteError

class ChewyScraper:
    def __init__(self, *args, **kwargs) -> None:
        for user_agent in args:
            self.user_agent = user_agent
        else:
            self.user_agent = {'User-agent': "Mozilla/5.0"}
    def scrape(self, animal_dict, no_pages):
        batch_list = []
        c_docs = 0
        for i in range(no_pages):
            with open(f"{animal_dict.get('htmfilename')}{i+1}.html", "rb") as rfile:
                soup = BeautifulSoup(rfile.read(), 'html.parser')
                url_list = soup.select("div.kib-product-card__canvas > a[href]")
                for j, url in enumerate(url_list):
                    doc_dict = dict()
                    if "https" not in url['href']:
                        continue
                    soup = BeautifulSoup(requests.get(url['href'], headers=self.user_agent).content, 'html.parser')
                    doc_dict['name'] = soup.find("h1").text
                    # Category
                    doc_dict['category'] = [item.find("a").text for item in soup.select("li.kib-breadcrumbs-item")]
                    # Prices
                    if soup.select("div[data-testid=advertised-price]"):
                        doc_dict['advertised_price'] = soup.select("div[data-testid=advertised-price]")[0].find(string=True)
                    if len(soup.select("div[data-testid=strike-through-price]")) != 0:
                        doc_dict['list_price'] = soup.select("div[data-testid=strike-through-price]")[0].find(string=True)
                    # Ingredients
                    if(len(soup.select("section#INGREDIENTS-section > p")) != 0):
                        doc_dict['ingredients'] = soup.select("section#INGREDIENTS-section > p")[0].find(string=True)
                    # Nutritional Information
                    if(len(soup.select("section#GUARANTEED_ANALYSIS-section > div.styles_markdownTable__Mtq7h")) != 0):
                        doc_dict['ingredients_analysis'] = soup.select("section#GUARANTEED_ANALYSIS-section > div.styles_markdownTable__Mtq7h")[0].text
                    # Brand
                    if(len(soup.select("a.styles_brandLink__MdoyO"))):
                        doc_dict['brand'] = soup.select("a.styles_brandLink__MdoyO")[0].find(string=True)
                    batch_list.append(doc_dict)
                    c_docs += 1
                    print(f"Updated document no.{c_docs} into bulk insert job.")
                    if c_docs % 200 == 0:
                        mongo_client = MongoClient("mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=5000&appName=mongosh+1.7.1import")
                        db = None
                        collection = None
                        db = mongo_client['ddr-final-project']
                        collection = db['chewy']
                        try:
                            print("Inserting 200 documents into database...")
                            result = collection.insert_many(batch_list)
                            print(result.inserted_ids)
                            batch_list = []
                        except BulkWriteError as e:
                            print(e.details)
        
