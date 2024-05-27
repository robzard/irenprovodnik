import asyncio
from typing import Callable, Dict, Any
from aiogram import BaseMiddleware, Bot, types
from aiogram.fsm.context import FSMContext
from aiogram.types import Update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from common.db.models import User
from common.db.requests import get_user_data, create_user
from utils.utils import MessageEditor, get_event_text

import logging


class DatabaseSessionMiddleware(BaseMiddleware):

    def __init__(self, bot: Bot, async_session_maker: sessionmaker[AsyncSession]):
        self.AsyncSession: sessionmaker[AsyncSession] = async_session_maker
        self.bot = bot

    async def __call__(self, handler: Callable[[Update, Dict[str, Any]], Any], event: Update,
                       data: Dict[str, Any]) -> Any:
        logging.debug(f'Старт обработки - {get_event_text(event)} ({event.event_type})')
        state: FSMContext = data.get('state')
        # await fsm_data.update_params_from_state()

        # before_handler_name = await self.get_before_handler(data, fsm_data)

        await self.registration_user(event)

        await handler(event, data)

        # await fsm_data.update_data()

        # await self.log_grafana(event, fsm_data, before_handler_name)

        logging.debug(f'Конец обработки - {get_event_text(event)} ({event.event_type})')

    async def registration_user(self, event: Update):
        user_id = event.event.from_user.id
        user: User = await get_user_data(user_id)
        if not user:
            user_data = {
                'user_id': user_id,
                'username': event.event.from_user.username,
                'first_name': event.event.from_user.first_name,
                'last_name': event.event.from_user.last_name,
                'language_code': event.event.from_user.language_code
            }
            await create_user(user_data)

    @staticmethod
    async def log_grafana(event: Update, state: FSMContext, before_handler_name: str):
        pass
        # await log_grafana_after(event, fsm_data, before_handler_name, 'INFO')

    @staticmethod
    async def get_before_handler(data: Dict[str, Any], state: FSMContext) -> str:
        data_fsm: dict = await data.get('state').get_data()
        before_handler_name = data_fsm.get('handler_name', '')
        await state.update_data(before_handler_name=before_handler_name)
        return before_handler_name


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()
        # TODO self.user_status может засорять память, вообще не факт (т.к. хранится немного данных), но нужно учесть
        self.user_status = {}  # Словарь для хранения статуса пользователя

    async def __call__(self, handler, event, data):
        user_id = self.get_user_id(event)

        if self.user_status.get(user_id, False):
            # Если пользователь уже в обработке, удаляем сообщение, отправленное с помощью кнопки Reply
            if isinstance(event, types.Message) and event.text:
                await event.bot.delete_message(chat_id=event.chat.id, message_id=event.message_id)
            return

        self.user_status[user_id] = True

        try:
            await handler(event, data)
        finally:
            self.user_status[user_id] = False

    @staticmethod
    def get_user_id(event: types.Update) -> int:
        """Извлекает идентификатор пользователя из различных типов событий."""
        if isinstance(event, types.Message):
            return event.from_user.id
        elif isinstance(event, types.CallbackQuery):
            return event.from_user.id
        return None


class CallbackThrottlingMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        if not isinstance(event, types.CallbackQuery):
            await handler(event, data)
            return

        fsm_context: FSMContext = data.get("state")
        state_data = await fsm_context.get_data()
        wait_callback = state_data.get('wait_callback', False)

        if wait_callback:
            await event.answer("Пожалуйста, подождите")
            return

        await fsm_context.update_data(wait_callback=True)
        try:
            await handler(event, data)
        finally:
            await asyncio.sleep(0.2)
            await fsm_context.update_data(wait_callback=False)

# TODO
# # Тут надо дорабатывать, хз в чём проблема, но близко к успеху
# class RateLimitMiddleware(BaseMiddleware):
#     def __init__(self, rate_limit=5):
#         super().__init__()
#         self.rate_limit = rate_limit
#         self.users_last_action = {}
#         self.info_messages = {}  # Словарь для хранения информационных сообщений по пользователям
#
#     async def __call__(self, handler, event, data):
#         user_id = self.get_user_id(event)
#
#         if user_id is None:
#             return await handler(event, data)
#
#         current_time = time.monotonic()
#         last_action_time = self.users_last_action.get(user_id, 0)
#
#         if current_time - last_action_time < self.rate_limit:
#             if isinstance(event, (types.CallbackQuery, types.Message)):
#                 # Проверяем, существует ли уже информационное сообщение для данного пользователя
#                 if user_id not in self.info_messages:
#                     info_message = await event.answer("Вы совершаете действия слишком часто. Пожалуйста, подождите.")
#                     self.info_messages[user_id] = info_message.message_id
#                     await asyncio.sleep(self.rate_limit)
#                     # Удаляем информационное сообщение, если оно еще существует
#                     try:
#                         await event.bot.delete_message(chat_id=user_id, message_id=self.info_messages[user_id])
#                     except Exception as e:
#                         print(f"Ошибка при удалении сообщения: {e}")
#                     finally:
#                         # Удаляем запись о сообщении из словаря
#                         del self.info_messages[user_id]
#                 return
#         else:
#             self.users_last_action[user_id] = current_time
#             return await handler(event, data)
#
#     def get_user_id(self, event):
#         """Возвращает идентификатор пользователя из различных типов обновлений."""
#         if isinstance(event, types.Message):
#             return event.from_user.id
#         elif isinstance(event, types.CallbackQuery):
#             return event.from_user.id
#         return None


# ОГРАНИЧЕНИЕ ЗАПРОСОВ ПО ВРЕМЕНИ
# class ThrottlingMiddleware(BaseMiddleware):
#     def __init__(self, limit=1):
#         super().__init__()
#         self.limit = limit  # Максимальное количество запросов...
#         self.users = {}  # Словарь для отслеживания запросов пользователей
#
#     async def __call__(self, handler, event, data):
#         user_id = self.get_user_id(event)
#
#         # Получаем время последнего запроса пользователя
#         last_request_time = self.users.get(user_id, 0)
#         current_time = time.time()
#
#         # Проверяем, превышен ли лимит
#         if current_time - last_request_time < self.limit:
#             # Если да, генерируем исключение или отправляем предупреждение
#             if isinstance(event, types.Message):
#                 await event.answer("Слишком много запросов, попробуйте позже.")
#             return
#
#         # Обновляем время последнего запроса
#         self.users[user_id] = current_time
#
#         # Вызываем следующий обработчик в цепочке
#         await handler(event, data)
#
#     def get_user_id(self, event: types.Update):
#         # Этот метод возвращает ID пользователя из различных типов обновлений
#         user_id = None
#         if isinstance(event, types.Message):
#             user_id = event.from_user.id
#         elif isinstance(event, types.CallbackQuery):
#             user_id = event.from_user.id
#         return user_id
