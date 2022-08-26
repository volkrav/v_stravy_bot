from aiogram.utils.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from app.models import db_api


'''************************ Меню ************************'''


menu_cd = CallbackData('show_menu', 'level', 'category', 'item')


def make_callback_data(level, category='0', item='0'):
    return menu_cd.new(level=level, category=category, item=item)


async def categories_keyboard():
    CURRENT_LEVEL = 1

    categories = await db_api.load_categories()

    markup = InlineKeyboardMarkup()

    for category in categories:
        button_text = f'{category["name"]}'
        callback_data = make_callback_data(
            level=CURRENT_LEVEL+1, category=category['partuid'])

        markup.insert(
            InlineKeyboardButton(
                text=button_text,
                callback_data=callback_data
            )
        )
    markup.row(
        InlineKeyboardButton(
            text='<- Назад',
            callback_data=make_callback_data(level=CURRENT_LEVEL-1)
        )
    )

    return markup


async def products_keyboard(category):
    CURRENT_LEVEL = 2

    products = await db_api.load_products()

    markup = InlineKeyboardMarkup()

    for product in products:
        if category in product['partuids']:
            print(
                f"{category} in {product['partuids']} where {product['uid']}")
            button_text = product['title']
            callback_data = product['uid']

            markup.add(
                InlineKeyboardButton(
                    text=button_text,
                    callback_data=callback_data
                )
            )

    markup.row(
        InlineKeyboardButton(
            text='<- Назад',
            callback_data=make_callback_data(level=CURRENT_LEVEL-1)
        )
    )

    return markup
