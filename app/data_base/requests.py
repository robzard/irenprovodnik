import json
import os
from datetime import datetime
from typing import Tuple, Optional

from aiogram.types import Update
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from sqlalchemy import create_engine, update

from sqlalchemy_utils import database_exists, create_database

# from states.states import FsmData
from .models import User, GrafanaLogs, Base, Payments

db_url = f"postgresql+psycopg://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DATABASE')}?options=-c%20timezone%3DAsia/Yekaterinburg"
engine: AsyncEngine = create_async_engine(db_url)
engine_sync = create_engine(db_url, connect_args={"options": "-c timezone=Asia/Yekaterinburg"})
AsyncSession: sessionmaker[AsyncSession] = sessionmaker(
    bind=engine, expire_on_commit=False, class_=AsyncSession
)


async def get_user_data(user_id):
    async with AsyncSession() as session:
        query = select(User).where(User.user_id == user_id)
        result = await session.execute(query)
        user = result.scalar()
        return user


async def get_all_users():
    async with AsyncSession() as session:
        query = select(User)
        result = await session.execute(query)
        users = result.scalars().all()
        return users


async def get_admins():
    try:
        async with AsyncSession() as session:
            query = select(User).where(User.is_admin == True)
            result = await session.execute(query)
            users = result.scalars().all()
            return [admin.user_id for admin in users]
    except Exception as ex:
        return []


# async def log_grafana_after(event: Update, fsm_data: FsmData, before_handler_name: str | None, log_type: str, exception: str = None, traceback: str = None):
#     async with AsyncSession() as session:
#         handler_type = await _determine_handler_type(event)
#         user_id, message_text = _extract_event_data(event)
#
#         data_fsm_json: str = json.dumps(fsm_data.__str__(), ensure_ascii=False)
#         handler_name = fsm_data.handler_name
#         selected_course = fsm_data.selected_course
#
#         # Создаем и сохраняем лог
#         log_entry = GrafanaLogs(
#             log_type=log_type,
#             user_id=user_id,
#             before_handler=before_handler_name,
#             handler=handler_name,
#             selected_course=selected_course,
#             handler_type=handler_type,
#             message_text=message_text,
#             fsm_data=data_fsm_json,
#             exception=exception,
#             traceback=traceback
#         )
#         session.add(log_entry)
#         await session.commit()
#
#         await update_user_time(user_id)


async def update_user_time(user_id):
    async with AsyncSession() as session:
        result = await session.execute(select(User).filter(User.user_id == user_id))
        user = result.scalars().first()
        if user:
            # Асинхронно обновляем время в поле updated_at
            await session.execute(
                update(User).
                where(User.user_id == user_id).
                values(updated_at=datetime.utcnow())
            )
            await session.commit()


async def _determine_handler_type(event: Update) -> str:
    if event.message:
        return 'message'
    elif event.callback_query:
        return 'callback_query'
    # Добавьте дополнительные проверки по мере необходимости
    return 'unknown'


def _extract_event_data(event: Update) -> Tuple[Optional[int], Optional[str]]:
    user_id = None
    message_text = None
    if event.message:
        user_id = event.message.from_user.id
        message_text = event.message.text
    elif event.callback_query:
        user_id = event.callback_query.from_user.id
        message_text = event.callback_query.data
    # Добавьте дополнительные проверки по мере необходимости
    return user_id, message_text


async def save_payment(yookassa_response: dict):
    user_id = yookassa_response.get('object').get('metadata').get('telegram_user_id')
    event, status = yookassa_response.get('event').split('.')
    payment_id = yookassa_response.get('object').get('payment_method').get('id')
    reason = yookassa_response.get('object', {}).get('cancellation_details', {}).get('reason')
    response = yookassa_response.__str__()
    async with AsyncSession() as session:
        payment = Payments(user_id=user_id, event=event, status=status, payment_id=payment_id, reason=reason, response=response)
        session.add(payment)
        await session.commit()
