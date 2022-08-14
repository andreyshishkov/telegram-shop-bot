from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from unicodedata import normalize

from telegram_shop_bot.exceptions import ItemNotFound
from telegram_shop_bot.shops.abstract_shop import Shop, Item


class WildBerries(Shop):

    start_url = 'https://www.wildberries.ru/'

    def __init__(self, ):
        options = webdriver.ChromeOptions()
        options.headless = True
        self.__driver = webdriver.Chrome(options=options)
        self.__driver.set_window_size(1440, 900)
        self.__driver.get(self.start_url)

        self.__soup = None

    def __find_items(self, item: str, num: int):
        search = self.__driver.find_element(
            by=By.ID,
            value='searchInput'
        )
        search.click()
        search.send_keys(item)
        search.send_keys(Keys.ENTER)
        self.__driver.implicitly_wait(3)

        self.__check_null()

        class_name = "product-card__wrapper"
        all_items = self.__driver.find_elements(
            by=By.CLASS_NAME,
            value=class_name
        )

        return all_items[:num]

    def __check_null(self):
        null = self.__driver.find_elements(
            by=By.CLASS_NAME,
            value='catalog-page__text'
        )
        for elem in null:
            if 'По Вашему запросу ничего не найдено' in normalize('NFKD', elem.get_attribute('innerHTML')):
                raise ItemNotFound

    def __set_html(self, item):
        html = item.get_attribute('innerHTML')
        self.__soup = BeautifulSoup(html, 'lxml')

    def _get_price(self):
        price = self.__soup.find(['ins', 'span'], class_='lower-price').text.strip()
        return normalize('NFKD', price)

    def _get_name(self):
        brand = self.__soup.find('strong', class_='brand-name').text
        name = self.__soup.find('span', class_='goods-name').text
        output_name = f'{brand}: {name}'
        return output_name

    def _get_picture_ref(self):
        img_ref = 'https:' + self.__soup.find('img', class_='j-thumbnail thumbnail')['src']
        return img_ref

    def _get_reference(self):
        reference = self.__soup.find('a', class_='product-card__main j-card-link')['href']
        return reference

    def find_items(self, item: str, num: int) -> list[Item]:
        raw_items = self.__find_items(item, num)
        if len(raw_items) == 0:
            raise ItemNotFound
        items = []
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
    wild_berries = WildBerries()
    things = wild_berries.find_items('футболка мужская', 5)
    for item in things:
        print(item.get_info())
