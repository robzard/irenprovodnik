from data_base.models import Payments
import os
from aiogram import Bot


async def send_telegram_message(payment: Payments):
    bot = Bot(token=os.getenv('BOT_TOKEN'), parse_mode='HTML')
    try:
        await bot.send_message(payment.user_id, 'TEST')
    finally:
        await bot.session.close()