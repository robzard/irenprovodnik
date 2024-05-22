import json
import logging

from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State


# from custom_logger.logger import logger


class FSMGpt(StatesGroup):
    wait_question = State()
    support_quit = State


class DefaultState(StatesGroup):
    default_state = State()
