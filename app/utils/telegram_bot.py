from data_base.models import Payments
import os
from aiogram import Bot

bot = Bot(token=os.getenv('BOT_TOKEN'), parse_mode='HTML')


async def send_telegram_message(payment: Payments):
    await bot.send_message(payment.user_id, 'TEST')
