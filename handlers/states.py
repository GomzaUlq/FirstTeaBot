from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from db import get_article, get_article_by_id
from handlers.cart import conn
from keyboards.all_kb import article

states_router = Router()


@states_router.message(F.text == 'Статьи')
async def cmd_articles(message: Message):
    """Обработчик команды для просмотра статей."""
    articles = get_article(conn)
    with open('all_media/for_article.txt', 'r', encoding='utf-8') as f:
        about = f.read()
        print("Файл прочитан")
    if not articles:
        await message.answer('Статей пока нет')
    await message.answer(about, reply_markup=article(articles))


@states_router.callback_query(F.data.startswith('article:'))
async def handle_articles_choice(callback_query: CallbackQuery):
    """Обработчик выбора статьи и отображения её содержимого."""
    article_id = int(callback_query.data.split(':')[1])
    article = get_article_by_id(conn, article_id)
    if not article:
        await callback_query.message.answer("Статья не найдена.")
        return
    title, description = article[1], article[2]
    await callback_query.message.answer(f"<b>{title}</b>\n{description}")
