import logging
import os
from aiogram import Bot
from aiogram.utils.keyboard import InlineKeyboardBuilder
from yookassa import Payment

from common.db.models import User
from common.db.requests import get_last_payment_id, set_subscription_true, set_subscription_false, set_user_subscription_notification
from common.yookassa_payment.yookassa_handler import YookassaHandler

private_channel_id = '-1002243003596'


def inline_payment(url: str):
    builder = InlineKeyboardBuilder()
    builder.button(text="Оформить подписку", url=url)
    builder.button(text="☰ Меню", callback_data='start')
    builder.adjust(1)
    return builder.as_markup()


def inline_menu():
    builder = InlineKeyboardBuilder()
    builder.button(text="☰ Меню", callback_data='start')
    builder.adjust(1)
    return builder.as_markup()


async def subscription_expired(user: User):
    bot = Bot(token=os.getenv('BOT_TOKEN'), parse_mode='HTML')

    await set_subscription_false(user)

    try:
        yk = YookassaHandler()
        url: str = yk.create_first_payment(user.user_id)
        text = f'Ваша подписка истекла, чтобы продлить подписку нажмите на кнопку.'
        await bot.send_message(user.user_id, text, reply_markup=inline_payment(url))
        await ban_chat_member(user.user_id)
    except Exception as ex:
        logging.warning(f'Пользователю {user.user_id} не удалось отправить сообщение - {str(ex)}')
    finally:
        await bot.session.close()


async def user_notification(user: User):
    bot = Bot(token=os.getenv('BOT_TOKEN'), parse_mode='HTML')
    text = "Ваша подписка на приватный канал истекает через 3 дня."
    if user.auto_payment:
        text += "\n\nЗа продление подписки деньги спишутся автоматически с вашей карты - у вас включён автоплатёж.\nЕсли хотите отключить автоплатёж, перейдите в настройки подписки и нажмите 'Отключить автоплатёж'"
    else:
        text += "\n\nУ вас отключён автоплатёж для продления подписки.\nЕсли хотите, чтобы подписка продливалась автоматически, то перейдите в настройки подписки и нажмите 'Включить автоплатёж'"
    try:
        await bot.send_message(user.user_id, text, reply_markup=inline_menu())
        await set_user_subscription_notification(user, True)
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
            await set_user_subscription_notification(user, False)
        else:
            yk = YookassaHandler()
            url: str = yk.create_first_payment(user.user_id)
            await set_subscription_false(user)
            await ban_chat_member(user.user_id)
            await bot.send_message(user.user_id, "Не удалось продлить подписку. Пожалуйста, попробуйте снова.", reply_markup=inline_payment(url))
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
