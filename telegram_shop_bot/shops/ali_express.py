from telegram_shop_bot.exceptions import ItemNotFound
from telegram_shop_bot.shops.abstract_shop import Shop, Item

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from unicodedata import normalize


class AliExpress(Shop):

    start_url = 'https://aliexpress.ru/'

    def __init__(self):
        options = webdriver.ChromeOptions()
        options.headless = True
        self.__driver = webdriver.Chrome(options=options)
        self.__driver.set_window_size(1440, 900)
        self.__driver.get(self.start_url)

        self.__soup = None

    def __find_items(self, item: str, num: int):
        search = self.__driver.find_element(
            by=By.NAME,
            value='SearchText'
        )
        search.click()
        search.send_keys(item)
        search.send_keys(Keys.ENTER)
        self.__driver.implicitly_wait(2)

        all_items = self.__driver.find_elements(
            by=By.CLASS_NAME,
            value='product-snippet_ProductSnippet__content__152uer'
        )
        return all_items[:num]

    def __set_html(self, item):
        html = item.get_attribute('innerHTML')
        self.__soup = BeautifulSoup(html, 'lxml')

    def _get_name(self):
        name = self.__soup.find('div', class_='product-snippet_ProductSnippet__name__152uer')\
            .text.replace('...', '')
        return name

    def _get_price(self):
        price = self.__soup.find('div', class_='snow-price_SnowPrice__mainM__bz77le').text
        return price

    def _get_reference(self):
        ref = self.__soup.find('div', class_='product-snippet_ProductSnippet__description__152uer').find('a')['href']
        return 'https://aliexpress.ru' + ref

    def _get_picture_ref(self):
        img_ref = self.__soup.find('img', class_='gallery_Gallery__image__1ln22f')['src']
        return 'https:' + img_ref

    def find_items(self, item: str, num: int):
        raw_items = self.__find_items(item, num)
        if len(raw_items) == 0:
            raise ItemNotFound
        items = []
        print(len(raw_items))
        for item in raw_items:
            self.__set_html(item)
            price = self._get_price()
            name = self._get_name()
            ref = self._get_reference()
            img_ref = self._get_picture_ref()
            items.append(Item(name, price, ref, img_ref))
        self.__driver.close()
        return items


if __name__ == '__main__':
    ali_express = AliExpress()
    things = ali_express.find_items('футболка мужская', 5)
    for item in things:
        print(item.get_info())
