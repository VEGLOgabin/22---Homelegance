from scrapy import signals
from pydispatch import dispatcher
import json
import scrapy
import os
from scrapy.crawler import CrawlerProcess
import requests
from bs4 import BeautifulSoup


class MenuScraper:
    def __init__(self):
        self.url = "https://www.homelegance.com/bedroom_bedroomcollections/"
        self.data = []

    def extract_collections(self, categories_and_collections, categories_and_collections_last):
        if categories_and_collections:
            for category in categories_and_collections:
                
                category_name = category.find('a').text.strip()
                print(f"Cetegories found----{category_name}------")
                collections = category.find("ul")
                if collections:
                    print("Collections found!!!!!!!!!!!!!!!!")
                    collections = collections.find_all("li", class_ = "menu-item-li categoryImageItem")
                    for collection in collections:
                        collection_name = collection.find("a").text.strip()
                        collection_link = "https://www.homelegance.com" + collection.find("a").get("href")
                        self.data.append({
                        "category_name": category_name,
                        "collection_name": collection_name,
                        "collection_link": collection_link
                        })
                        
        if categories_and_collections_last:
            for category in categories_and_collections_last:
                
                category_name = category.find('a').text.strip()
                print(f"Cetegories found----{category_name}------")
                collections = category.find("ul")
                if collections:
                    print("Collections found!!!!!!!!!!!!!!!!")
                    collections = collections.find_all("li", class_ = "menu-item-li categoryImageItem")
                    for collection in collections:
                        collection_name = collection.find("a").text.strip()
                        collection_link = "https://www.homelegance.com" + collection.find("a").get("href")
                        self.data.append({
                        "category_name": category_name,
                        "collection_name": collection_name,
                        "collection_link": collection_link
                        })

                
                

    def scrape(self):
        response = requests.get(self.url)
        soup = BeautifulSoup(response.content, 'html.parser')
        print(soup.title.text.strip())
        
        categories_and_collections = soup.find_all('li', class_ = 'main-menu-li categoryImageItem')
        categories_and_collections_last = soup.find_all('li', class_ = 'main-menu-li categoryImageItem last-child')
        if categories_and_collections and categories_and_collections_last:
            
            self.extract_collections(categories_and_collections, categories_and_collections_last)


        with open('utilities/category-collection.json', 'w') as f:
            json.dump(self.data, f, indent=4)

        print("Data extraction complete. Saved to utilities/category-collection.json")
        
        
        
        
        
        
