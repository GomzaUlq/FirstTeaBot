from aiogram import Router, F
from aiogram.types import Message

about_router = Router()


@about_router.message(F.text == 'О нас')
async def about_us(message: Message):
    """О нас"""
    with open('all_media/about.txt', 'r', encoding='utf-8') as f:
        about = f.read()
    await message.answer(about)


@about_router.message(F.text == 'Контакты')
async def contact_us(message: Message):
    """Контакты"""
    with open('all_media/contact.txt', 'r', encoding='utf-8') as f:
        contact = f.read()
    await message.answer(contact)
