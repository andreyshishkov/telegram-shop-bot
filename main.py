import telebot
from telebot import types
import urllib

from telegram_shop_bot import config as cfg
from telegram_shop_bot.shops.ali_express import AliExpress
from telegram_shop_bot.shops.wild_berries import WildBerries
from telegram_shop_bot.exceptions import ItemNotFound

bot = telebot.TeleBot(cfg.TOKEN)
ali_express, wild_berries = AliExpress(), WildBerries()


@bot.message_handler(commands=['start'])
def greet(message: types.Message, text: str = 'Привет. Введите интересующий продукт'):
    bot.send_message(message.chat.id, text)


@bot.message_handler(content_types=['text'])
def get_product(message: types.Message):
    product = message.text

    keyboard = types.ReplyKeyboardMarkup()
    ali_express_button = types.KeyboardButton(cfg.ALIEXPRESS_BUTTON)
    wild_berries_button = types.KeyboardButton(cfg.WILD_BERRIES_BUTTON)
    all_button = types.KeyboardButton(cfg.ALL_BUTTON)
    keyboard.row(
        ali_express_button,
        wild_berries_button,
        all_button
    )
    shop_message = bot.send_message(
        chat_id=message.chat.id,
        text='Выберете магазин для поиска',
        reply_markup=keyboard)
    bot.register_next_step_handler(shop_message, find_item, product)


def find_item(shop_message: types.Message, product: str):
    bot.send_message(shop_message.chat.id, 'Пожалуйста подождите, идёт поиск')
    shop = shop_message.text
    items = []

    if shop == cfg.ALIEXPRESS_BUTTON:
        try:
            items.extend(ali_express.find_items(product, 5))
        except ItemNotFound:
            pass
    elif shop == cfg.WILD_BERRIES_BUTTON:
        try:
            items.extend(wild_berries.find_items(product, 5))
        except ItemNotFound:
            pass
    elif shop == cfg.ALL_BUTTON:
        try:
            items.extend(ali_express.find_items(product, 2))
        except ItemNotFound:
            pass

        try:
            items.extend(wild_berries.find_items(product, 2))
        except ItemNotFound:
            pass
    if len(items) == 0:
        bot.send_message(shop_message.chat.id, 'Товар не найден.')
    else:
        for item in items:
            response_message = f'{item.name};\nЦена: {item.price};\nСсылка: {item.reference}'
            img = urllib.request.urlopen(item.image_ref).read()
            bot.send_photo(shop_message.chat.id, img, caption=response_message)


if __name__ == '__main__':
    bot.infinity_polling()
