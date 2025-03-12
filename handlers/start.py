from aiogram import Router, F
from aiogram.types import Message

from keyboards.all_kb import main_kb

start_router = Router()


@start_router.message(F.text == '/start')
async def start(message: Message):
    """Обработчик команды /start"""
    await message.answer('Добро пожаловать в магазин китайского чая "Первый чайный"',
                         reply_markup=main_kb(message.from_user.id))

