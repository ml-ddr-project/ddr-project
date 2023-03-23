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
import csv
import requests


class ChewyScraper:
    def __init__(self, *args, **kwargs) -> None:
        for user_agent in args:
            self.user_agent = user_agent
        else:
            self.user_agent = {"User-agent": "Mozilla/5.0"}

    def scrape(self, animal_dict, no_pages):
        batch_list = []
        c_docs = 0
        for i in range(no_pages):
            with open(f"{animal_dict.get('htmfilename')}{i+1}.html", "rb") as rfile:
                soup = BeautifulSoup(rfile.read(), "html.parser")
                url_list = soup.select("div.kib-product-card__canvas > a[href]")
                for j, url in enumerate(url_list):
                    doc_dict = dict()
                    if "https" not in url["href"]:
                        continue
                    soup = BeautifulSoup(
                        requests.get(url["href"], headers=self.user_agent).content,
                        "html.parser",
                    )
                    doc_dict["name"] = soup.find("h1").text
                    # Category
                    doc_dict["category"] = [
                        item.find("a").text
                        for item in soup.select("li.kib-breadcrumbs-item")
                    ]
                    # Prices
                    if soup.select("div[data-testid=advertised-price]"):
                        doc_dict["advertised_price"] = float(soup.select(
                            "div[data-testid=advertised-price]"
                        )[0].find(string=True).replace("$", ""))
                    if len(soup.select("div[data-testid=strike-through-price]")) != 0:
                        doc_dict["list_price"] = float(soup.select(
                            "div[data-testid=strike-through-price]"
                        )[0].find(string=True).replace("$", ""))
                    # Ingredients
                    if len(soup.select("section#INGREDIENTS-section > p")) != 0:
                        doc_dict["ingredients"] = soup.select(
                            "section#INGREDIENTS-section > p"
                        )[0].find(string=True)
                    # Nutritional Information
                    if (
                        len(
                            soup.select(
                                "section#GUARANTEED_ANALYSIS-section > div.styles_markdownTable__Mtq7h"
                            )
                        )
                        != 0
                    ):
                        doc_dict["ingredients_analysis"] = soup.select(
                            "section#GUARANTEED_ANALYSIS-section > div.styles_markdownTable__Mtq7h"
                        )[0].text
                    # Brand
                    if len(soup.select("a.styles_brandLink__MdoyO")):
                        doc_dict["brand"] = soup.select("a.styles_brandLink__MdoyO")[
                            0
                        ].find(string=True)
                    batch_list.append(doc_dict)
                    c_docs += 1
                    print(f"Updated document no.{c_docs} into bulk insert job.")
                    if c_docs % 200 == 0:
                        mongo_client = MongoClient(
                            "mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=5000&appName=mongosh+1.7.1import"
                        )
                        db = None
                        collection = None
                        db = mongo_client["ddr-final-project"]
                        collection = db["chewy"]
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
        self.client = MongoClient("localhost", 27017)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
        }
        self.db = self.client["ddr-final-project"]
        self._tech = None

    @property
    def tech(self):
        return self._tech

    @tech.setter
    def tech(self, value):
        self._tech = self.db["value"]

    def saveString(htmldoc, filename="test.html"):
        try:
            file = open(filename, "w")
            file.write(str(htmldoc))
            file.close()
        except Exception as ex:
            print("Error: " + str(ex))

    def loadString(f="test.html"):
        try:
            html = open(f, "r", encoding="utf-8").read()
            return html
        except Exception as ex:
            print("Error: " + str(ex))

    def saveResultPage(self, url_1, url_2, animal_name):
        page = requests.get(url_1, headers=self.headers)
        animal = BeautifulSoup(page.content, "html.parser")

        # how many result pages
        total_page = animal.find_all("li", class_="kib-pagination-new__list-item")

        # more than one result pages
        if total_page != []:
            # find max page number
            page_num = []
            for i in total_page:
                page_num.append(i.text)
            print(animal_name, "Max page number is:", page_num[-1])
            max_page = int(page_num[-1])
            time.sleep(5)

            # save htm. file for each page
            for i in range(1, (max_page + 1)):
                # load the website
                page = requests.get(url_2.format(str(i)), headers=self.headers)
                cat = BeautifulSoup(page.content, "html.parser")

                # save pack
                relative_path = "chewy_" + animal_name + "_{}.htm"
                saveTo = os.path.join(self.absolute_path, relative_path)
                filename = saveTo.format(str(i))
                self.saveString(cat, filename)
                time.sleep(5)

                #####
                print(filename)
                self.tech_items(filename)

                i = i + 1
                time.sleep(5)

        # only one result page
        else:
            relative_path = "chewy_" + animal_name + ".htm"
            saveTo = os.path.join(self.absolute_path, relative_path)
            filename = saveTo
            self.saveString(animal, filename)
            time.sleep(5)
            print(filename)
            self.tech_items(filename)
            time.sleep(5)

    def tech_items(self, filename):
        # open saved result page
        feeders = BeautifulSoup(self.loadString(filename), "html.parser")
        # ttl = feeders.select("a.kib-product-image.product-card-image")
        sku = feeders.find_all(
            "a", class_="kib-product-image product-card-image", href=True
        )

        # get url/pic of each item
        for j in range(0, len(sku)):
            # get url link for each item in the result page
            url = sku[j]["href"]
            url_filename = re.findall(".com.*", str(url))
            url_filename = re.sub(".com", "", str(url_filename))
            url_filename = re.sub("/", "_", str(url_filename))
            url_filename = f"{url_filename}.htm"

            # get key product image
            pic = re.findall('src=".*jpg?"', str(sku[j].select("img")))
            pic = re.findall('".*"', str(pic))  # only keep key pic .jpg link
            pic = re.sub("\[|]|'|\"", "", str(pic))

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
        driver.implicitly_wait(40)  # ex: browser #im: wait more than browser
        driver.set_script_timeout(120)
        driver.set_page_load_timeout(30)

        # step 1: load item page
        driver.get(url)

        ## step 2: Loop until the "Show More Reviews" button is no longer clickable
        while True:
            try:
                show_more_button = WebDriverWait(driver, 80).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, '//span[text()="Show More Reviews"]')
                    )
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
            print("success")

        driver.quit()

    def findItemElements(self, url, pic, url_filename):
        ## open saved item page in previous step
        item = BeautifulSoup(
            self.loadString(os.path.join(self.absolute_path, url_filename)),
            "html.parser",
        )

        # product name
        name = item.find("h1", class_="styles_productName__vSdxx")
        name = name.text

        # brand and the brand's special page
        brand = item.find("a", class_="styles_brandLink__MdoyO")
        brand_name = brand.text
        brand_special_page = brand["href"]

        ## ratings summary place
        ratings = item.find("section", class_="styles_ratingsAndReview__kxjfE")
        ratings = ratings.text
        # how many reviews
        reviews_cnt = re.findall(".* Reviews", ratings)
        reviews_cnt = re.sub(" Reviews", "", str(reviews_cnt))
        if eval(reviews_cnt) != []:
            reviews_cnt = int(eval(reviews_cnt)[0])
        else:
            reviews_cnt = eval(reviews_cnt)
        # how many questions
        questions_cnt = re.findall("[0-9.*][.*0-9.*] Answered Questions", ratings)
        if len(questions_cnt) != 0:
            questions_cnt = re.sub(" Answered Questions", "", str(questions_cnt))
            questions_cnt = int(eval(questions_cnt)[0])
        # star ratings out of 5
        star = re.findall("Rated.* out of [\.0-5]", ratings)
        star = re.sub("Rated|out|of", "", str(star))
        star = float(eval(re.split(" ", str(star))[1]))

        ## price
        # selling price
        selling_price = item.find("div", attrs={"data-testid": "advertised-price"})
        selling_price = re.sub("Chewy Price", "", selling_price.text)
        #TODO(Banner): Check with Jinny
        selling_price = float(selling_price.replace("$", ""))
        # list price
        list_price = item.find("div", attrs={"data-testid": "strike-through-price"})
        if list_price is not None:
            list_price = re.sub("Chewy Price", "", list_price.text)
            #TODO(Banner): Check with Jinny
            list_price = float(list_price.replace("$", ""))

        ## specifications
        # find table and get rows
        spec = item.select(
            "div.styles_details__FzjFy.kib-grid section.styles_infoGroupSection__ArCb9 tr"
        )
        rows = []
        for row in spec:
            cells = [cell.text for cell in row.find_all(["td", "th"])]
            rows.append(cells)

        ## reviews
        reviews_text = []
        reviews = item.find_all("p", attrs={"data-testid": "review-text"})
        # get text
        for rev in reviews:
            rev = rev.text
            reviews_text.append(rev)

        print(
            "Item Name",
            name,
            "URL",
            url,
            "img",
            pic,
            "Brand",
            brand_name,
            brand_special_page,
            "Ratings",
            reviews_cnt,
            questions_cnt,
            star,
            "Price",
            selling_price,
            list_price,
            "Specification",
            rows,
            "Reviews",
            reviews_text,
        )

        ### mongoDB insert function
        self.tech.insert(
            {
                "Item Name": name,
                "URL": url,
                "Image": pic,
                "Brand": {"Brand name": brand_name, "special_page": brand_special_page},
                "Star": star,
                "Feedbacks Count": {"Ratings": reviews_cnt, "Questions": questions_cnt},
                "Price": {"Selling Price": selling_price, "List Price": list_price},
                "Specification": rows,
                "Reviews": reviews_text,
            }
        )


