from dataclasses import dataclass
import os


@dataclass
class DatabaseConfig:
    database: str
    db_host: str
    db_user: str
    db_password: str


@dataclass
class WebHook:
    path: str
    url: str
    webapp_host: str
    webapp_port: int
    secret: str


@dataclass
class TgBot:
    token: str
    gigachat_token: str
    webhook: WebHook
    domen_web_app: str


@dataclass
class Redis:
    host: str
    port: int
    db: int


@dataclass
class Yookassa:
    shop_id: str
    secret_key: str


@dataclass
class Config:
    tg_bot: TgBot
    db: DatabaseConfig
    redis: Redis
    yookassa: Yookassa


def load_config() -> Config:
    return Config(
        tg_bot=TgBot(
            token=os.getenv('BOT_TOKEN'),
            gigachat_token=os.getenv('GIGACHAT_TOKEN'),
            webhook=WebHook(
                path=os.getenv('WEBHOOK_PATH'),
                url=os.getenv('WEBHOOK_URL'),
                secret=os.getenv('WEBHOOK_SECRET'),
                webapp_host=os.getenv('WEBAPP_HOST'),
                webapp_port=int(os.getenv('WEBAPP_PORT'))
            ),
            domen_web_app=os.getenv('DOMEN_WEB_APP'),
        ),
        db=DatabaseConfig(
            database=os.getenv('DATABASE'),
            db_host=os.getenv('DB_HOST'),
            db_user=os.getenv('DB_USER'),
            db_password=os.getenv('DB_PASSWORD')
        ),
        redis=Redis(
            host=os.getenv('REDIS_HOST'),
            port=int(os.getenv('REDIS_PORT')),
            db=int(os.getenv('REDIS_DB'))
        ),
        yookassa=Yookassa(
            shop_id=os.getenv('YOOKASSA_SHOP_ID'),
            secret_key=os.getenv('YOOKASSA_SECRET_KEY')
        )
    )
