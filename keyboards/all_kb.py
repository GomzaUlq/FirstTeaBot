from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import admins_id


def main_kb(user_telegram_id: id) -> ReplyKeyboardMarkup:
    """Клавиатура для пользователей"""
    kb_list = [
        [KeyboardButton(text='Категории'), KeyboardButton(text='Корзина')],
        [KeyboardButton(text='Статьи')],
        [KeyboardButton(text='О нас'), KeyboardButton(text='Контакты')]
    ]
    if user_telegram_id in admins_id:
        kb_list.append([KeyboardButton(text="⚙️ Админ панель")])
    keyboard = ReplyKeyboardMarkup(keyboard=kb_list, resize_keyboard=True, one_time_keyboeard=True)
    return keyboard


def admin_kb() -> ReplyKeyboardMarkup:
    """Клавиатура для администраторов"""
    kb_list = [
        [KeyboardButton(text='Добавить продукт')],
        [KeyboardButton(text='Добавить статью')],
        [KeyboardButton(text='Выйти')]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb_list, resize_keyboard=True, one_time_keyboeard=True)
    return keyboard


def article(articles) -> InlineKeyboardMarkup:
    """Клавиатура для статей"""
    kb = InlineKeyboardBuilder()
    for article in articles:
        kb.button(text=article[1], callback_data=f'article:{article[0]}')
    kb.adjust(2)
    return kb.as_markup()


def catalog_kb(categories) -> InlineKeyboardMarkup:
    """Клавиатура для категорий"""
    kb = InlineKeyboardBuilder()
    for category in categories:
        kb.button(text=category[1], callback_data=f'category:{category[0]}')
    kb.adjust(2)
    return kb.as_markup()


def product_kb(products):
    """Клавиатура для продуктов"""
    kb = InlineKeyboardBuilder()
    for product in products:
        kb.button(text=product[1], callback_data=f'product:{product[0]}')
    kb.adjust(2)
    return kb.as_markup()


def add_to_cart_kb(product_id):
    """Клавиатура для добавления продукта в корзину"""
    kb = InlineKeyboardBuilder()
    kb.button(text='Добавить в корзину', callback_data=f'add_to_cart:{product_id}')
    kb.button(text='Выбрать другой товар', callback_data='select_product')
    kb.adjust(2)
    return kb.as_markup()


def manage_cart_kb(cart) -> InlineKeyboardMarkup:
    """Клавиатура для управления корзиной"""
    kb = InlineKeyboardBuilder()
    for item in cart:
        id, product_name, product_id, quality = item
        kb.button(text=f"{product_name} (x{quality})", callback_data=f'manage_cart:{product_id}')
        kb.button(text='+', callback_data=f'update_quality:{id}:inc')
        kb.button(text='-', callback_data=f'update_quality:{id}:dec')
        kb.button(text='Удалить', callback_data=f'delete:{id}')
    kb.button(text='Оформить заказ', callback_data='order')
    kb.adjust(4)
    return kb.as_markup()


def order_kb(cart_id):
    """Клавиатура для оформления заказа"""
    kb = InlineKeyboardBuilder()
    kb.button(text='Оформить заказ', callback_data=f'order:{cart_id}')
    kb.adjust(2)
    return kb.as_markup()
