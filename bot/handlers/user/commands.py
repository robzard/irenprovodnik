import asyncio

from aiogram import Router, types, Bot
from aiogram.fsm.state import default_state
from aiogram.filters import CommandStart, StateFilter, Command

import logging

from aiogram.types import InputMediaPhoto, FSInputFile

# from custom_logger.logger import logger
from common.db.requests import get_all_users
from filters.all_filters import IsAdmin
from keyboards.user.inline import command_start, channel_move_to_chatbot, send_all
from lexicon.lexicon import LEXICON
from states.states import FSMGpt
from utils.utils import delete_need_messages, MessageEditor

# from custom_logger.logger import logger

router = Router(name=__name__)


@router.message(Command('forward_channel'), IsAdmin())
async def forward_message_to_channel(message: types.Message, bot: Bot):
    if message.reply_to_message:
        await bot.send_message(chat_id='@teylaschool_online', text=message.reply_to_message.text, reply_markup=channel_move_to_chatbot())
        await message.answer("Сообщение было переслано в канал.")
    else:
        await message.answer("Пожалуйста, используйте команду в ответ на сообщение, которое вы хотите переслать.")


@router.message(CommandStart(), StateFilter(default_state, FSMGpt.wait_question))
async def on_start(message: types.Message):
    image_path = './static/images/iren2.jpg'
    media = FSInputFile(image_path)
    await message.answer_photo(photo=media, caption=LEXICON['user_command_start'], reply_markup=command_start(message.from_user.id))


@router.message(Command('send_all'), IsAdmin())
async def forward_message_to_channel(message: types.Message, bot: Bot):
    text = ("Добрый день!\n"
            "<b>Завтра уже старт обучения</b>🔥\n"
            "*<i>следующий поток будет только осенью</i>\n\n"
            "Успевайте присоединиться, завтра последний день продаж❤️"
            )
    users = await get_all_users()
    i = 0
    for user in users:
        try:
            await bot.send_message(chat_id=user.user_id, text=text, reply_markup=send_all(), parse_mode='HTML')
            logging.debug(f'Отправлено сообщение пользователю {user.user_id}')
        except Exception as ex:
            logging.warning(f'Сообщение не отправлено! - {ex}')
        i += 1
        await asyncio.sleep(0.05)
    await message.answer(f"Сообщение было переслано {i} человек.")
