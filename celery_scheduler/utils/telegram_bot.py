import logging
import os
from aiogram import Bot
from yookassa import Payment

from db.requests import get_last_payment_id
from utils.yookassa_payment import create_recurring_payment


async def subscription_expired(user_id):
    bot = Bot(token=os.getenv('BOT_TOKEN'), parse_mode='HTML')

    try:
        text = f'Ваша подписка истекла, чтобы продлить подписку нажмите на кнопку.'
        await bot.send_message(user_id, text)
    except Exception as ex:
        logging.warning(f'Пользователю {user_id} не удалось отправить сообщение - {str(ex)}')
    finally:
        await bot.session.close()


async def subscription_extended(user_id):
    bot = Bot(token=os.getenv('BOT_TOKEN'), parse_mode='HTML')

    try:
        text = f'Ваша подписка продлена автоматически.'
        await bot.send_message(user_id, text)
    except Exception as ex:
        logging.warning(f'Пользователю {user_id} не удалось отправить сообщение - {str(ex)}')
    finally:
        await bot.session.close()


async def renew_subscription(user_id):
    bot = Bot(token=os.getenv('BOT_TOKEN'), parse_mode='HTML')
    try:
        last_payment_id = await get_last_payment_id(user_id)
        payment = await create_recurring_payment(user_id, last_payment_id)

        while payment.status not in ('succeeded', 'canceled'):
            payment = Payment.find_one(payment.id)
        return payment
    except Exception as ex:
        logging.error(f'Пользователю {user_id} не автоматически списать деньги - {str(ex)}')
    finally:
        await bot.session.close()
