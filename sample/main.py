from url import (
map_dict, URL_FEEDER, URL_FEEDER_SUBPAGE, 
 URL_CLEANER, URL_DOOR, URL_DOOR_SUBPAGE
)
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
    scraper = PetTechScraper()
    scraper.tech = 'chewy_tech_cleaner'
    scraper.saveResultPage(URL_CLEANER, "", "tech_cleaners")


    # create a new db for feeders
    # tech = db["chewy_tech_feeder"]
    scraper.tech = 'chewy_tech_feeder'
    scraper.saveResultPage(URL_FEEDER, URL_FEEDER_SUBPAGE, "tech_feeders")


    # create a new db for doors
    # tech = db["chewy_tech_door"]
    scraper.tech = 'chewy_tech_door'
    scraper.saveResultPage(URL_DOOR, URL_DOOR_SUBPAGE, "tech_doors")

if __name__ == "__main__":
    main()

        
