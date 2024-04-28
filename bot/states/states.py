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


class FsmData:
    def __init__(self, state: FSMContext, edit_message=None, category_message_id=None, msg_need_delete=None, msg_need_delete_on_start=None, before_handler_name=None, handler_name=None, selected_course=None, send_args=None, update_message_data=None,
                 wait_callback=None,
                 caption=None,
                 text=None,
                 reply_markup=None,
                 reply_markup_push=None,
                 course_name_id=None,
                 photo=None,
                 photo_path=None):
        self.state = state
        self.edit_message = edit_message
        self.category_message_id = category_message_id
        self.msg_need_delete = msg_need_delete or []
        self.msg_need_delete_on_start = msg_need_delete_on_start or []
        self.before_handler_name = before_handler_name
        self.handler_name = handler_name
        self.selected_course = selected_course
        self.send_args = send_args
        self.update_message_data = update_message_data
        self.wait_callback = wait_callback
        self.caption = caption
        self.text = text
        self.reply_markup = reply_markup
        self.reply_markup_push = reply_markup_push
        self.course_name_id = course_name_id
        self.photo = photo
        self.photo_path = photo_path

    def __str__(self):
        attributes = [f"{attr}={getattr(self, attr)}" for attr in vars(self) if attr != 'state']
        return f"FsmData({', '.join(attributes)})"

    def from_dict(self, **kwargs):
        self.__init__(self.state, **kwargs)

    async def get_state_data(self):
        return await self.state.get_data()

    async def update_params_from_state(self):
        state_data = await self.state.get_data()
        self.from_dict(**state_data)

    async def update_data(self, **kwargs):
        logging.debug(f'Обновление параметров fsm: {kwargs.__str__()}')
        kwargs = self.serialized_data(**kwargs)
        await self.state.update_data(**kwargs)
        await self.update_params_from_state()

    @staticmethod
    def serialized_data(**kwargs):
        photo = kwargs.get('send_args', {}).get('photo')
        reply_markup = kwargs.get('send_args', {}).get('reply_markup')
        if photo:
            kwargs['send_args']['photo'] = json.dumps(photo.__str__(), ensure_ascii=False) if photo else None
        if reply_markup:
            kwargs['send_args']['reply_markup'] = json.dumps(reply_markup.__str__(), ensure_ascii=False) if reply_markup else None
        if kwargs.get('reply_markup'):
            kwargs['reply_markup'] = json.dumps(kwargs.get('reply_markup').__str__(), ensure_ascii=False) if kwargs.get('reply_markup') else None
        return kwargs
