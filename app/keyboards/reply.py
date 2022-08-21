from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


'''************************ Стартове вікно ************************'''

kb_start = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Меню')
        ],
        [
            KeyboardButton(text='Розташування'),
            KeyboardButton(text='Умови доставки'),
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
            KeyboardButton(text='<- Повернутися')
        ]
    ],
    resize_keyboard=True
)
