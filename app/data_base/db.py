import os
from typing import Tuple, Optional, Dict, Any

from aiogram.types import Update

from sqlalchemy_utils import database_exists, create_database

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from .models import User, GrafanaLogs, Base

# Базовый класс для менеджеров




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
    def create_database_and_tables(engine):
        # Создание базы данных, если она не существует
        sync_engine = engine
        if not database_exists(sync_engine.url):
            create_database(sync_engine.url)

        # Создание таблиц, если они не существуют
        with engine.begin() as conn:
            Base.metadata.drop_all(conn)
            Base.metadata.create_all(conn)


class GrafanaManager(BaseManager):
    def __init__(self, async_session_maker: sessionmaker[AsyncSession]):
        super().__init__(async_session_maker)

    async def log_grafana_after(self, user_id: int, handler_name: str, selected_course: str=None):
        # Создаем и сохраняем лог
        log_entry = GrafanaLogs(
            user_id=user_id,
            before_handler=None,
            handler=handler_name,
            selected_course=selected_course,
            handler_type='web-site',
            message_text=None
        )
        await self.add(log_entry)
