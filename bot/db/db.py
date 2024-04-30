import json
import logging
from datetime import datetime
from typing import Tuple, Optional, Dict, Any

from aiogram.fsm.context import FSMContext
from aiogram.types import Update
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from sqlalchemy import create_engine, update

from sqlalchemy_utils import database_exists, create_database

from config_data.config import load_config
from .models import User, GrafanaLogs, Base

config = load_config()

db_url = f"postgresql+psycopg://{config.db.db_user}:{config.db.db_password}@{config.db.db_host}/{config.db.database}?options=-c%20timezone%3DAsia/Yekaterinburg"
engine: AsyncEngine = create_async_engine(db_url)
engine_sync = create_engine(db_url, connect_args={"options": "-c timezone=Asia/Yekaterinburg"})
AsyncSession: sessionmaker[AsyncSession] = sessionmaker(
    bind=engine, expire_on_commit=False, class_=AsyncSession
)


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
            # Base.metadata.drop_all(conn)
            logging.debug(f'Создание таблиц')
            Base.metadata.create_all(conn)


class UserManager(BaseManager):
    def __init__(self, async_session_maker: sessionmaker[AsyncSession]):
        super().__init__(async_session_maker)
        self.user = None

    async def get_user_data(self, user_id):
        query = select(User).where(User.user_id == user_id)
        result = await self.execute_query(query)
        self.user = result.scalar()

    async def create_user(self, user_data):
        new_user = User(**user_data)
        await self.add(new_user)
        self.user = new_user

    async def create_grafana_logs(self, grafana_log_data):
        grafana_log = GrafanaLogs(**grafana_log_data)
        await self.add(grafana_log)

    async def get_all_users(self):
        query = select(User)
        result = await self.session.execute(query)
        users = result.scalars().all()
        return users

