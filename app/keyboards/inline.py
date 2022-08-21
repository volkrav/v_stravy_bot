from aiogram.utils.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


'''************************ Меню ************************'''


menu_cd = CallbackData('show_menu', 'level', 'category', 'item')


def make_callback_data(level, category='0', item='0'):
    return menu_cd(level=level, category=category, item=item)


async def categories_keyboard():
    CURRENT_LEVEL = 0

    markup = InlineKeyboardMarkup()

    categories = ['Новинки', 'Перші страви', 'Випічка', 'Пельмені', 'Вареники', 'Котлети', 'Чебуреки', 'Крученики', 'Млинці']

    for category in categories:
        button_text = f'{category}'
        callback_data = make_callback_data(level=CURRENT_LEVEL+1,
                                           category=category)

        markup.insert(
            InlineKeyboardButton(
                text=button_text,
                callback_data=callback_data
            )
        )

    return markup


async def items_keyboard(category):
    CURRENT_LEVEL = 1

    markup = InlineKeyboardMarkup(row_width=1)

    items = {'item1': 10, 'item2': 20, 'item3': 30, 'item4': 40, 'item5': 50}

    for key, value in items.items():
        button_text = f'{key} - ${value}'
        callback_data = make_callback_data(level=CURRENT_LEVEL+1,
                                           category=category,
                                           item=key)

    markup.insert(
        InlineKeyboardButton(
            text=button_text,
            callback_data=callback_data
        )
    )
    markup.row(
        InlineKeyboardButton(
            text='Назад',
            callback_data=make_callback_data(
                level=CURRENT_LEVEL-1, category=category)
        )
    )
    return markup


async def item_keyboard(category, item):
    CURRENT_LEVEL = 2

    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardMarkup(text='Купити', callback_data=item)
    )
    markup.row(
        InlineKeyboardButton(
            text='Назад',
            callback_data=make_callback_data(
                level=CURRENT_LEVEL-1, category=category)
        )
    )
    return markup
