from aiogram.types import WebAppInfo, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from config_data.config import load_config

config = load_config()

def fill_form() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(
        text="Заполнить форму", web_app=WebAppInfo(url=f'https://{config.tg_bot.domen_web_app}.ru/teyla_courses'))
    )

    return builder.as_markup(resize_keyboard=True)


def create_keyboard(buttons_questions):
    builder = ReplyKeyboardBuilder()
    for button_text in buttons_questions.keys():
        builder.row(KeyboardButton(text=button_text))
    builder.adjust(1,1,1,2)
    return builder.as_markup(resize_keyboard=True)
