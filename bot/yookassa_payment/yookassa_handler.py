from yookassa import Configuration, Payment
from yookassa.domain.response import PaymentResponse

from config_data.config import load_config

config = load_config()
Configuration.account_id = config.yookassa.shop_id
Configuration.secret_key = config.yookassa.secret_key


class YookassaHandler:

    def __init__(self):
        self.payment_id = None
        self.payment = None

    def create_first_payment(self, user_id) -> str:
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
            },
            'metadata': {
                'telegram_user_id': user_id  # Сохранение ID пользователя Telegram
            }
        })

        self.payment_id: str = payment.id
        return payment.confirmation.confirmation_url

    async def create_recurring_payment(self, payment_method_id):
        payment = Payment.create({
            'amount': {
                'value': '100.00',
                'currency': 'RUB'
            },
            'capture': True,
            'description': 'Ежемесячная подписка на канал',
            'payment_method_id': payment_method_id  # Используем сохраненный payment_method_id
        })
        return payment
