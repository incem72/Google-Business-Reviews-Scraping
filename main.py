import os
import sys
import time
import datetime
import logging
from bs4 import BeautifulSoup
import pandas as pd
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
import selenium.common.exceptions
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import re



# SET CHROME OPTIONS:
options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('--disable-gpu')  # applicable to windows os only
options.add_argument('start-maximized') #
options.add_argument('disable-infobars')
options.add_argument("--disable-extensions")

# SET OUTPUT FILES:
log_file_root = "output" + '/' + "log.txt"
csv_file_root = "output" + '/' + "data.csv"

os.makedirs(os.path.dirname(log_file_root), exist_ok=True)
os.makedirs(os.path.dirname(csv_file_root), exist_ok=True)


# SET LOGGING:
logging.basicConfig(filename=log_file_root,
                    format='%(asctime)s-%(levelname)s-FILE:%(filename)s-FUNC:%(funcName)s-LINE:%(lineno)d-%(message)s',
                    level=logging.INFO)


def selenium_get_url(url, _options, sleep_time):

    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get(url)
        time.sleep(sleep_time)
    except selenium.common.exceptions.WebDriverException as e:
        logging.error(f'WEB DRIVER ERROR ON URL: {url}. Exception Details: {e}')
        return ""
    except Exception as e:
        logging.error(f'GENERAL ERROR ON URL: {url}. Exception Details: {e}')
        return ""
    return driver

def selenium_find_element(driver, key, element):

    try:
         found_object = driver.find_element(key, element)
         return found_object

    except selenium.common.exceptions.NoSuchElementException:
        logging.info(f'NoSuchElementException received - {datetime.datetime.now()}')
    except selenium.common.exceptions.ElementNotInteractableException:
        logging.info(f'ElementNotInteractableException received.. - {datetime.datetime.now()}')
    except Exception as e:
        logging.error(f'Some other Exception is Received  !!!:  {e}')

    return ""

def get_review_dialog_list_length(page_source):
    soup = BeautifulSoup(page_source.encode('utf-8'),"html.parser")
    rewiev_container = soup.find_all("div", {"class", "WMbnJf vY6njf gws-localreviews__google-review"})
    return len(rewiev_container)

def checkIfBottomOfViewReached(driver, element):
    return driver.execute_script("if (arguments[0].scrollHeight == arguments[0].offsetHeight + arguments[0].scrollTop) { return true; } else { return false; }", element)

#
# Retrieve all Reviews from Pop-up url
#
def selenium_get_reviews(url):

    options.add_argument("--headless") # Runs Chrome in headless mode.
    driver = selenium_get_url(url, options, 10)
    logging.info(f'Chrome loaded - {datetime.datetime.now()}')

    try:
        # review_dialog_list  = driver.find_element("xpath", '//div[@class="review-dialog-list"]')
        review_dialog_list  = driver.find_element("xpath", '//*[@id="gsr"]/span[2]/g-lightbox/div/div[2]/div[3]/span/div/div/div/div[2]')
        scroll = 0
        while True:
            scroll += 1
            is_reached = checkIfBottomOfViewReached(driver, review_dialog_list)
            dialog_list_length = get_review_dialog_list_length(driver.page_source)
            print(f'Scrollling: {scroll} / Retrieved Rewievs: {dialog_list_length}')
            logging.info(f'Scrollling: {scroll} - Scraped Rewievs: {dialog_list_length}')
            if is_reached:
                logging.info(f'Total of {dialog_list_length} records retrieved. Now, output file will be prepared..')
                break

            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", review_dialog_list)
            #driver.execute_script('arguments[0].scrollTop = arguments[0].scrollTop + arguments[0].offsetHeight;', review_dialog_list)
            time.sleep(5)

        time.sleep(5)
        text = driver.page_source
        soup = BeautifulSoup(text.encode('utf-8'),"html.parser")
        container = soup.find_all("div", {"class", "WMbnJf vY6njf gws-localreviews__google-review"})

        print("Completed... Total reviews retrieved:", len(container))

        result_list = []

        for content in container:
            dict = {}
            rating_score = ""
            rewiew_text = ""
            rewiver_link = ""
            rewiver_name = ""
            href_div = content.find("div", {"class", "TSUbDb"})
            if href_div:
                rewiver_link = href_div.find('a', href=True)["href"]
                rewiver_name = href_div.text
                rewiew_text = content.find("span", {"class", "review-full-text"})
                if rewiew_text:
                    rewiew_text = rewiew_text.text.replace("\n", "").replace("\r", " ").strip()
                else:
                    temp_1 = content.find("div", {"class", "Jtu6Td"})
                    if temp_1:
                        rewiew_text = temp_1.find("span")
                        if rewiew_text:
                            rewiew_text = rewiew_text.text.replace("\n", "").replace("\r", " ").strip()


                rating = content.find("span", {"class", "Fam1ne EBe2gf"})
                if rating:
                    rating_aria = rating.get('aria-label')
                    if rating_aria:
                        rating_array = re.findall(r'\b\d+\b',rating_aria )
                        rating_score = rating_array[1]

                # dict = {"Name": rewiver_name,  "Rating":rating_score, "Text":rewiew_text, "Url": rewiver_link }
                dict = {"Name": rewiver_name,  "Rating":rating_score, "Text":rewiew_text}
                result_list.append(dict)

        return result_list

    except selenium.common.exceptions.NoSuchElementException:
        logging.info(f'NoSuchElementException received - {datetime.datetime.now()}')
    except selenium.common.exceptions.ElementNotInteractableException:
        logging.info(f'ElementNotInteractableException received.. - {datetime.datetime.now()}')
    except Exception as e:
        logging.error(f'Some other Exception is Received  !!!:  {e}')

    driver.close


