import logging
import re

from aiogram import types
from aiogram.filters import Filter

from common.db.models import User
from common.db.requests import get_admins
from utils.dict_buttons import buttons_questions

course_names = {'Стиль для себя': 'course_style_for_me',
                'Профессия-стилист': 'course_profession_style'}


class MarafonBuyFilter(Filter):
    async def __call__(self, message: types.Message) -> bool | dict:
        buy_course_label = 'Оплата марфона'
        if message.text == buy_course_label:
            return True
        return False


class ReplyButtonsQuestions(Filter):
    async def __call__(self, message: types.Message) -> bool | dict:
        all_keys: list = []
        for k in buttons_questions.keys():
            all_keys.append(k)
            children = buttons_questions[k].get('children', None)
            if children:
                for k_children in children.keys():
                    all_keys.append(k_children)
        return message.text in all_keys


class IsAdmin(Filter):
    async def __call__(self, message: types.Message) -> bool:
        admins = await get_admins()
        if message.chat.id in admins:
            logging.debug(f'Пользователь {message.chat.id} является админом')
            return True
        return False
