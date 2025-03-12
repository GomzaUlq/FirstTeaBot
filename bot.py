from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from config import config
import logging
import asyncio
from handlers.about import about_router
from handlers.admin import admin_route
from handlers.cart import cart_router
from handlers.catalog import catalog_route
from handlers.start import start_router
from handlers.states import states_router

logging.basicConfig(level=logging.DEBUG)
bot = Bot(token=config.bot_token.get_secret_value(), default=DefaultBotProperties(parse_mode='HTML'))
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
"""
Запуск бота
"""


async def main():
    dp.include_router(start_router)
    dp.include_router(catalog_route)
    dp.include_router(admin_route)
    dp.include_router(cart_router)
    dp.include_router(about_router)
    dp.include_router(states_router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info('Bot stopped')
