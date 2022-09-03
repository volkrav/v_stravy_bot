from aiogram.utils.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from app.models import db_api


'''************************ Меню ************************'''


menu_cd = CallbackData('show_menu', 'level', 'category', 'product', 'msg_id')


def make_callback_data(level, category='0', product='0', msg_id='0'):
    return menu_cd.new(level=level, category=category, product=product, msg_id=msg_id)


async def categories_keyboard():
    CURRENT_LEVEL = 1

    categories = await db_api.load_all_categories()

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

    return markup


async def products_keyboard(category):
    CURRENT_LEVEL = 2

    products = await db_api.load_products(['uid', 'title', 'partuids'])

    markup = InlineKeyboardMarkup()

    for product in products:
        if category in product['partuids']:

            button_text = product['title']
            callback_data = make_callback_data(
                level=CURRENT_LEVEL+1, product=product['uid'], category=category)

            markup.add(
                InlineKeyboardButton(
                    text=button_text,
                    callback_data=callback_data
                )
            )

    markup.row(
        InlineKeyboardButton(
            text='↩️ Назад',
            callback_data=make_callback_data(level=CURRENT_LEVEL-1)
        )
    )

    return markup


async def product_keyboard(title, uid, price, category):
    CURRENT_LEVEL = 3

    markup = InlineKeyboardMarkup(row_width=2)

    button_text = f'Додати до 🛒'
    callback_data = f'buy:{category}:{uid}'

    markup.row(
        InlineKeyboardButton(
            text='↩️ Назад',
            callback_data=make_callback_data(
                level=CURRENT_LEVEL-1, category=category)
        ),
        InlineKeyboardButton(
            text=button_text,
            callback_data=callback_data
        )
    )

    return markup

'''************************ Buy ************************'''
# 🛒 Кошик
