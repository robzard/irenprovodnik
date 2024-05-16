import os

from yookassa import Configuration, Payment
from yookassa.domain.response import PaymentResponse

# from config_data.config import load_config
#
# config = load_config()
Configuration.account_id = os.getenv('YOOKASSA_SHOP_ID')
Configuration.secret_key = os.getenv('YOOKASSA_SECRET_KEY')


class YookassaHandler:

    def __init__(self):
        self.payment_id = None
        self.payment = None

    def create_first_payment(self) -> str:
        payment: PaymentResponse = Payment.create({
            'amount': {
                'value': '100.00',
                'currency': 'RUB'
            },
            'confirmation': {
                'type': 'redirect',
                'return_url': 'https://your-website.com/return'
            },
            'capture': True,
            'description': 'Первоначальная подписка на канал',
            'save_payment_method': True,
            'payment_method_data': {
                'type': 'bank_card'
            }
        })

        self.payment_id: str = payment.id
        return payment.confirmation.confirmation_url

    async def create_recurring_payment(self, user_id, payment_id):
        self.payment = Payment.create({
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
        return self.payment
