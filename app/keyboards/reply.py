from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


'''************************ Стартове вікно ************************'''

kb_start = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Меню')
        ],
        [
            KeyboardButton(text='ℹ️ Про нас'),
            KeyboardButton(text='📞 Контакти')
        ],
        [
            KeyboardButton(text='💪 Самовивіз'),
            KeyboardButton(text='🚚 Доставка і оплата'),
        ],
        [
            KeyboardButton(text='😇 Особиста інформація')
        ]
    ],
    resize_keyboard=True
)

'''************************ Вікно каталогу ************************'''

kb_catalog = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Ваше замовлення')
        ],
        [
            KeyboardButton(text='✖️ Вихід')
        ]
    ],
    resize_keyboard=True
)

'''************************ Кількість товару при додаванні до корзини ************************'''

kb_quantity = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='1'),
            KeyboardButton(text='2'),
        ],
        [
            KeyboardButton(text='3'),
            KeyboardButton(text='4'),
        ],
        [
            KeyboardButton(text='Передумав')
        ]
    ],
    resize_keyboard=True
)
