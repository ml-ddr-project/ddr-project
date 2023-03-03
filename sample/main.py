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
    download_catalogue_page(DOG_FOOD)
    # Logic for accessing all product links from catalogue
    scraper = ChewyScraper() 
    scraper.scrape()
    

if __name__ == "__main__":
    main()

        
