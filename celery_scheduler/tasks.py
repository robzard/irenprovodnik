import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
import logging
import utils.telegram_bot as tg

from db.requests import get_users_subscription_expired, set_subscription_false, set_subscription_true

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


async def my_daily_task():
    users = await get_users_subscription_expired()
    logging.info(f'get_users_subscription_expired: {len(users)}')
    for user in users:
        logging.info(f'user_id: {user.user_id}')
        if user.auto_payment:
            payment = await tg.renew_subscription(user.user_id)
            if payment.status == 'succeeded':
                await set_subscription_true(user)
            else:
                await set_subscription_false(user)
        else:
            await set_subscription_false(user)
            await tg.subscription_expired(user.user_id)
    logging.info("Выполнение задачи: %s", datetime.now())


scheduler = AsyncIOScheduler()

# scheduler.add_job(my_daily_task, 'cron', hour=13, minute=1)
scheduler.add_job(my_daily_task, 'interval', minutes=1)

# Запускаем планировщик
scheduler.start()

try:
    asyncio.get_event_loop().run_forever()
except (KeyboardInterrupt, SystemExit):
    pass
