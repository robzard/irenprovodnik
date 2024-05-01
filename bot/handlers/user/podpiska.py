import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State, default_state
from yookassa import Configuration, Payment
from aiogram import types

from config_data.config import load_config

config = load_config()

# Настройка бота и диспетчера
bot = Bot(token=config.tg_bot.token)
dp = Dispatcher()

# Настройка YooKassa
Configuration.account_id = config.yookassa.shop_id
Configuration.secret_key = config.yookassa.secret_key


# Определение состояний
class SubscriptionState(StatesGroup):
    awaiting_payment_confirmation = State()


@dp.message(Command('subscribe'))
async def subscribe_command(message: types.Message, state: FSMContext):
    payment = Payment.create({
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
    button = types.InlineKeyboardButton(text="Оплатить подписку", url=payment.confirmation.confirmation_url)
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[button]])  # Создаем объект клавиатуры

    await state.update_data(payment_id=payment.id)
    print(f'payment.id - {payment.id}')
    await state.set_state(SubscriptionState.awaiting_payment_confirmation)
    await message.answer("Перейдите по ссылке для оплаты подписки:", reply_markup=keyboard)


# Проверка статуса платежа
@dp.message(StateFilter(SubscriptionState.awaiting_payment_confirmation))
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
@dp.message(Command('renew_subscription'))
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


def set_logger():
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    stream_handler = logging.StreamHandler(sys.stderr)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s:%(lineno)d - %(message)s')
    stream_handler.setFormatter(formatter)
    root_logger.addHandler(stream_handler)


async def main() -> None:
    set_logger()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
