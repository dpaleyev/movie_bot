import os

from aiogram import Bot
from aiogram import Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
import asyncio
import logging
import sys

from handlers import movie, commands
import src.database as db

bot = Bot(token=os.environ['BOT_TOKEN'])
dp = Dispatcher()

BASE_WEBHOOK_URL = "http://moviebot.alwaysdata.net/"
WEBHOOK_PATH = "/movie_bot/"

WEB_SERVER_HOST = '::'
WEB_SERVER_PORT = 8350

async def on_startup(bot: Bot) -> None:
    await bot.set_webhook(f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}")

async def main():
    db.setup()
    dp.include_router(commands.router)
    dp.include_router(movie.router)
    bot.delete_webhook(drop_pending_updates=True)

    dp.startup.register(on_startup)

    app = web.Application()

    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot
    )

    webhook_requests_handler.register(app, path=WEBHOOK_PATH)

    setup_application(app, dp, bot=bot)

    web.run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