class CollectionSpider(scrapy.Spider):
    name = 'collection_spider'
    
    custom_settings = {
        'CONCURRENT_REQUESTS': 1,
        'FEEDS': {
            'utilities/products-links.json': {
                'format': 'json',
                'overwrite': True,
                'encoding': 'utf8',
            },
        },
        'LOG_LEVEL': 'INFO',
        'RETRY_ENABLED': True,
        'RETRY_TIMES': 3,
        'RETRY_HTTP_CODES': [500, 502, 503, 504, 522, 524, 408, 429],
        'HTTPERROR_ALLOW_ALL': True,
        'DEFAULT_REQUEST_HEADERS': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' \
                        'AppleWebKit/537.36 (KHTML, like Gecko) ' \
                        'Chrome/115.0.0.0 Safari/537.36',
            'Accept-Language': 'en',
        },
    }

    def start_requests(self):
        output_dir = 'utilities'
        os.makedirs(output_dir, exist_ok=True)

        file_path = 'utilities/products-links.json'
        with open(file_path, 'w') as file:
            pass
        
        with open('utilities/category-collection.json') as file:
            self.collections = json.load(file)
        
        if self.collections:
            yield from self.process_collection(self.collections[0], 0)

    def process_collection(self, collection, collection_index):
        category_name = collection['category_name']
        collection_name = collection['collection_name']
        collection_link = collection['collection_link']
        
        yield scrapy.Request(
            url=collection_link,
            callback=self.parse_collection,
            meta={
                'category_name': category_name,
                'collection_name': collection_name,
                'collection_link': collection_link,
                'collection_index': collection_index 
            },
            dont_filter=True
        )
        

    def parse_collection(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        products = soup.find_all('div', class_ = "col position-relative")
        product_links = ["https://www.homelegance.com" + item.find('a').get('href') for item in products if item.find('a')]

        for link in product_links:
            yield {
                'category_name': response.meta['category_name'],
                'collection_name': response.meta['collection_name'],
                'product_link': link
            }
            
        self.logger.info(f"Current category : {response.meta['category_name']} and collection : {response.meta['collection_name']}")
            
        paginations = soup.find("nav", attrs={'aria-label': 'Page navigation'})
        if paginations:
            active_page = int(paginations.find("li", class_ ="page-item active").find("a").text.strip())
            all_pages = paginations.find_all("li", class_ ="page-item")
            item = int(all_pages[-2].find("a").text.strip())
            if item > active_page:
                next_page_url = response.meta['collection_link'] + f"?pageNo={active_page + 1}"

                if next_page_url != response.url:
                    self.logger.info(f"Following next page: {next_page_url}")
                    yield scrapy.Request(
                        url=next_page_url,
                        callback=self.parse_collection,
                        meta=response.meta,
                        dont_filter=True
                    )
                else:
                    self.logger.info("No new page detected. Stopping pagination.")
            else:
                self.logger.info("Reached the last page of the collection.")
        
        current_index = response.meta['collection_index']
        next_index = current_index + 1
        if next_index < len(self.collections):
            next_collection = self.collections[next_index]
            yield from self.process_collection(next_collection, next_index)
        else:
            self.logger.info("All collections have been processed.")
            






     
class ProductSpider(scrapy.Spider):
    name = "product_spider"
    
    custom_settings = {
        'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
        'CONCURRENT_REQUESTS': 1,
        'LOG_LEVEL': 'INFO',
        'RETRY_ENABLED': True,
        'RETRY_TIMES': 3,
        'RETRY_HTTP_CODES': [500, 502, 503, 504, 522, 524, 408, 429],
        'HTTPERROR_ALLOW_ALL': True,
        'DEFAULT_REQUEST_HEADERS': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' \
                        'AppleWebKit/537.36 (KHTML, like Gecko) ' \
                        'Chrome/115.0.0.0 Safari/537.36',
            'Accept-Language': 'en',
        },
    }
    
    def start_requests(self):
        """Initial request handler."""
        self.logger.info("Spider started. Preparing to scrape products.")
        os.makedirs('output', exist_ok=True)
        self.scraped_data = []
        scraped_links = set()
        self.output_file = open('output/products-data.json', 'a', encoding='utf-8')
        if os.path.exists('output/products-data.json'):
            self.logger.info("Loading existing scraped data.")
            with open('output/products-data.json', 'r', encoding='utf-8') as f:
                    try:
                        self.scraped_data = json.load(f)
                        scraped_links = {(item['Product Link'], item["Collection"], item['Category']) for item in self.scraped_data}
                    except json.JSONDecodeError:
                        self.logger.warning("Encountered JSONDecodeError while loading existing data. Skipping line.")
                        pass 
        scraped_product_links = {item['Product Link'] for item in self.scraped_data}
        try:
            with open('utilities/products-links.json', 'r', encoding='utf-8') as file:
                products = json.load(file)
            self.logger.info(f"Loaded {len(products)} products to scrape.")
        except Exception as e:
            self.logger.error(f"Failed to load products-links.json: {e}")
            return
        for product in products:
            product_link = product['product_link']
            category_name = product['category_name']
            collection_name = product['collection_name']
            product_key = (product_link, collection_name, category_name)
            if product_key not in scraped_links:
                if product_link in scraped_product_links:
                    scraped_product = next((item for item in self.scraped_data if item['Product Link'] == product_link), None)
                    product_name = scraped_product["Product Title"]
                    if scraped_product:
                            if product_name:
                                if collection_name not in scraped_product['Collection'] or category_name not in scraped_product['Category']:
                                    new_product_data = scraped_product.copy()
                                    new_product_data['Collection'] = collection_name
                                    new_product_data['Category'] = category_name
                                    
                                    self.scraped_data.append(new_product_data)
                                    with open('output/products-data.json', 'w', encoding='utf-8') as f:
                                        json.dump(self.scraped_data, f, ensure_ascii=False, indent=4)
                                    self.logger.info(f"Updated product with new collection or category: {product_link}")

                            else:
                                yield scrapy.Request(
                                    url=product_link,
                                    callback=self.parse,
                                    meta={
                                        'product': product
                                    }
                                )

                    else:
                        self.logger.warning(f"Product link found in scraped_product_links but not in scraped_data: {product_link}")
                else:
                    
                        yield scrapy.Request(
                            url=product_link,
                            callback=self.parse,
                            meta={
                                'product': product
                            }
                        )
            else:
                
                self.logger.info(f"Skipping already scraped product: {product_link} under category: {category_name}")
    
    def parse(self, response):
        """Parse the product page using BeautifulSoup and extract details."""
        self.logger.info(f"Parsing product: {response.url}")
        try:
            product = response.meta['product']
            soup = BeautifulSoup(response.text, 'html.parser')
            category_name = product['category_name']
            collection_name = product['collection_name']
            product_link = product['product_link']
            
            product_name = soup.find("div", class_ = "model_name font-FuturaPT-Book color-text-42210B")
            
            if product_name:
                product_name = product_name.get_text().replace("\n", " ")
                
            if not product_name:
                 product_name = soup.find('div', class_ = "d-flex align-items-center collection-name mt-2")
                 if product_name:
                     product_name = product_name.get_text().replace("\n", " ")
            
            weight_dimensions_product_details = soup.find_all('div', class_ = "norm-desc ps-5 pe-5 mt-3 pb-4 description-box")
            product_details = []
            weights_dimensions = []
            if weight_dimensions_product_details:
                for item in weight_dimensions_product_details:
                    label = item.find("p").text.strip()
                    print(item.find("p").text.strip())
                    if "Weights & Dimensions" in label:
                        weight_dimensions = item.find_all("li")
                        for li in weight_dimensions:
                            text = li.get_text(strip=True)
                            if ": " in text:
                                key, value = text.split(": ", 1)
                                dim = f"{key.strip()} : {value.strip()}"
                                weights_dimensions.append(dim)
                    if "Product Details" in label:
                        product_detail = item.find_all("li")
                        for detail in product_detail:
                            if detail.text.strip() != "Prop 65 Information":
                                product_details.append(detail.text.strip())
                                
                        # product_details = ", ".join(product_details)

            imgs = soup.find_all('a', class_ ="cloud-zoom-gallery")
            product_images = []
            for item in imgs:
                
                product_images.append('https://www.homelegance.com' + item.get("href"))
                
            if product_images:
                product_images = list(set(product_images))
            
            packaging = soup.find('div', class_ = "norm-desc ps-5 pe-5 mt-4 mb-4 pb-4")
            packaging_data = []
            if packaging:
                packaging = packaging.find_all("li")
                
                for li in packaging:
                    text = li.get_text(strip=True)
                    if ": " in text:
                        key, value = text.split(": ", 1)
                        if key != "Assembly Instruction":
                            pack = f"{key.strip()} : {value.strip()}"
                            packaging_data.append(pack)
                            
                    if li.find("a"):
                        link = li.find("a").get("href")
                        packaging_data.append(f"Assembly Instruction : https://www.homelegance.com{link}")
            description = soup.find('div', class_ = "desc font-FuturaPT-Light collapse-description overflow-auto")
            if description:
                description = description.text.strip()

            sku = ""

            if product_name:
                sku = product_name.split()[0].strip()

                product_name = product_name.replace(sku, "").strip()


            new_product_data =  {
                'Category': category_name,
                'Collection': collection_name,
                'Product Link': product_link,
                'Product Title': product_name,
                "SKU": sku,
                'Packaging': packaging_data,
                'Product Details': product_details,
                'Weights & Dimensions ': weights_dimensions,
                "Product Images": product_images,
                "Description" : description
            }
            
            self.scraped_data.append(new_product_data)
            
            with open('output/products-data.json', 'w', encoding='utf-8') as f:
                json.dump(self.scraped_data, f, ensure_ascii=False, indent=4)
            self.logger.info(f"Successfully scraped product: {product_link}")
            
            
        except Exception as e:
            self.logger.error(f"Error parsing {response.url}: {e}")

    
    
    


   
#   -----------------------------------------------------------Run------------------------------------------------------------------------

def run_spiders():
    
    output_dir = 'utilities'
    os.makedirs(output_dir, exist_ok=True)
    products_links_scraper = MenuScraper()
    products_links_scraper.scrape()
    process = CrawlerProcess()
    def run_collection_spider():
        process.crawl(CollectionSpider)
    def run_product_spider():
        process.crawl(ProductSpider)

    def spider_closed(spider, reason):
        if isinstance(spider, CollectionSpider):
            run_product_spider()
    dispatcher.connect(spider_closed, signal=signals.spider_closed)
    process.crawl(CollectionSpider)
    process.start()

    # process.crawl(ProductSpider)
    # process.start()

run_spiders()
