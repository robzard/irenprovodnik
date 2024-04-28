import asyncio
import logging

import sys
from logging.handlers import TimedRotatingFileHandler

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage, Redis

from sqlalchemy import create_engine

from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine

from handlers.user import include_routers
from config_data.config import load_config
from db.db import BaseManager
from middlewares.middlewares import DatabaseSessionMiddleware, ThrottlingMiddleware, CallbackThrottlingMiddleware

TEST_MODE = True if sys.argv[-1] == 'local_testing' else False

config = load_config()

db_url = f"postgresql+psycopg://{config.db.db_user}:{config.db.db_password}@{config.db.db_host}/{config.db.database}?options=-c%20timezone%3DAsia/Yekaterinburg"
engine: AsyncEngine = create_async_engine(db_url)
engine_sync = create_engine(db_url, connect_args={"options": "-c timezone=Asia/Yekaterinburg"})
AsyncSession: sessionmaker[AsyncSession] = sessionmaker(
    bind=engine, expire_on_commit=False, class_=AsyncSession
)

redis = Redis(host=config.redis.host,
              port=config.redis.port,
              db=config.redis.db)
storage = RedisStorage(redis)

bot = Bot(token=config.tg_bot.token, parse_mode='HTML')


def create_database_and_tables():
    bm = BaseManager()
    bm.create_database_and_tables(engine_sync)


async def on_startup():
    await bot.delete_webhook()
    await bot.set_webhook(config.tg_bot.webhook.url,
                          secret_token=config.tg_bot.webhook.secret)


async def on_shutdown():
    await bot.delete_webhook()


async def main() -> None:
    create_database_and_tables()

    bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
    dp = Dispatcher()

    # await bot.delete_webhook()

    # dp.message.middleware(RateLimitMiddleware())
    dp.update.outer_middleware(DatabaseSessionMiddleware(bot, AsyncSession))
    dp.message.middleware(ThrottlingMiddleware())
    dp.callback_query.middleware(CallbackThrottlingMiddleware())

    include_routers(dp)

    await dp.start_polling(bot)


def set_logger():
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    stream_handler = logging.StreamHandler(sys.stderr)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s:%(lineno)d - %(message)s')
    stream_handler.setFormatter(formatter)
    root_logger.addHandler(stream_handler)
    file_handler = TimedRotatingFileHandler("logs/aiogram_bot.log", when="midnight", interval=1, backupCount=10)
    file_handler.suffix = "%Y-%m-%d"  # Формат имени файла лога
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)


if __name__ == "__main__":
    set_logger()

    # logger = setup_logger(__name__, 'logfile.log')
    asyncio.run(main())
    # main()
