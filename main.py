import time
import csv
import re
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options

VERSION = 1.1

GECKODRIVER_PATH = "C:\\Users\\dumpl\\Documents\\Firefox_Webscrape\\geckodriver.exe"
FIREFOX_BINARY_PATH = "C:\\Program Files\\Mozilla Firefox\\firefox.exe"
EXTENSION_PATH = "C:\\Users\\dumpl\\Documents\\Projects\\MangaDL\\AdBlock\\adblock_for_firefox-6.13.0.xpi"

GOOGLE = "https://google.com"
CSV_PATH = "C:\\Users\\dumpl\\Documents\\Projects\\MangaDL\\Input\\titles.csv"


TITLE = "-BLANK-"
MAIN_WEBSITE = "https://manganato.com/"

def normalize_string(s):
    s = s.lower()
    s = re.sub(r'[^\w\s]', '', s)
    s = re.sub(r'\s+', '', s)
    return s

def target(title):
    normalized_title = normalize_string(title)
    manga_list = []

    with open(CSV_PATH, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            manga_list.append((row[0], row[1]))

    for manga_title, url in manga_list:
        if normalized_title == normalize_string(manga_title):
            print(f"Found: {manga_title} - {url}")
            global TITLE
            global MAIN_WEBSITE

            TITLE = manga_title
            MAIN_WEBSITE = url

            return url

    print("Manga not found in the CSV. Please add it manually.")
    new_link = input("Link: ")

    with open(CSV_PATH, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([title, new_link])
    
    print(f"Added new manga: {title} with link: {new_link}")
    return new_link

def main():
    #User Input
    title = input("Enter the title of the manga you want to download: ")
    link = target(title)

    print(f"Link for '{title}': {link}\n")

    #Browser Setup
    options = Options()
    options.binary_location = FIREFOX_BINARY_PATH

    print("Launching Firefox Browser\n")
    try:
        service = Service(GECKODRIVER_PATH)
        driver = webdriver.Firefox(service=service, options=options)
    except:
        print("ERROR: Failed to launch Firefox")
        return
    
    current_window = driver.current_window_handle

    print("Installing AdBlock (8s Delay)")
    try:
        driver.install_addon(EXTENSION_PATH, temporary=True)
        time.sleep(8)

        driver.switch_to.window(driver.window_handles[1])
        driver.close()
        driver.switch_to.window(current_window)
    except:
        print("ERROR: AdBlock Failed to Install")
        return
    
    print("AdBlock Successfully Installed - Closing Tab\n")

    #Actual Downloading Part
    print(f"Opening '{TITLE}' on Manganato")
    driver.get(MAIN_WEBSITE)

    time.sleep(10)

    print("Run Finished - Closing Browser")
    driver.quit()

if __name__ == '__main__':
    print(f"\n\nMangaDL Version: '{VERSION}'\n")
    main()
