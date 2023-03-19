from bs4 import BeautifulSoup
import requests
import pandas as pd
import time
from url import map_dict
from pymongo import MongoClient
from pymongo.errors import BulkWriteError
import os
from helpers import download_catalogue_page
from scraper import ChewyScraper, PetTechScraper

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
    #TODO(Sayar): Add dictionary data structure for ingredients
    # Classification of companies and products. Tier vs Ingredients
    # Does top tier company have more nutritional products as compared to bottom tier.
    # Define tier based on price. Do some ingredient analysis based on tier
    url_feeder = "https://www.chewy.com/s?query=automatic+feeders&rh=price_d%3A5" # filter out price < $50 - other animal or not automatic feeders
    url_feeder_subpage = "https://www.chewy.com/s?query=automatic+feeders&page={}&rh=price_d%3A5"
    url_cleaner = "https://www.chewy.com/s?query=automatic%20self-cleaning"
    url_door = "https://www.chewy.com/s?query=automatic+doors&rh=price_d%3A5" # filter out price < $50
    url_door_subpage = "https://www.chewy.com/s?query=automatic+doors&page={}&rh=price_d%3A5"
    scraper = PetTechScraper()
    scraper.tech = 'chewy_tech_cleaner'
    scraper.saveResultPage(url_cleaner, "", "tech_cleaners")


    # create a new db for feeders
    # tech = db["chewy_tech_feeder"]
    scraper.tech = 'chewy_tech_feeder'
    scraper.saveResultPage(url_feeder, url_feeder_subpage, "tech_feeders")


    # create a new db for doors
    # tech = db["chewy_tech_door"]
    scraper.tech = 'chewy_tech_door'
    scraper.saveResultPage(url_door, url_door_subpage, "tech_doors")

if __name__ == "__main__":
    main()

        
