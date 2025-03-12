import os
from aiogram import F, Router
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext

from config import all_media_dir
from db import get_connection, get_products_by_category, get_category_by_id, get_categories, get_product_by_id, \
    add_to_cart
from keyboards.all_kb import catalog_kb, product_kb, add_to_cart_kb

conn = get_connection()
cursor = conn.cursor()

catalog_route = Router()


class CatalogState(StatesGroup):
    """Класс для состояний пользовательской машины состояний"""
    waiting_for_category = State()
    waiting_for_product = State()
    waiting_for_cart_action = State()


@catalog_route.message(F.text == 'Категории')
async def cmd_catalog(message: Message):
    """Отображает список категорий и предлагает выбрать категорию для просмотра товаров."""
    categories = get_categories(conn)
    if not categories:
        await message.answer("Категории отсутствуют. Обратитесь к администратору.")
        return
    await message.answer("Выберите категорию, в которой хотите просмотреть товары.",
                         reply_markup=catalog_kb(categories))


@catalog_route.callback_query(F.data.startswith('category'))
async def handle_category_choice(callback_query: CallbackQuery):
    """Обрабатывает выбор категории и отображает список товаров в выбранной категории."""
    await callback_query.answer()
    category_id = int(callback_query.data.split(':')[1])
    category = get_category_by_id(conn, category_id)
    if not category:
        await callback_query.message.answer("Категория не найдена.")
        return

    products = get_products_by_category(conn, category_id)
    response_message = f"Категория: {category[1]}\nОписание: {category[2]}"

    if not products:
        await callback_query.message.answer(f"{response_message}\nВ этой категории пока нет товаров.")
        return

    await callback_query.message.edit_text(response_message, reply_markup=product_kb(products))


@catalog_route.callback_query(F.data.startswith('product'))
async def handle_product_choice(callback_query: CallbackQuery):
    """Обрабатывает выбор товара и отображает информацию о выбранном товаре с кнопкой добавления в корзину."""
    await callback_query.answer()
    product_id = int(callback_query.data.split(':')[1])
    product = get_product_by_id(conn, product_id)
    if product:
        product_name, product_description, product_price, product_image = product[1], product[2], product[3], product[4]
        photo_file_path = os.path.join(all_media_dir, f"{product_image}")

        print(f"Путь к файлу изображения: {photo_file_path}")

        photo_file = FSInputFile(path=photo_file_path)

        try:
            await callback_query.message.answer_photo(
                photo=photo_file,
                caption=f"{product_name}\n\n{product_description}\nЦена за 25 гр: {product_price}₽",
                reply_markup=add_to_cart_kb(product_id)  # Передаем product_id
            )
        except Exception as e:
            await callback_query.message.answer("Ошибка при отправке изображения. Проверьте путь к файлу.")
            print(f"Ошибка: {e}")
    else:
        await callback_query.message.answer("Товар не найден.")


@catalog_route.callback_query(F.data.startswith('add_to_cart'))
async def add_to_cart_handler(callback_query: CallbackQuery, state: FSMContext):
    """Обрабатывает добавление товара в корзину и отображает соответствующее сообщение."""
    await callback_query.answer()
    await callback_query.answer("Товар добавлен в корзину!")
    data = callback_query.data
    _, product_id = data.split(':')  # Разделяем команду и идентификатор товара
    user_id = callback_query.from_user.id
    print(f"Пользователь: {user_id} хочет добавить {product_id} в корзину")
    add_to_cart(user_id, int(product_id))
    await state.clear()


@catalog_route.callback_query(F.data == 'select_product')
async def cmd_select_product(callback_query: CallbackQuery, state: FSMContext):
    """Обрабатывает выбор товара и возвращает пользователя к выбору категории."""
    await callback_query.answer()
    await state.clear()  # Сбрасываем состояние
    await cmd_catalog(callback_query.message)  # Возвращаемся к выбору категории
