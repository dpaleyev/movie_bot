import os

from aiogram import Bot
from aiogram import Dispatcher
from aiogram.filters.command import Command
import aiohttp
import asyncio

from handlers import movie, commands
import src.database as db

bot = Bot(token=os.environ['BOT_TOKEN'])
dp = Dispatcher()

async def main():
    db.setup()
    dp.include_router(commands.router)
    dp.include_router(movie.router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
