from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import Command, state
from aiogram.types import Message

from config import config, admins_id
from db import insert_product, insert_article
from keyboards.all_kb import admin_kb, main_kb

admin_route = Router()


async def is_admin(message: types.Message):
    return message.from_user.id in admins_id


class AddProductState(StatesGroup):
    """Состояния для добавления товара"""
    waiting_for_name = State()
    waiting_for_description = State()
    waiting_for_price = State()
    waiting_for_image = State()
    waiting_for_category_id = State()


class AddArticle(StatesGroup):
    """Состояния для добавления статей"""
    waiting_for_title = State()
    waiting_for_description = State()


@admin_route.message(is_admin, F.text == "⚙️ Админ панель")
async def cmd_admin_panel(message: Message):
    """Обработчик команды админ панели"""
    await message.answer("Вы в админ панели", reply_markup=admin_kb())


@admin_route.message(is_admin, F.text == "Выйти")
async def cmd_exit(message: Message):
    """Обработчик команды выхода из админ панели"""
    await message.answer("До свидания!", reply_markup=main_kb(message.from_user.id))


@admin_route.message(is_admin, F.text == "Добавить статью")
async def cmd_add_article(message: Message, state: FSMContext):
    """Обработчик команды добавления статьи"""
    await state.set_state(AddArticle.waiting_for_title)
    await message.answer("Отправьте название статьи:")


@admin_route.message(F.text, AddArticle.waiting_for_title)
async def process_title(message: Message, state: FSMContext):
    """Обработчик названия статьи"""
    await state.update_data(title=message.text)
    await message.answer("Отправьте описание статьи:")
    await state.set_state(AddArticle.waiting_for_description)


@admin_route.message(F.text, AddArticle.waiting_for_description)
async def process_description_article(message: Message, state: FSMContext):
    """Обработчик описания статьи"""
    await state.update_data(description=message.text)
    data = await state.get_data()
    title = data['title']
    description = data["description"]
    insert_article(title, description)
    await message.answer("Статья добавлена!")
    await message.answer(f"Статья \"{title}\" успешно добавлена.")
    await state.clear()


@admin_route.message(is_admin, F.text == "Добавить продукт")
async def cmd_add_product(message: Message, state: FSMContext):
    """Обработчик команды добавления товара"""
    await state.set_state(AddProductState.waiting_for_name)
    await message.answer("Отправьте название товара:")


# Ожидание названия товара
@admin_route.message(F.text, AddProductState.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    """Обработчик названия товара"""
    await state.update_data(name=message.text)
    await message.answer("Отправьте описание товара:")
    await state.set_state(AddProductState.waiting_for_description)


# Ожидание описания товара
@admin_route.message(F.text, AddProductState.waiting_for_description)
async def process_description(message: Message, state: FSMContext):
    """Обработчик описания товара"""
    await state.update_data(description=message.text)
    await message.answer("Отправьте цену товара (в рублях):")
    await state.set_state(AddProductState.waiting_for_price)


# Ожидание цены товара
@admin_route.message(F.text, AddProductState.waiting_for_price)
async def process_price(message: Message, state: FSMContext):
    """Обработчик цены товара"""
    try:
        price = float(message.text)
    except ValueError:
        await message.answer("Цена должна быть числом. Попробуйте снова:")
        return
    await state.update_data(price=message.text)
    await message.answer("Отправьте ссылку на изображение товара:")
    await state.set_state(AddProductState.waiting_for_image)


# Ожидание ссылки на изображение товара
@admin_route.message(F.text, AddProductState.waiting_for_image)
async def process_image_url(message: Message, state: FSMContext):
    """Обработчик ссылки на изображение товара"""
    await state.update_data(image=message.text)
    await message.answer("Отправьте ID категории товара:")
    await state.set_state(AddProductState.waiting_for_category_id)


# Ожидание ID категории товара
@admin_route.message(F.text, AddProductState.waiting_for_category_id)
async def process_category_id(message: Message, state: FSMContext):
    """Обработчик ID категории товара"""
    try:
        category_id = int(message.text)
    except ValueError:
        await message.answer("ID категории должен быть числом. Попробуйте снова:")
        return
    print(f"Категория получена {category_id}")
    await state.update_data(category_id=message.text)
    # Получаем все данные из состояния
    data = await state.get_data()
    name = data['name']
    description = data['description']
    price = data['price']
    image = data['image']
    category_id = data['category_id']

    # Вставляем товар в базу данных
    insert_product(name, description, price, image, category_id)

    await message.answer(f"Товар \"{name}\" успешно добавлен.")
    await state.clear()
