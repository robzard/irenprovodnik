import json
import os
from datetime import datetime, timedelta
from typing import Tuple, Optional

from aiogram.types import Update
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from sqlalchemy import create_engine, update, and_, func, desc
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
