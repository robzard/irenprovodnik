import logging

from aiogram import Bot, Dispatcher, types, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State, default_state
from yookassa import Configuration, Payment

from config_data.config import load_config
from pathlib import Path
import sys

root_path = Path(__file__).parent.parent.parent.parent
sys.path.append(str(root_path))

from yookassa_payment.yookassa_handler import YookassaHandler

from keyboards.user import inline

config = load_config()

# Настройка YooKassa
Configuration.account_id = config.yookassa.shop_id
Configuration.secret_key = config.yookassa.secret_key


# Определение состояний
class SubscriptionState(StatesGroup):
    awaiting_payment_confirmation = State()


router = Router(name=__name__)


@router.message(Command('start'))
async def subscribe_command(message: types.Message, state: FSMContext):
    await state.clear()
    yk = YookassaHandler()
    url: str = yk.create_first_payment()

    await state.update_data(yk=yk)
    print(f'payment.id - {yk.payment_id}')
    await message.answer("Перейдите по ссылке для оплаты подписки:", reply_markup=inline.payment(url))


# Проверка статуса платежа
@router.message(StateFilter(SubscriptionState.awaiting_payment_confirmation))
async def payment_confirmation_check(message: types.Message, state: FSMContext):
    data = await state.get_data()
    payment_id = data.get('payment_id')
    if payment_id:
        payment = Payment.find_one(payment_id)
        if payment.status == 'succeeded':
            await message.answer("Спасибо за подписку! Теперь вы имеете доступ к каналу.")
            await state.set_state(default_state)
        else:
            await message.answer("Платеж не найден или не завершен. Пожалуйста, проверьте и попробуйте еще раз.")
    else:
        await message.answer("Не удалось найти информацию о платеже.")


# Функция для создания рекуррентного платежа
async def create_recurring_payment(payment_method_id):
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


# Команда для продления подписки
@router.message(Command('renew_subscription'))
async def renew_subscription(message: types.Message, state: FSMContext):
    data = await state.get_data()
    payment_method_id = data.get('payment_id')
    payment = await create_recurring_payment(payment_method_id)

    while payment.status != 'succeeded':
        payment = Payment.find_one(payment_method_id)

    if payment.status == 'succeeded':
        await message.answer("Ваша подписка успешно продлена на следующий месяц.")
    else:
        await message.answer("Не удалось продлить подписку. Пожалуйста, попробуйте снова.")
