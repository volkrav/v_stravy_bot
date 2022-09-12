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

'''************************ Меню перегляду замовлення ************************'''

kb_menu_view_order = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='🚀 Оформити'),
            KeyboardButton(text='✏️ Змінити'),
        ],
        [
            KeyboardButton(text='🧹 Очистити'),
            KeyboardButton(text='↩️ До каталогу'),
        ],
    ],
    resize_keyboard=True
)

'''************************ Меню оформлення замовлення ************************'''

btn_delivery = KeyboardButton(text='🚚 Доставка')
btn_pickup = KeyboardButton(text='💪 Самовивіз')
btn_cancel_ordering = KeyboardButton(text='❌ Відміна')

kb_ordering = ReplyKeyboardMarkup(resize_keyboard=True).row(
    btn_pickup, btn_delivery).add(btn_cancel_ordering)



# 💪 Самовивіз
