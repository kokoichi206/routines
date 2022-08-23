import time
from typing import List

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By

from api.interface.book_fetcher import BookFetcher
from entity.book import BookItem


class DriveManager(BookFetcher):
    """Class for fetching from Google Drive.

    You need to set your chromedriver.
    1. Download a driver according to your chrome version: https://chromedriver.chromium.org/downloads
    2. Move it to self.DRIVER_PATH
    """

    def __init__(self, url: str) -> None:
        """Initialize instance variables.

        Args:
            url (str): URL from which manager will fetch pdf data.
        """

        self._url = url
        self.DRIVER_PATH = "./config/chromedriver"
        # Wait time to render HTML DOM (seconds).
        self.LOAD_WAIT_TIME = 1.5

    def fetch(self) -> List[BookItem]:
        """Fetch pdf data from Google Drive.

        Returns:
            formatted date (List[:class:`BookItem`]): Data about books.
        """

        options = webdriver.ChromeOptions()
        # Comment out this line when you want to check by sight.
        options.add_argument("--headless")
        driver = webdriver.Chrome(self.DRIVER_PATH, options=options)
        driver.get(self._url)

        BASE_URL = "https://drive.google.com/file/d/"
        SUFFIX = "/view?usp=sharing"

        time.sleep(self.LOAD_WAIT_TIME)

        # Scroll the element to display all files.
        elms = driver.find_elements(By.TAG_NAME, "c-wiz")
        for elm in elms:
            scrollHeight = driver.execute_script(
                "return arguments[0].scrollHeight;", elm)
            offsetHeight = driver.execute_script(
                "return arguments[0].offsetHeight;", elm)

            # Judge whether the 'elm' is the scrollabe area or not.
            if scrollHeight - offsetHeight > 500:
                class_names = elm.get_attribute("class")
                print(f"{class_names}")

                if class_names:
                    class_name = class_names.split(" ")[0]
                    print(f"Scroll target class name is '{class_name}'")
                    self.scroll_and_findAll(driver, class_name)

        # Get BeautifulSoup element after all elements are displayed.
        html = driver.page_source.encode("utf-8")
        soup = BeautifulSoup(html, "html.parser")

        # Collect books information.
        result = []
        divs = soup.findAll(["div"])
        for div in divs:
            if div.has_attr("data-id"):

                id = div["data-id"]
                pdf_url = BASE_URL + id + SUFFIX

                inner_divs = div.findChildren("div", recursive=True)

                for inner_div in inner_divs:
                    # Collect only pdf files.
                    if inner_div.text[:6] != "ダウンロード" and inner_div.text[-4:] == ".pdf":
                        title = inner_div.text
                        book = BookItem(title=title, url=pdf_url)
                        result.append(book)
                        break

        driver.close()
        return result

    def scroll_and_findAll(self, driver: webdriver, class_selector) -> None:
        """Scroll down until no elements show up.

        Args:
            driver (webdriver): WebDriver of selenium.
            class_selector (str): Class name to specify the target element.
        """

        time.sleep(self.LOAD_WAIT_TIME)

        element = driver.find_element(By.CLASS_NAME, class_selector)

        last_height = driver.execute_script(
            "return arguments[0].scrollTop", element)

        while True:
            print(last_height)

            # Scroll and wait.
            driver.execute_script(
                "arguments[0].scrollTop = arguments[0].scrollHeight;", element)
            time.sleep(self.LOAD_WAIT_TIME)

            new_height = driver.execute_script(
                "return arguments[0].scrollTop", element)

            # Condition to exit while loop:
            # No more elements show up when scroll down
            if new_height == last_height:
                break

            last_height = new_height

        print(new_height)
