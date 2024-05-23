import json
import logging
import os
from datetime import datetime, timedelta
from typing import Tuple, Optional

from aiogram.types import Update
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from sqlalchemy import create_engine, update, desc

from sqlalchemy_utils import database_exists, create_database

# from config_data.config import load_config
# from states.states import FsmData
from .models import User, GrafanaLogs, Base, Payments

# config = load_config()

db_url = f"postgresql+psycopg://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DATABASE')}?options=-c%20timezone%3DAsia/Yekaterinburg"
engine: AsyncEngine = create_async_engine(db_url)
engine_sync = create_engine(db_url, connect_args={"options": "-c timezone=Asia/Yekaterinburg"})
AsyncSession: sessionmaker[AsyncSession] = sessionmaker(
    bind=engine, expire_on_commit=False, class_=AsyncSession
)


def create_database_and_tables(engine):
    # Создание базы данных, если она не существует
    sync_engine = engine
    if not database_exists(sync_engine.url):
        create_database(sync_engine.url)

    # Создание таблиц, если они не существуют
    with engine.begin() as conn:
        # Base.metadata.drop_all(conn)
        Base.metadata.create_all(conn)


async def get_user_data(user_id):
    async with AsyncSession() as session:
        query = select(User).where(User.user_id == user_id)
        result = await session.execute(query)
        user = result.scalar()
        return user


async def create_user(user_data):
    async with AsyncSession() as session:
        new_user = User(**user_data)
        session.add(new_user)
        await session.commit()


async def create_grafana_logs(grafana_log_data):
    async with AsyncSession() as session:
        grafana_log = GrafanaLogs(**grafana_log_data)
        session.add(grafana_log)
        await session.commit()


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
    description = yookassa_response.get('object', {}).get('description')
    amount = yookassa_response.get('object', {}).get('amount', {}).get('value')
    income_amount = yookassa_response.get('object', {}).get('income_amount', {}).get('value')
    reason = yookassa_response.get('object', {}).get('cancellation_details', {}).get('reason')
    response = yookassa_response.__str__()
    async with AsyncSession() as session:
        payment = Payments(user_id=user_id, event=event, status=status, payment_id=payment_id, description=description, amount=amount, income_amount=income_amount, reason=reason, response=response)
        session.add(payment)
        await session.commit()
    return payment


async def update_payment_date(payment: Payments, subscription=True):
    async with AsyncSession() as session:
        result = await session.execute(select(User).filter(User.user_id == int(payment.user_id)))
        user = result.scalars().first()
        if user:
            # Асинхронно обновляем время в поле updated_at
            await session.execute(
                update(User).
                where(User.user_id == int(payment.user_id)).
                values(payment_date=payment.created_at, subscription=subscription)
            )
            await session.commit()


async def get_users_subscription_expired():
    async with AsyncSession() as session:
        one_month_ago = datetime.utcnow() - timedelta(days=30)
        result = await session.execute(
            select(User).
            where(
                User.subscription.is_(True),
                User.payment_date < one_month_ago
            )
        )
        users = result.scalars().all()
        return users


async def set_subscription_false(user: User):
    async with AsyncSession() as session:
        await session.execute(
            update(User).
            where(User.user_id == int(user.user_id)).
            values(subscription=False)
        )
        await session.commit()


async def set_subscription_true(user: User):
    async with AsyncSession() as session:
        await session.execute(
            update(User).
            where(User.user_id == int(user.user_id)).
            values(subscription=True)
        )
        await session.commit()


async def get_last_payment_id(user_id: int):
    async with AsyncSession() as session:
        result = await session.execute(
            select(Payments.payment_id).filter(Payments.user_id == user_id).order_by(desc(Payments.created_at)).limit(1)
        )
        last_payment = result.scalars().first()
        return last_payment


async def set_user_auto_payment(user: User, auto_payment: bool):
    async with AsyncSession() as session:
        await session.execute(
            update(User).
            where(User.user_id == int(user.user_id)).
            values(auto_payment=auto_payment)
        )
        await session.commit()


class BaseManager:

    def __init__(self, session=None):
        self.session = session

    async def close_session(self):
        if self.session:
            await self.session.close()

    async def execute_query(self, query):
        return await self.session.execute(query)

    async def add(self, obj):
        self.session.add(obj)
        await self.session.commit()

    @staticmethod
    def get_async_session() -> sessionmaker[AsyncSession]:
        return AsyncSession

    @staticmethod
    def create_database_and_tables(engine):
        # Создание базы данных, если она не существует
        sync_engine = engine
        if not database_exists(sync_engine.url):
            create_database(sync_engine.url)

        # Создание таблиц, если они не существуют
        with engine.begin() as conn:
            Base.metadata.drop_all(conn)
            logging.debug(f'Создание таблиц')
            Base.metadata.create_all(conn)
