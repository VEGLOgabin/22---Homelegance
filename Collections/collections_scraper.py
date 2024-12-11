# import os
# import json
# from playwright.sync_api import sync_playwright
# from bs4 import BeautifulSoup

# def process_collection(page, collection, collection_index, collections, output_file):
#     category_name = collection['category_name']
#     collection_name = collection['collection_name']
#     collection_link = collection['collection_link']

#     current_index = collection_index

#     print(f"Processing category: {category_name}, collection: {collection_name}")

#     page.goto(collection_link)
#     while True:
#         content = page.content()
#         soup = BeautifulSoup(content, 'html.parser')
#         products = soup.find_all('div', class_="col position-relative")
        
#         product_links = [
#             "https://www.homelegance.com" + item.find('a').get('href')
#             for item in products if item.find('a')
#         ]
#         print("Products found: ", len(product_links))
#         with open(output_file, 'a', encoding='utf-8') as f:
#             for link in product_links:
#                 data = {
#                     'category_name': category_name,
#                     'collection_name': collection_name,
#                     'product_link': link
#                 }
#                 f.write(json.dumps(data) + "\n")

#         paginations = soup.find("nav", attrs={'aria-label': 'Page navigation'})
#         if paginations:
#             active_page = int(paginations.find("li", class_="page-item active").find("a").text.strip())
#             all_pages = paginations.find_all("li", class_="page-item")
#             last_page = int(all_pages[-2].find("a").text.strip())

#             if active_page < last_page:
#                 next_page_url = f"{collection_link}?pageNo={active_page + 1}"
#                 print(f"Following next page: {next_page_url}")
#                 page.goto(next_page_url)
#             else:
#                 print("Reached the last page of the collection.")
#                 break
#         else:
#             print("No pagination found.")
#             break


#     next_index = current_index + 1
#     if next_index < len(collections):
#         process_collection(page, collections[next_index], next_index, collections, output_file)
#     else:
#         print("All collections have been processed.")

# if __name__ == "__main__":
#     output_dir = 'utilities'
#     os.makedirs(output_dir, exist_ok=True)

#     category_file = os.path.join(output_dir, 'category-collection.json')
#     output_file = os.path.join(output_dir, 'products-links.json')

#     with open(output_file, 'w', encoding='utf-8') as file:
#         pass

#     with open(category_file, 'r', encoding='utf-8') as file:
#         collections = json.load(file)

#     if collections:
#         with sync_playwright() as p:
#             browser = p.chromium.launch(headless=True)
#             page = browser.new_page()

#             process_collection(page, collections[0], 0, collections, output_file)

#             browser.close()

#     print("Scraping completed.")




import os
import json
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

# def process_collection_products(page, collection, collection_index, collections, output_file):
#     category_name = collection['category_name']
#     collection_name = collection['collection_name']
#     collection_link = collection['collection_link']

#     current_index = collection_index

#     print(f"Processing category: {category_name}, collection: {collection_name}")

#     page.goto(collection_link)
#     while True:
#         content = page.content()
#         soup = BeautifulSoup(content, 'html.parser')
#         products = soup.find_all('div', class_="col position-relative")
        
#         product_links = [
#             "https://www.homelegance.com" + item.find('a').get('href')
#             for item in products if item.find('a')
#         ]
#         print("Products found: ", len(product_links))
#         with open(output_file, 'a', encoding='utf-8') as f:
#             for link in product_links:
#                 data = {
#                     'category_name': category_name,
#                     'collection_name': collection_name,
#                     'product_link': link
#                 }
#                 f.write(json.dumps(data) + "\n")

#         paginations = soup.find("nav", attrs={'aria-label': 'Page navigation'})
#         if paginations:
#             active_page = int(paginations.find("li", class_="page-item active").find("a").text.strip())
#             all_pages = paginations.find_all("li", class_="page-item")
#             last_page = int(all_pages[-2].find("a").text.strip())

#             if active_page < last_page:
#                 next_page_url = f"{collection_link}?pageNo={active_page + 1}"
#                 print(f"Following next page: {next_page_url}")
#                 page.goto(next_page_url)
#             else:
#                 print("Reached the last page of the collection.")
#                 break
#         else:
#             print("No pagination found.")
#             break

#     next_index = current_index + 1
#     if next_index < len(collections):
#         process_collection_products(page, collections[next_index], next_index, collections, output_file)
#     else:
#         print("All collections have been processed.")


def process_collection_products(page, collection, collection_index, collections, output_file, all_products):
    category_name = collection['category_name']
    collection_name = collection['collection_name']
    collection_link = collection['collection_link']

    current_index = collection_index

    print(f"Processing category: {category_name}, collection: {collection_name}")

    page.goto(collection_link)
    while True:
        content = page.content()
        soup = BeautifulSoup(content, 'html.parser')
        products = soup.find_all('div', class_="col position-relative")
        
        product_links = [
            "https://www.homelegance.com" + item.find('a').get('href')
            for item in products if item.find('a')
        ]
        print("Products found: ", len(product_links))
        
        for link in product_links:
            data = {
                'category_name': category_name,
                'collection_name': collection_name,
                'product_link': link
            }
            all_products.append(data)

        paginations = soup.find("nav", attrs={'aria-label': 'Page navigation'})
        if paginations:
            active_page = int(paginations.find("li", class_="page-item active").find("a").text.strip())
            all_pages = paginations.find_all("li", class_="page-item")
            last_page = int(all_pages[-2].find("a").text.strip())

            if active_page < last_page:
                next_page_url = f"{collection_link}?pageNo={active_page + 1}"
                print(f"Following next page: {next_page_url}")
                page.goto(next_page_url)
            else:
                print("Reached the last page of the collection.")
                break
        else:
            print("No pagination found.")
            break

    next_index = current_index + 1
    if next_index < len(collections):
        process_collection_products(page, collections[next_index], next_index, collections, output_file, all_products)
    else:
        print("All collections have been processed.")
        # Write all data to the output file at the end
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_products, f, indent=4)



# def get_collections_products():
#     output_dir = 'utilities'
#     os.makedirs(output_dir, exist_ok=True)

#     category_file = os.path.join(output_dir, 'category-collection.json')
#     output_file = os.path.join(output_dir, 'products-links.json')

#     with open(output_file, 'w', encoding='utf-8') as file:
#         pass

#     with open(category_file, 'r', encoding='utf-8') as file:
#         collections = json.load(file)

#     if collections:
#         with sync_playwright() as p:
#             browser = p.chromium.launch(headless=True)
#             page = browser.new_page()

#             process_collection_products(page, collections[0], 0, collections, output_file)

#             browser.close()

#     print("Scraping completed.")



def get_collections_products():
    output_dir = 'utilities'
    os.makedirs(output_dir, exist_ok=True)

    category_file = os.path.join(output_dir, 'category-collection.json')
    output_file = os.path.join(output_dir, 'products-links.json')

    all_products = []  # Initialize the list to hold all product data

    with open(category_file, 'r', encoding='utf-8') as file:
        collections = json.load(file)

    if collections:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            process_collection_products(page, collections[0], 0, collections, output_file, all_products)

            browser.close()

    print("Scraping completed.")


if __name__ == "__main__":
    get_collections_products()
