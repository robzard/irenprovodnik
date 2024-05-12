import os

from yookassa import Configuration, Payment

Configuration.account_id = os.getenv('YOOKASSA_SHOP_ID')
Configuration.secret_key = os.getenv('YOOKASSA_SECRET_KEY')


async def create_recurring_payment(user_id, payment_id):
    payment = Payment.create({
        'amount': {
            'value': '100.00',
            'currency': 'RUB'
        },
        'capture': True,
        'description': 'Ежемесячная подписка на канал',
        'payment_method_id': payment_id,
        'metadata': {
            'telegram_user_id': user_id
        }
    })
    return payment
