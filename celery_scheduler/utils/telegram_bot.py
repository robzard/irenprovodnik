import logging
import os
from aiogram import Bot
from yookassa import Payment

from common.db.models import User
from common.db.requests import get_last_payment_id, set_subscription_true, set_subscription_false
from common.yookassa_payment.yookassa_handler import YookassaHandler

private_channel_id = '-1002243003596'


async def subscription_expired(user: User):
    bot = Bot(token=os.getenv('BOT_TOKEN'), parse_mode='HTML')

    await set_subscription_false(user)

    try:
        text = f'Ваша подписка истекла, чтобы продлить подписку нажмите на кнопку.'
        await bot.send_message(user.user_id, text)
        await ban_chat_member(user.user_id)
    except Exception as ex:
        logging.warning(f'Пользователю {user.user_id} не удалось отправить сообщение - {str(ex)}')
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


async def renew_subscription(user: User):
    bot = Bot(token=os.getenv('BOT_TOKEN'), parse_mode='HTML')
    yh = YookassaHandler()
    try:
        last_payment_id = await get_last_payment_id(user.user_id)
        payment = await yh.create_recurring_payment(user.user_id, last_payment_id)

        while payment.status not in ('succeeded', 'canceled'):
            payment = Payment.find_one(payment.id)

        if payment.status == 'succeeded':
            await set_subscription_true(user)
        else:
            await set_subscription_false(user)
            await ban_chat_member(user.user_id)
            await bot.send_message(user.user_id, "Не удалось продлить подписку. Пожалуйста, попробуйте снова.")
    except Exception as ex:
        logging.error(f'Пользователю {user.user_id} не автоматически списать деньги - {str(ex)}')
    finally:
        await bot.session.close()


async def ban_chat_member(user_id):
    bot = Bot(token=os.getenv('BOT_TOKEN'), parse_mode='HTML')

    try:
        logging.info('Бан пользователя из канала')
        await bot.ban_chat_member(chat_id=private_channel_id, user_id=user_id)
        logging.info('Пользователь забанен успешно')
    except Exception as ex:
        logging.error(f'Не удалось забанить пользователя с канала - {user_id} ({str(ex)})')
    finally:
        await bot.session.close()


async def unban_chat_member(user_id):
    bot = Bot(token=os.getenv('BOT_TOKEN'), parse_mode='HTML')

    try:
        logging.info('Разбан пользователя канала')
        await bot.unban_chat_member(chat_id=private_channel_id, user_id=user_id)
        logging.info('Пользователь разбанен в канале успешно')
    except Exception as ex:
        logging.error(f'Не удалось разбанить пользователя в канале - {user_id} ({str(ex)})')
    finally:
        await bot.session.close()