#
# Finds Review Pop-up url for given search keyword.
#
def find_url_from_searchwords(searchword):
    business_exist = False
    company_name = ""
    total_rewiev = ""
    rewiew_popup_url = ""

    options.add_argument("--headless")
    keywords = searchword.split()
    searchword = ""
    for key in keywords:
        searchword =searchword + "+" + key

    url = f'https://www.google.com/search?q=google{searchword}'

    logging.info(f'We are testing... : {url} for your "{searchword}" searchwords')
    print("\nSearching... :",url)
    driver = selenium_get_url(url, options, 10)
    if not driver:
        return ""

    soup = BeautifulSoup(driver.page_source.encode('utf-8'),"html.parser")
    if soup.find("div", {"class", "liYKde g VjDLd"}):
        business_exist = True

    if business_exist:
        soup = BeautifulSoup(driver.page_source.encode('utf-8'),"html.parser")
        company_name_temp = soup.find("div", {"class", "SPZz6b"})
        if company_name_temp:
            company_name = company_name_temp.find("span").text.strip()

        rewiew_temp = soup.find("span", {"class", "hqzQac"})
        if rewiew_temp:
            rewiew_temp_a = rewiew_temp.find("a")
            if rewiew_temp_a:
                total_rewiev = rewiew_temp_a.find("span").text.strip()
                # - GET pop-up dataifid ID: (to open REWIEV popup)e.g.,=> www.google.com/search?q=....#lrd=0x14ba16acdff4b257:0xac813bd5a3d06e47,1,,,
                url_temp = rewiew_temp_a.attrs["data-fid"]
                rewiew_popup_url = f'{url}#lrd={url_temp},1'
                logging.info(f' FOUND The link FOR REVIEWS POPUP : {rewiew_popup_url}')

        if company_name and total_rewiev:
            print(f'\nWe found -{company_name}- for your search. It has {total_rewiev} reviews.')

        else:
            print("company_name and or total_rewiev not available")
            driver.close()
            return ""
    else:
        print("Sorry, we couldnt find any businesss site for your search words. Please try with more precise searchwords.")
        driver.close()
        return ""

    driver.close()
    return rewiew_popup_url


def main():

    searchwords = input("Please type business name, city, town, etc. to search (e.g., 'petmania madrid'):")
    popup_url = find_url_from_searchwords(searchwords)

    if popup_url:
        user_input = input(f'\nDo you want us to retrieve all reviews (yes/no): ')
        yes_choices = ['yes', 'y']
        no_choices = ['no', 'n']
        if user_input.lower() in yes_choices:
            pass
        elif user_input.lower() in no_choices:
            quit()
        else:
            print('Next time Type "yes" or "no" ONLY !')
            quit()
    else:
        logging.info(f'No business found for your search words: {searchwords}. Please try with more precise words like: business name, city')
        quit()

    # Get RAll evies
    scraped_data = selenium_get_reviews(popup_url)

    # Output data
    if scraped_data:
        df = pd.DataFrame(scraped_data)
        df.to_csv(csv_file_root, index=False)


if __name__ == '__main__':
    main()
