from bs4 import BeautifulSoup
import requests
import pandas as pd
import time
from url import DOG_FOOD, CAT_FOOD
from pymongo import MongoClient
from pymongo.errors import BulkWriteError
import os
from helpers import download_catalogue_page
from scraper import ChewyScraper

def main():
    no_pages = 5
    download_catalogue_page(DOG_FOOD, no_pages=no_pages)
    # Logic for accessing all product links from catalogue
    scraper = ChewyScraper() 
    scraper.scrape(no_pages=no_pages)
    

if __name__ == "__main__":
    main()

        
