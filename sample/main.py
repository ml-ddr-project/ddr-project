from bs4 import BeautifulSoup
import requests
import pandas as pd
import time
from url import map_dict
from pymongo import MongoClient
from pymongo.errors import BulkWriteError
import os
from helpers import download_catalogue_page
from scraper import ChewyScraper

def main():
    no_pages = -1
    for item in map_dict:
        no_pages = min(no_pages, map_dict[item].get("max_pages"))
    animal_dict = map_dict.get("DOG_FOOD")
    download_catalogue_page(animal_dict, no_pages=no_pages)
    # Logic for accessing all product links from catalogue
    scraper = ChewyScraper() 
    scraper.scrape(animal_dict, no_pages=no_pages)

    animal_dict = map_dict.get("CAT_FOOD")
    download_catalogue_page(animal_dict, no_pages=no_pages)
    # Logic for accessing all product links from catalogue
    scraper = ChewyScraper() 
    scraper.scrape(animal_dict, no_pages=no_pages)
    

if __name__ == "__main__":
    main()

        
