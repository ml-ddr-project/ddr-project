# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import requests
from pymongo import MongoClient
from pymongo.errors import BulkWriteError
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import re
import time
import requests

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
        
class PetTechScraper:
    def __init__(self, *args, **kwargs) -> None:
        self.absolute_path = os.path.dirname("/Users/zhongjinying/Downloads/")
        self.client = MongoClient('localhost', 27017)
        self.headers = headers =  {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'}
        self.db = self.client["ddr-final-project"]
        self.tech = self.db["chewy_tech_cleaner"]
        self.url_feeder = "https://www.chewy.com/s?query=automatic+feeders&rh=price_d%3A5" # filter out price < $50 - other animal or not automatic feeders
        self.url_feeder_subpage = "https://www.chewy.com/s?query=automatic+feeders&page={}&rh=price_d%3A5"
        self.url_cleaner = "https://www.chewy.com/s?query=automatic%20self-cleaning"
        self.url_door = "https://www.chewy.com/s?query=automatic+doors&rh=price_d%3A5" # filter out price < $50
        self.url_door_subpage = "https://www.chewy.com/s?query=automatic+doors&page={}&rh=price_d%3A5"

    def saveString(htmldoc, filename="test.html"):
        try:
            file = open(filename,"w")
            file.write(str(htmldoc))
            file.close()
        except Exception as ex:
            print('Error: ' + str(ex))


    def loadString(f="test.html"):
        try:
            html = open(f, "r", encoding='utf-8').read()
            return(html)
        except Exception as ex:
            print('Error: ' + str(ex))

    def saveResultPage(self, url_1, url_2, animal_name):
        page = requests.get(url_1, headers = self.headers)
        animal = BeautifulSoup(page.content, 'html.parser')
        
        # how many result pages 
        total_page = animal.find_all("li", class_ = "kib-pagination-new__list-item")
        
        # more than one result pages
        if total_page != []:
            # find max page number
            page_num=[]
            for i in total_page:
                page_num.append(i.text)
            print(animal_name, "Max page number is:", page_num[-1])
            max_page = int(page_num[-1])
            time.sleep(5)
            
            # save htm. file for each page
            for i in range(1, (max_page+1)):
                # load the website
                page = requests.get(url_2.format(str(i)), headers = self.headers)
                cat = BeautifulSoup(page.content, 'html.parser')

                # save pack
                relative_path = "chewy_"+ animal_name +"_{}.htm"
                saveTo = os.path.join(self.absolute_path, relative_path)
                filename = saveTo.format(str(i))
                self.saveString(cat, filename)
                time.sleep(5)
                
                ##### 
                print(filename)
                self.tech_items(filename)

                i = i+1
                time.sleep(5)
        
        # only one result page
        else: 
            relative_path = "chewy_"+ animal_name +".htm"
            saveTo = os.path.join(self.absolute_path, relative_path)
            filename = saveTo
            self.saveString(animal, filename)
            time.sleep(5)
            print(filename)
            self.tech_items(filename)
            time.sleep(5)

    def tech_items(self, filename):
        # open saved result page
        feeders = BeautifulSoup(self.loadString(filename),"html.parser")
        #ttl = feeders.select("a.kib-product-image.product-card-image")
        sku = feeders.find_all("a", class_ = 'kib-product-image product-card-image', href=True)
        
        # get url/pic of each item
        for j in range(0, len(sku)):
            # get url link for each item in the result page
            url = sku[j]['href']
            url_filename = re.findall(".com.*",str(url))
            url_filename = re.sub(".com", "", str(url_filename))
            url_filename = re.sub("/","_",str(url_filename))
            url_filename = f"{url_filename}.htm"

            # get key product image
            pic = re.findall("src=\".*jpg?\"",str(sku[j].select('img'))) 
            pic = re.findall("\".*\"", str(pic)) # only keep key pic .jpg link
            pic = re.sub("\[|]|\'|\"","", str(pic))
            
            ## use selenium to save each skus
            self.seleniumGetItemPage(url, url_filename)
            
            print(j)
            self.findItemElements(url, pic, url_filename)
            print("\n")
            
            j = j + 1
            time.sleep(5)

    def seleniumGetItemPage(self, url, url_filename):
        ########## get reviews - use selenium

        # activate webdriver
        relative_path = "chromedriver_mac64_new/chromedriver"
        driver_path = os.path.join(self.absolute_path, relative_path)

        driver = webdriver.Chrome(executable_path=driver_path)
        driver.implicitly_wait(40) #ex: browser #im: wait more than browser
        driver.set_script_timeout(120)
        driver.set_page_load_timeout(30)

        # step 1: load item page
        driver.get(url)

        ## step 2: Loop until the "Show More Reviews" button is no longer clickable
        while True:
            try:
                show_more_button = WebDriverWait(driver, 80).until(
                    EC.element_to_be_clickable((By.XPATH, '//span[text()="Show More Reviews"]'))
                )
                time.sleep(20) 
                show_more_button.click()
                time.sleep(20) 
                driver.set_page_load_timeout(40)
            except (TimeoutException, NoSuchElementException):
                # If the button is not found or is no longer clickable, break out of the loop
                break

        # save pack
        relative_path = url_filename
        saveTo = os.path.join(self.absolute_path, relative_path)
        with open(saveTo, "w", encoding="utf-8") as file:
            file.write(driver.page_source)
            print('success')
        
        driver.quit()

    def findItemElements(self, url, pic, url_filename):
        ## open saved item page in previous step
        item = BeautifulSoup(self.loadString(os.path.join(self.absolute_path, url_filename)),"html.parser")
        
        # product name
        name = item.find("h1", class_ = 'styles_productName__vSdxx')
        name = name.text

        # brand and the brand's special page
        brand = item.find("a", class_ = 'styles_brandLink__MdoyO')
        brand_name = brand.text
        brand_special_page = brand['href']
        
        ## ratings summary place
        ratings = item.find("section", class_ = "styles_ratingsAndReview__kxjfE")
        ratings = ratings.text
        # how many reviews
        reviews_cnt = re.findall(".* Reviews", ratings)
        reviews_cnt = re.sub(" Reviews","",str(reviews_cnt))
        if eval(reviews_cnt) != []:
            reviews_cnt = int(eval(reviews_cnt)[0])
        else:
            reviews_cnt = eval(reviews_cnt)
        # how many questions
        questions_cnt = re.findall("[0-9.*][.*0-9.*] Answered Questions", ratings)
        if len(questions_cnt) != 0:
            questions_cnt = re.sub(" Answered Questions","", str(questions_cnt))
            questions_cnt = int(eval(questions_cnt)[0])
        # star ratings out of 5
        star = re.findall("Rated.* out of [\.0-5]", ratings)
        star = re.sub("Rated|out|of", "", str(star))
        star = float(eval(re.split(" ", str(star))[1]))
        
        ## price
        # selling price
        selling_price = item.find("div", attrs={"data-testid": "advertised-price"})
        selling_price = re.sub("Chewy Price", "", selling_price.text)
        # list price
        list_price = item.find("div", attrs={"data-testid": "strike-through-price"})
        if list_price is not None:
            list_price = re.sub("Chewy Price", "", list_price.text)
            
        ## specifications
        # find table and get rows
        spec = item.select("div.styles_details__FzjFy.kib-grid section.styles_infoGroupSection__ArCb9 tr")
        rows = []
        for row in spec:
            cells = [cell.text for cell in row.find_all(['td', 'th'])]
            rows.append(cells)
            
        ## reviews
        reviews_text = []
        reviews = item.find_all("p", attrs={"data-testid": "review-text"})
        # get text
        for rev in reviews:
            rev = rev.text
            reviews_text.append(rev)
        
        print("Item Name", name, "URL", url, "img", pic, "Brand", brand_name, brand_special_page, 
            "Ratings", reviews_cnt, questions_cnt, star, "Price", selling_price, list_price, 
            "Specification", rows, "Reviews", reviews_text)
        
        ### mongoDB insert function
        tech.insert({
            "Item Name": name,
            "URL": url,
            "Image": pic,
            "Brand":  {"Brand name": brand_name, "special_page": brand_special_page},
            "Star": star,
            "Feedbacks Count": {"Ratings": reviews_cnt, "Questions": questions_cnt},
            "Price": {"Selling Price": selling_price, "List Price": list_price},
            "Specification": rows,
            "Reviews": reviews_text
        })

scraper = PetTechScraper()
scraper.saveResultPage(url_cleaner, "", "tech_cleaners")


# create a new db for feeders
tech = db["chewy_tech_feeder"]
scraper.saveResultPage(url_feeder, url_feeder_subpage, "tech_feeders")


# create a new db for doors
tech = db["chewy_tech_door"]
scraper.saveResultPage(url_door, url_door_subpage, "tech_doors")
