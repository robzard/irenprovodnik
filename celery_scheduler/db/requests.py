import json
import os
from datetime import datetime
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

async def get_latest_successful_payments():
    async with AsyncSession() as session:
        # Подзапрос для выбора максимальной даты created_at для каждого user_id
        subquery = (
            select(
                Payments.user_id,
                func.max(Payments.created_at).label('max_created_at')
            ).where(
                and_(
                    Payments.event == 'payment',
                    Payments.status == 'succeeded'
                )
            ).group_by(Payments.user_id)
        ).subquery()

        # Основной запрос, который присоединяет результаты подзапроса и фильтрует записи по максимальной дате
        # и проверяет, что максимальная дата меньше текущей даты на месяц
        query = (
            select(Payments)
            .join(subquery, and_(
                Payments.user_id == subquery.c.user_id,
                Payments.created_at == subquery.c.max_created_at
            ))
            .where(
                Payments.created_at + text("interval '1 month'") < func.now()
            )
        )

        result = await session.execute(query)
        payments = result.scalars().all()
        return payments
