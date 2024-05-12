from yookassa import Payment


async def create_recurring_payment(user_id, payment_id):
    payment = Payment.create({
        'amount': {
            'value': '100.00',
            'currency': 'RUB'
        },
        'capture': True,
        'description': 'Ежемесячная подписка на канал',
        'payment_method_id': '2dc597a4-000f-5000-9000-139de27893c0',
        'metadata': {
            'telegram_user_id': user_id
        }
    })
    return payment



