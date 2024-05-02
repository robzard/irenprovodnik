from data_base.models import Payments
import os
from aiogram import Bot


async def send_telegram_message(payment: Payments):
    bot = Bot(token=os.getenv('BOT_TOKEN'), parse_mode='HTML')
    description_type = {'Первоначальная подписка на канал': 'Оплата подписки', 'Ежемесячная подписка на канал': 'Продление подписки'}

    try:
        if payment.status == "succeeded":
            text = (f'{description_type[payment.description]} на сумму {payment.amount} рублей прошла успешно!\n'
                    f'Подписка на приватный канал оформлена, вы уже добавлены в канал, перейдите по ссылке.\n\n'
                    f'Деньги будут списываться ежемесячно автоматически (автоплатёж) для продления подписки, если хотите отменить автоплатёж, нажмите на кнопку "Отменить автоплатёж"')
            await bot.send_message(payment.user_id, text)
    finally:
        await bot.session.close()
