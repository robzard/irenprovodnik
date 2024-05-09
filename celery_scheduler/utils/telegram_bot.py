import os
from aiogram import Bot


async def subscription_expired(user_id):
    bot = Bot(token=os.getenv('BOT_TOKEN'), parse_mode='HTML')

    try:
        text = f'Ваша подписка истекла, чтобы продлить подписку нажмите на кнопку.'
        await bot.send_message(user_id, text)
    finally:
        await bot.session.close()
