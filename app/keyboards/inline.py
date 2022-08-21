from aiogram.utils.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


'''************************ Меню ************************'''


menu_cd = CallbackData('show_menu', 'level', 'category', 'item')


categories = ['Новинки', 'Перші страви', 'Випічка', 'Пельмені',
              'Вареники', 'Котлети', 'Чебуреки', 'Крученики', 'Млинці']

items = {'Котлети': ['котлета1', 'котлета2', 'котлета3']}


def make_callback_data(level, category='0', item='0'):
    return menu_cd.new(level=level, category=category, item=item)


async def categories_keyboard():
    CURRENT_LEVEL = 0

    markup = InlineKeyboardMarkup()

    for category in categories:
        button_text = f'{category}'
        callback_data = make_callback_data(
            level=CURRENT_LEVEL+1, category=category)

        markup.insert(
            InlineKeyboardButton(
                text=button_text,
                callback_data=callback_data
            )
        )

    return markup


async def item_keyboard(category):
    CURRENT_LEVEL = 1

    markup = InlineKeyboardMarkup()

    for k, v in items.items():
        if category == k:
            for item in v:
                button_text = item
                callback_data = item

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
