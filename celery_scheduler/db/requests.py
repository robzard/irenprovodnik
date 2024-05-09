import json
import os
from datetime import datetime, timedelta
from typing import Tuple, Optional

from aiogram.types import Update
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from sqlalchemy import create_engine, update, and_, func
from sqlalchemy.sql.expression import text

from sqlalchemy_utils import database_exists, create_database

# from states.states import FsmData
from .models import User, GrafanaLogs, Base, Payments

# db_url = f"postgresql+psycopg://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DATABASE')}?options=-c%20timezone%3DAsia/Yekaterinburg"
# engine = create_engine(db_url, connect_args={"options": "-c timezone=Asia/Yekaterinburg"})
#
# # Создание сессии
# SessionLocal = sessionmaker(bind=engine)

db_url = f"postgresql+psycopg://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DATABASE')}?options=-c%20timezone%3DAsia/Yekaterinburg"
engine: AsyncEngine = create_async_engine(db_url)
engine_sync = create_engine(db_url, connect_args={"options": "-c timezone=Asia/Yekaterinburg"})
AsyncSession: sessionmaker[AsyncSession] = sessionmaker(
    bind=engine, expire_on_commit=False, class_=AsyncSession
)


# def get_subscriptions_expired():
#     with SessionLocal() as session:
#         query = select(Payments).where(
#             and_(
#                 Payments.event == 'payment',
#                 Payments.status == 'succeeded',
#                 Payments.created_at > func.now()
#             )
#         )
#         result = session.execute(query)
#         payments = result.scalars().all()
#         return payments

async def get_users_subscription_expired():
    async with AsyncSession() as session:
        one_month_ago = datetime.utcnow() - timedelta(days=30)
        # Формируем запрос на выборку пользователей
        result = await session.execute(
            select(User).
            where(
                User.subscription.is_(True),  # Проверяем, что подписка активна
                User.payment_date < one_month_ago  # и что последний платёж был более месяца назад
            )
        )
        # Получаем список пользователей
        users = result.scalars().all()
        return users
