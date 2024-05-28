import asyncio
import os
import sys

# Явное добавление пути к common
# sys.path.insert(0, '/common')

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
import logging
import utils.telegram_bot as tg

# sys.path.append('/common')

from common.db.requests import get_users_subscription_expired, set_subscription_false, set_subscription_true, get_users_subscription_notification

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


async def my_daily_task():
    await users_notification()

    users = await get_users_subscription_expired()
    logging.info(f'get_users_subscription_expired: {len(users)}')
    for user in users:
        logging.info(f'user_id: {user.user_id}')
        if user.auto_payment:
            await tg.renew_subscription(user)
        else:
            await tg.subscription_expired(user)
    logging.info("Выполнение задачи: %s", datetime.now())


async def users_notification():
    users_need_notification = await get_users_subscription_notification()
    for user in users_need_notification:
        logging.info(f'user_id notification: {user.user_id}')
        await tg.user_notification(user)


scheduler = AsyncIOScheduler()

# scheduler.add_job(my_daily_task, 'cron', hour=13, minute=1)
scheduler.add_job(my_daily_task, 'interval', minutes=1)

# Запускаем планировщик
scheduler.start()

try:
    asyncio.get_event_loop().run_forever()
except (KeyboardInterrupt, SystemExit):
    pass