class PetSmartScraper:
    def __init__(self, *args, **kwargs):
        for user_agent in args:
            self.user_agent = user_agent
        else:
            self.user_agent = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
            }
        self.url_parent = "https://www.petsmart.com/"
        self.driver_path = "/Users/shaolongxue/Documents/_Misc./chromedriver"

    def get_search_result(self):
        for page_num in range(0, 2):  # change range
            # change url
            url = f"https://www.petsmart.com/cat/food-and-treats/veterinary-diets/?pmin=0.01&srule=best-sellers&start={page_num*60}&sz=60&format=ajax"
            response = requests.get(url, headers=self.user_agent)
            soup = BeautifulSoup(response.text, "html.parser")
            #################
            ###Change Here###
            #################
            with open(
                f"PetSmart_Cat_Vet_Food_{page_num+1:02}.htm", "w", encoding="utf-8"
            ) as f:
                f.write(str(soup.prettify()))

            time.sleep(15)

    ## get urls of a result page
    def get_item_url(self):
        url_list = []
        for page_num in range(0, 2):
            #################
            ###Change Here###
            #################
            file_name = f"PetSmart_Cat_Vet_Food_{page_num+1:02}.htm"

            with open(file_name, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f, "html.parser")

            # extract url
            urls = soup.find_all("a", class_="name-link")

            for item in range(len(urls)):
                link = urls[item].get("href")
                url_list.append(self.url_parent + link)

        # store urls locally for easier retrival
        #################
        ###Change Here###
        #################
        with open("PetSmart_Cat_Vet_Food_Item_URLs.csv", "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            for url in url_list:
                writer.writerow([url])

    ## get each item page
    def get_item_page(self):
        # read in the url list file
        url_list = []
        #################
        ###Change Here###
        #################
        with open("PetSmart_Dog_Vet_Food_Item_URLs.csv", "r", newline="") as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                url_list.append(row[0])

        driver = webdriver.Chrome(executable_path=self.driver_path)

        ## first 100 item pages: range(0,10)
        ## all items: range(len(url_list))
        for item_num in range(100, 101):
            time.sleep(2)
            driver.get(url_list[item_num])
            # wait for selenium to load the page properly
            time.sleep(15)

            # save the initial page
            soupA = BeautifulSoup(driver.page_source, "html.parser").prettify()
            #################
            ###Change Here###
            #################
            with open(
                f"PetSmart_Dog_Vet_Food_Item_{item_num+1:03}_A.htm",
                "w",
                encoding="utf-8",
            ) as f:
                f.write(soupA)

            # check for ingredients tab
            try:
                ingre = driver.find_element(By.ID, "react-tabs-2")
                ingre.click()
                time.sleep(2)

                soupB = BeautifulSoup(driver.page_source, "html.parser").prettify()
                #################
                ###Change Here###
                #################
                with open(
                    f"PetSmart_Dog_Vet_Food_Item_{item_num+1:03}_B.htm",
                    "w",
                    encoding="utf-8",
                ) as f:
                    f.write(soupB)
            except Exception as e:
                print("None")

    ## extract info from each page and load into MongoDB
    def get_data(self):
        client = MongoClient("localhost", 27017)
        db = client["petsmart"]
        collection = db["petfood"]

        for item_num in range(100, 121):
            filename_A = f"PetSmart_Dog_Vet_Food_Item_{item_num+1:03}_A.htm"
            filename_B = f"PetSmart_Dog_Vet_Food_Item_{item_num+1:03}_B.htm"
            ##### A Version #####
            with open(filename_A, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f, "html.parser")

            # item title
            title = soup.find("h1", class_="pdp-product-name").get_text().strip()

            # item number
            itemnum = soup.select('span[itemprop="productID"]')[0].text.strip()

            # Animal & Category
            animal = "Dog"
            category = "Vet Food"

            # description
            tab1 = soup.find("div", class_="react-tabs__tab-content")
            try:
                description = (
                    tab1.find("b", text=re.compile("DESCRIPTION"))
                    .find_next_sibling("p")
                    .text.strip()
                )
            except Exception as e:
                description = None

            # Life Stage
            try:
                life_stage = (
                    tab1.find("b", text=re.compile("Life Stage:"))
                    .find_next_sibling(text=True)
                    .strip()
                )
            except Exception as e:
                life_stage = None

            # Sellng Price & Listing Price
            try:
                sell_price = float(
                    soup.find("span", class_="product-price-sales")["data-gtm-price"]
                )
                list_price = soup.find(
                    "span", class_="product-price-standard"
                ).text.strip()
                list_price = float(re.findall(r"\d+\.\d+", list_price)[0])
            except Exception as e:
                sell_price = float(
                    soup.find("span", class_="product-price-standard")["data-gtm-price"]
                )
                list_price = sell_price

            # Weight
            try:
                weight_str = (
                    tab1.find("b", text=re.compile("Weight"))
                    .find_next_sibling(text=True)
                    .strip()
                )
                pattern = r"\d+(\.\d+)?\s*(lb|oz)"
                match = re.search(pattern, weight_str)
                weight = match.group()
            except Exception as e:
                weight = None

            # Brand
            try:
                brand = (
                    tab1.find("b", text=re.compile("Brand:"))
                    .find_next_sibling(text=True)
                    .strip()
                )

            except Exception as e:
                brand = None

            # Health Consideration
            try:
                health_consid = (
                    tab1.find("b", text=re.compile("Health Consideration:"))
                    .find_next_sibling(text=True)
                    .strip()
                )
            except Exception as e:
                health_consid = None

            ##### B Version #####
            try:
                with open(filename_B, "r", encoding="utf-8") as f:
                    soupB = BeautifulSoup(f, "html.parser")

                tab2 = soupB.find("div", class_="react-tabs__tab-content")

                # Ingredients
                try:
                    ingredient = (
                        tab2.find("b", text=re.compile("Ingredients:"))
                        .find_next_sibling()
                        .find_next_sibling(text=True)
                        .strip()
                    )
                except Exception as e:
                    ingredient = None

                # Nutritional Info (Guaranteed Analysis)
                try:
                    nutri_str = (
                        tab2.find("b", text=re.compile("Guaranteed Analysis:"))
                        .find_parent()
                        .get_text()
                        .strip()
                    )
                    nutri_str = re.sub(r"^Guaranteed Analysis:\n\s+", "", nutri_str)
                    nutrition = re.sub(r"\n\s*\n", "\n", nutri_str)
                except Exception as e:
                    nutrition = None
            except Exception as e:
                ingredient = None
                nutrition = None

            document = {
                "Title": title,
                "Item_Num": itemnum,
                "Animal": animal,
                "Category": category,
                "Description": description,
                "Life_Stage": life_stage,
                "Selling_Price": sell_price,
                "Listing_Price": list_price,
                "Weight": weight,
                "Brand": brand,
                "Health_Consideration": health_consid,
                "Ingredients": ingredient,
                "Nutritional_Info": nutrition,
            }

            collection.insert_one(document)

            print("------")
            print("Item: ", item_num + 1)
