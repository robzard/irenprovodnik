import logging
import traceback
from datetime import datetime

from aiogram import Router
from aiogram.filters import ExceptionTypeFilter
from aiogram.types import ErrorEvent

from common.db.requests import get_admins  # ,log_grafana_after
from states.states import FsmData
from utils.utils import extract_event_data

router = Router(name=__name__)


@router.error(ExceptionTypeFilter(Exception))
async def handle_my_custom_exception(event: ErrorEvent, fsm_data: FsmData):
    exception = event.exception
    traceback_format_exc = traceback.format_exc()
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    before_handler_name = fsm_data.before_handler_name
    error_msg = f"Time: {time}\nException: {exception}\nTraceback: {traceback_format_exc}"
    logging.error(error_msg)

    update_obj = extract_event_data(event.update)

    user_data = None
    if update_obj:
        user = update_obj.from_user
        user_data = f"User ID: {user.id}, Username: {user.username}"
        error_msg += f"\n{user_data}\nFSM Data: {fsm_data}"

    admins = await get_admins()

    # await log_grafana_after(event.update, fsm_data, before_handler_name, 'ERROR', exception=str(exception), traceback=traceback_format_exc)
    for admin in admins:
        await event.update.bot.send_message(chat_id=admin, text=f"🔴 ERROR\nTime: {time}\n{user_data}\nException: {exception}\nTraceback: \n{traceback_format_exc[-500:]}")


# Глобальный обработчик ошибок
@router.error()
async def error_handler(event: ErrorEvent, fsm_data: FsmData):
    exception = event.exception
    traceback_format_exc = traceback.format_exc()
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    before_handler_name = fsm_data.before_handler_name
    error_msg = f"Time: {time}\nException: {exception}\nTraceback: {traceback_format_exc}"
    logging.critical(error_msg, exc_info=True)

    update_obj = extract_event_data(event.update)

    user_data = None
    if update_obj:
        user = update_obj.from_user
        user_data = f"User ID: {user.id}, Username: {user.username}"
        error_msg += f"\n{user_data}\nFSM Data: {fsm_data}"

    admins = await get_admins()

    # await log_grafana_after(event.update, fsm_data, before_handler_name, 'CRITICAL', exception=str(exception), traceback=traceback_format_exc)
    for admin in admins:
        await event.update.bot.send_message(chat_id=admin, text=f"🔴 ERROR\nTime: {time}\n{user_data}\nException: {exception}\nTraceback: \n{traceback_format_exc[-500:]}")
