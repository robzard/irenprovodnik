import logging
import re

from aiogram import types
from aiogram.filters import Filter

from db.models import User
from db.requests import get_admins
from utils.dict_buttons import buttons_questions

course_names = {'Стиль для себя': 'course_style_for_me',
                'Профессия-стилист': 'course_profession_style'}


class CourseNameFilter(Filter):
    async def __call__(self, message: types.Message) -> bool | dict:
        if message.text in course_names.keys():
            return {'course_names': course_names}
        return False


class CourseBuyFilter(Filter):
    async def __call__(self, message: types.Message) -> bool | dict:
        buy_course_label = 'купить курс - '
        course_name = message.text.replace(buy_course_label, '')
        if course_name in course_names.keys():
            return {'course_names': course_names, 'course_name': course_name}
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
