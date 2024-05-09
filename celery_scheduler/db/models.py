import sqlalchemy as sa
from sqlalchemy import ForeignKey, text, BigInteger, String, JSON, Text, TIMESTAMP, Boolean
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from typing import Annotated, Any

from datetime import datetime

int_pk = Annotated[int, mapped_column(BigInteger, sa.Identity(), primary_key=True)]
created_at = Annotated[datetime, mapped_column(server_default=text("TIMEZONE('Asia/Yekaterinburg', now())"))]
updated_at = Annotated[datetime, mapped_column(server_default=text("TIMEZONE('Asia/Yekaterinburg', now())"), onupdate=datetime.utcnow())]


class Base(DeclarativeBase):
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]


class User(Base):
    __tablename__ = 'users'

    user_id: Mapped[int_pk]
    username: Mapped[str] = mapped_column(String, nullable=True)
    first_name: Mapped[str | None] = mapped_column(String, nullable=True)
    last_name: Mapped[str | None] = mapped_column(String, nullable=True)
    phone_number: Mapped[str | None] = mapped_column(String, nullable=True)
    payment_date = Annotated[datetime, mapped_column(server_default=text("TIMEZONE('Asia/Yekaterinburg', now())"))]
    language_code: Mapped[str | None] = mapped_column(String, nullable=True)
    is_admin: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    # Связь с таблицей "Курсы"
    grafana_logs: Mapped[list["GrafanaLogs"]] = relationship(back_populates='creator', lazy='selectin')


class GrafanaLogs(Base):
    __tablename__ = 'grafana_logs'

    id: Mapped[int_pk]
    log_type: Mapped[str] = mapped_column(String, nullable=True)
    before_handler: Mapped[str] = mapped_column(String, nullable=True)
    handler: Mapped[str] = mapped_column(String, nullable=True)
    selected_course: Mapped[str] = mapped_column(String, nullable=True)
    handler_type: Mapped[str] = mapped_column(String, nullable=True)
    message_text: Mapped[str] = mapped_column(String, nullable=True)
    fsm_data: Mapped[Any] = mapped_column(JSON, nullable=True)
    exception: Mapped[str] = mapped_column(Text, nullable=True)
    traceback: Mapped[str] = mapped_column(Text, nullable=True)

    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.user_id'))
    creator: Mapped["User"] = relationship(back_populates='grafana_logs', lazy='selectin')


class Payments(Base):
    __tablename__ = 'payments'

    id: Mapped[int_pk]
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.user_id'))
    event: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String)
    payment_id: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String, nullable=True)
    amount: Mapped[str] = mapped_column(String, nullable=True)
    income_amount: Mapped[str] = mapped_column(String, nullable=True)
    reason: Mapped[str] = mapped_column(Text, nullable=True)
    response: Mapped[Any] = mapped_column(JSON, nullable=True)