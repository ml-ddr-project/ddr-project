
map_dict = {
        "DOG_FOOD":{"url": "https://www.chewy.com/b/food_c332_p", "max_pages": 124, "htmfilename": "dog_food_"},
        "CAT_FOOD":{"url": "https://www.chewy.com/b/food_c387_p", "max_pages": 98, "htmfilename": "cat_food_"},
}
URL_FEEDER = "https://www.chewy.com/s?query=automatic+feeders&rh=price_d%3A5"
URL_FEEDER_SUBPAGE = "https://www.chewy.com/s?query=automatic+feeders&page={}&rh=price_d%3A5"
URL_CLEANER = "https://www.chewy.com/s?query=automatic%20self-cleaning"
URL_DOOR = "HTTPS://WWW.CHEWY.COM/S?QUERY=AUTOMATIC+DOORS&RH=PRICE_D%3a5" # FILTER OUT PRICE < $50
URL_DOOR_SUBPAGE = "https://www.chewy.com/s?query=automatic+doors&page={}&rh=price_d%3A5"