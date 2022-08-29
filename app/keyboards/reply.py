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
