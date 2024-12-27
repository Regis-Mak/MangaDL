import time
import csv
import re
import os
import shutil

from tqdm import tqdm

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options

VERSION = 1.1

DEBUG_MODE = False
HEADLESS = False

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
    global TITLE
    global MAIN_WEBSITE
    TITLE = title

    normalized_title = normalize_string(title)
    manga_list = []

    with open(CSV_PATH, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            manga_list.append((row[0], row[1]))

    for manga_title, url in manga_list:
        if normalized_title == normalize_string(manga_title):
            print(f"Found: {manga_title} - {url}")
            TITLE = manga_title
            MAIN_WEBSITE = url
            return url

    print("Manga not found in the CSV. Please add it manually.\n")
    new_link = input("Link: ")

    print(f"Adding new row: {title}, {new_link}")

    with open(CSV_PATH, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        file.seek(0, 2)
        writer.writerow([title, new_link])

    print(f"Added new manga: {title} with link: {new_link}")
    
    return new_link

def close_browser(driver, message):
    print(message)
    driver.quit()

def download(driver):
    print("Beginning Download")
    elements = driver.find_elements(By.XPATH, "/html/body/div[2]/div[3]/div[1]/div[3]/ul/*[contains(@class, 'a-h')]")
    elements = list(reversed(elements))
    original_window = driver.current_window_handle

    for chapter in elements:
        chapter_link = chapter.find_element(By.XPATH, ".//a[@class='chapter-name text-nowrap']").get_attribute("href")
        chapter_title = chapter.find_element(By.XPATH, ".//a[@class='chapter-name text-nowrap']").text

        if ":" in chapter_title:
            chapter_title = chapter_title.split(":")[0].strip()

        os.mkdir(chapter_title)
        #print(f"Downloading '{chapter_title}'")
        
        driver.execute_script(f"window.open('{chapter_link}', '_blank');")
        driver.switch_to.window(driver.window_handles[-1])

        os.chdir(chapter_title)
        print()
        download_chapter(driver, chapter_title)
        os.chdir('..')

        driver.close()
        driver.switch_to.window(original_window)

def download_chapter(driver, chapter_title):
    #Required if not it's too fast to download
    time.sleep(2)

    images = driver.find_elements(By.TAG_NAME, "img")
    image_count = len(images)

    if image_count <= 1:
        print("No images found on this page or only one image present.")
        return

    for idx, image in enumerate(tqdm(images[:-1], desc=f"Downloading {chapter_title}", unit="image", colour="blue")):
        try:
            image_screenshot_path = f"{idx + 1}.png"
            image.screenshot(image_screenshot_path)
            #print(f"Page {idx + 1} saved")
        except Exception as e:
            print(f"Error capturing image {idx + 1}: {e}")

def main():
    #User Input
    title = input("Enter the title of the manga you want to download: ")
    link = target(title)

    print(f"\nTARGETED -> '{TITLE}' @ {link}\n")

    #Browser Setup
    options = Options()
    if HEADLESS:
        options.add_argument("--headless")

    options.binary_location = FIREFOX_BINARY_PATH

    print("Launching Firefox Browser\n")
    try:
        service = Service(GECKODRIVER_PATH)
        driver = webdriver.Firefox(service=service, options=options)
    except:
        print("ERROR: Failed to launch Firefox")
        return
    
    current_window = driver.current_window_handle

    print("Installing AdBlock (5s Delay)")
    try:
        driver.install_addon(EXTENSION_PATH, temporary=True)
        time.sleep(5)

        driver.switch_to.window(driver.window_handles[1])
        driver.close()
        driver.switch_to.window(current_window)
    except:
        print("ERROR: AdBlock Failed to Install")
        return
    
    print("AdBlock Successfully Installed - Closing Tab\n")

    print(f"Opening '{TITLE}' on Manganato")
    driver.get(MAIN_WEBSITE)

    #Output Preperation
    try:
        print("Output Folder Found\n")
        os.chdir("Output")
    except FileNotFoundError:
        print("Output Folder NOT Found - Creating")
        os.mkdir("Output")
        os.chdir("Output")

    try:
        os.mkdir(TITLE)
        print(f"Directory For '{TITLE}' created successfully.\n")
    except FileExistsError:
        print(f"Directory '{TITLE}' already exists.\nWARNING: Continuing will delete existing 'Directory : {TITLE}'\n")

        while True:
            if DEBUG_MODE:
                shutil.rmtree(TITLE)
                os.mkdir(TITLE)
                print(f"DEBUG_MODE: Auto Overide. '{TITLE}' created successfully.\n")
                break

            override = input("Would you like to proceed? (y/n) : ")
            override = override.lower()

            if override == 'y':
                shutil.rmtree(TITLE)
                os.mkdir(TITLE)
                print(f"Directory For '{TITLE}' created successfully.\n")
                break
            elif override == 'n':
                close_browser(driver, "Run ABORTED - Closing Browser")
                return
            print(". Invalid Input .")
    except Exception as e:
        print(f"An error occurred: {e}")
    
    #Attempt Download
    try:
        start_time = time.time()
        os.chdir(TITLE)
        download(driver)
    except Exception as e:
        close_browser(driver, e)

    end_time = time.time()
    elapsed_time = end_time - start_time

    print(f"Time Elapsed: {elapsed_time:.2f}s")
    close_browser(driver, "Run Finished - Closing Browser")

if __name__ == '__main__':
    print(f"\nMangaDL Version: '{VERSION}'\n")
    main()
