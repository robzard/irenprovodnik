from aiogram.types import InlineKeyboardMarkup, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config_data.config import load_config

config = load_config()


def command_start(user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🎓 Курсы", web_app=WebAppInfo(url=f'https://{config.tg_bot.domen_web_app}.ru/teyla_courses?user_id={user_id}'))
    builder.button(text="✉️ Контакты", callback_data='contacts')
    builder.button(text="❓ Часто задаваемые вопросы", callback_data='questions')
    builder.button(text="💬 Написать менеджеру", url='https://t.me/Teylaschool')  # callback_data='support'
    # builder.button(text="Статистика", web_app=WebAppInfo(url='https://teylaschoolcourse.ru/grafana/public-dashboards/196b77dca7b64b75b6dc4e3edfadb8a9'))
    builder.adjust(2, 1, 1)
    return builder.as_markup()


def web_query_course(course_name_id: str, user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Программа курса", web_app=WebAppInfo(url=f'https://{config.tg_bot.domen_web_app}.ru/course_program?course_name_id={course_name_id}&user_id={user_id}'))
    builder.button(text="Купить курс", callback_data='buy_course')
    builder.button(text="Информация о курсе", web_app=WebAppInfo(url=f'https://{config.tg_bot.domen_web_app}.ru/course_info?course_name_id={course_name_id}&user_id={user_id}'))
    builder.button(text="Оплата и стоимость", web_app=WebAppInfo(url=f'https://{config.tg_bot.domen_web_app}.ru/payment_and_cost?course_name_id={course_name_id}&user_id={user_id}'))
    # builder.button(text="Написать менеджеру", callback_data='support')
    builder.button(text="Написать менеджеру", url='https://t.me/Teylaschool')
    builder.button(text="☰ Меню", callback_data='start')
    builder.adjust(2, 1, 1, 1, 1)
    return builder.as_markup()


def menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="☰ Меню", callback_data='start')
    builder.adjust(1)
    return builder.as_markup()


def support_quit() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Спасибо!", callback_data='support_quit')
    builder.button(text="Ответ не помог", callback_data='support_quit')
    return builder.as_markup()


def questions() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Когда старт курса?", callback_data='answer_questions')
    builder.button(text="Сколько стоит курс?", callback_data='answer_questions')
    builder.button(text="Как забронировать место?", callback_data='answer_questions')
    builder.button(text="Какие способы оплаты?", callback_data='answer_questions')
    builder.button(text="Назад", callback_data='start')
    builder.adjust(2, 1, 1, 1)
    return builder.as_markup()


def buy_course(course_name_id: str) -> InlineKeyboardMarkup:
    url_path = {'course_style_for_me': 'myself',
                'course_profession_style': 'stylist_kurator'}
    builder = InlineKeyboardBuilder()
    builder.button(text="Забронировать место", url=f'https://teylaschool.getcourse.ru/{url_path[course_name_id]}')
    builder.button(text="Оплатить всю сумму", url=f'https://teylaschool.getcourse.ru/{url_path[course_name_id]}')
    builder.button(text="Оформить рассрочку", url='https://www.teylaschool.ru/rassrochka')
    builder.button(text="☰ Меню", callback_data='start')
    builder.button(text="Назад", callback_data='back_to_course')
    builder.adjust(1, 1, 1, 2)
    return builder.as_markup()


def buy_course_registration() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Запись на курс", url='https://forms.gle/aofX3bgae5fjv7rA7')
    builder.button(text="☰ Меню", callback_data='start')
    builder.button(text="Назад", callback_data='back_to_course')
    builder.adjust(1, 2)
    return builder.as_markup()


def contacts() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Telegram канал школы", url='https://t.me/teylaschool_online')
    builder.button(text="Сайт школы", url='https://www.teylaschool.ru')
    builder.button(text="Менеджер", url='https://t.me/Teylaschool')
    builder.button(text="Назад", callback_data='start')
    builder.adjust(1, 2)
    return builder.as_markup()


def questions_back() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Назад", callback_data='start')
    return builder.as_markup()


def questions_back_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Выбрать другую категорию", callback_data='chose_another_category')
    builder.button(text="☰ Меню", callback_data='questions_back_menu')
    builder.adjust(1)
    return builder.as_markup()


def channel_move_to_chatbot() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Перейти в чат бот", url='https://t.me/teylaschool_bot')
    builder.adjust(1)
    return builder.as_markup()


def send_all() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🎓 Посмотреть курсы", callback_data='start_new')
    builder.adjust(1)
    return builder.as_markup()

