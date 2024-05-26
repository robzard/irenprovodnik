import logging

from aiogram.enums import ChatMemberStatus
from aiogram.types import ChatInviteLink
from aiogram.utils.keyboard import InlineKeyboardBuilder

from common.db.models import Payments
import os
from aiogram import Bot


private_channel_id = '-1002243003596'


async def send_telegram_message_succeeded(payment: Payments):
    bot = Bot(token=os.getenv('BOT_TOKEN'), parse_mode='HTML')
    description_type = {'Первоначальная подписка на канал': 'Оплата подписки', 'Ежемесячная подписка на канал': 'Продление подписки'}
    link: ChatInviteLink = await bot.create_chat_invite_link('-1002243003596', member_limit=1)

    try:
        if payment.status == "succeeded":
            text = (f'{description_type[payment.description]} на сумму {payment.amount} рублей прошла успешно!\n'
                    f'Подписка на приватный канал оформлена, чтобы подписаться на канал нажмите на кнопку "Подписаться на канал".\n\n'
                    f'Деньги будут списываться ежемесячно автоматически (автоплатёж) для продления подписки, если хотите отменить автоплатёж, нажмите на кнопку "Отменить автоплатёж"')
            await bot.send_message(payment.user_id, text, reply_markup=inline_button_invite_link(link))
    finally:
        await bot.session.close()


def inline_button_invite_link(link: ChatInviteLink):
    builder = InlineKeyboardBuilder()
    builder.button(text="Подписаться на канал", url=link.invite_link)
    return builder.as_markup()


async def unban_chat_member(user_id):
    bot = Bot(token=os.getenv('BOT_TOKEN'), parse_mode='HTML')

    try:
        logging.info('Разбан пользователя канала')

        chat_member = await bot.get_chat_member(chat_id=private_channel_id, user_id=user_id)
        if chat_member.status == ChatMemberStatus.KICKED:
            await bot.unban_chat_member(chat_id=private_channel_id, user_id=user_id)
            logging.info('Пользователь разбанен в канале успешно')
        else:
            logging.info('Пользователь не забанен, пропуск события')
    except Exception as ex:
        logging.error(f'Не удалось разбанить пользователя в канале - {user_id} ({str(ex)})')
    finally:
        await bot.session.close()