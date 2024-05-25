from aiogram.types import ChatInviteLink
from aiogram.utils.keyboard import InlineKeyboardBuilder

from common.db.models import Payments
import os
from aiogram import Bot


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
