from datetime import timedelta
from functools import wraps
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, make_response
import logging
from aiogram.utils.web_app import check_webapp_signature
import json
import requests
import os

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from utils.telegram_bot import send_telegram_message_succeeded, unban_chat_member
from common.db.requests import save_payment, update_payment_date

db_url = f"postgresql+psycopg://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DATABASE')}?options=-c%20timezone%3DAsia/Yekaterinburg"
engine: AsyncEngine = create_async_engine(db_url)
engine_sync = create_engine(db_url, connect_args={"options": "-c timezone=Asia/Yekaterinburg"})
AsyncSession: sessionmaker[AsyncSession] = sessionmaker(
    bind=engine, expire_on_commit=False, class_=AsyncSession
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)

BOT_TOKEN = os.getenv("BOT_TOKEN")

app.secret_key = os.getenv("SECRET_KEY")


class IgnoreSocketIOLogs(logging.Filter):
    def filter(self, record):
        return 'socket.io' not in record.getMessage()


logging.getLogger('werkzeug').addFilter(IgnoreSocketIOLogs())

courses_data = {'course_style_for_me': {'cost': '39 000', 'name': 'Стиль для себя', 'monthly_payment': '3 900', 'url_buy_path': 'myself'},
                'course_profession_style': {'cost': '69 000', 'name': 'Профессия-стилист', 'monthly_payment': '6 900', 'url_buy_path': 'stylist_kurator'}}


def login_required(f):
    @wraps(f)
    async def decorated_function(*args, **kwargs):
        logger.info('---login_required---')
        logger.info(f'---login_required--- auth - {session.get("auth")}')
        if session.get('auth') is not True:
            session['request_path'] = request.path
            logger.info(f'---login_required--- request_path - {session.get("request_path")}')
            return render_template('validate_user.html')
        return await f(*args, **kwargs)

    return decorated_function


@app.route('/validate_user', methods=['POST'])
async def validate_user():
    # Получаем данные, отправленные с клиента
    logger.info(f"--validate_user-- session.auth = {session.get('auth', 'Отсутствует')}")
    received_data = json.loads(request.data)
    logger.info(f'--validate_user-- received_data - {received_data}')

    # Проверяем подпись
    try:
        if check_webapp_signature(BOT_TOKEN, received_data):
            session['auth'] = True
            session.modified = True
            original_url = session.pop('original_url', '/')
            logger.info(f'Подпись верна, {original_url}')
            logger.info(f"--validate_user-- session.auth = {session['auth']}")
            # return render_template('data_free_course.html')
            return jsonify({'success': True, 'redirect': session['request_path']})
        else:
            logger.info('Подпись не верна')
            session['auth'] = False
            session.modified = True
            return jsonify({'success': False, 'error': 'Invalid signature'}), 403
    except Exception as e:
        logger.info(f'Ошибка - {str(e)}')
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/send-data', methods=['POST'])
def send_data():
    data = request.json
    web_app_query_id = data['web_app_query_id']
    logger.info(f'web_app_query_id - {web_app_query_id}')
    answer_data = data['data']
    logger.info(f'data - {answer_data}')

    # Замените "YOUR_BOT_TOKEN" на токен вашего бота
    url = "https://api.telegram.org/bot" + BOT_TOKEN + "/answerWebAppQuery"
    payload = {
        "web_app_query_id": web_app_query_id,
        "result": {
            "type": "article",
            "id": "unique_id",
            "title": "Title",
            "input_message_content": {
                "message_text": answer_data
            }
        }
    }
    response = requests.post(url, json=payload)
    logger.info(f'response - {response.status_code}')
    logger.info(f'response_text - {response.text}')
    return response.json()


@app.route('/teyla_courses')  # Выбор курса (static)
async def teyla_courses():
    user_id = request.args.get('user_id')
    await add_log_grafana(user_id, 'Страница Курсов')
    print(os.getenv("DOMEN_WEB_APP"))
    return render_template('teyla_courses.html',
                           domen_web_app=os.getenv("DOMEN_WEB_APP"))


@app.route('/course_program')  # Программа курса (static)
async def course_program():
    user_id = request.args.get('user_id')
    course_name_id = request.args.get('course_name_id')
    await add_log_grafana(user_id, 'Страница Программа курса', courses_data[course_name_id]['name'])
    return render_template(f'program_{course_name_id}.html')


@app.route('/course_info')  # Информация о курсе (static)
async def course_info():
    user_id = request.args.get('user_id')
    course_name_id = request.args.get('course_name_id')
    await add_log_grafana(user_id, 'Страница Информация курса', courses_data[course_name_id]['name'])
    return render_template(f'info_{course_name_id}.html')


@app.route('/payment_and_cost')  # Оплата и стоимость (dynamic)
async def payment_and_cost():
    user_id = request.args.get('user_id')
    course_name_id = request.args.get('course_name_id')
    await add_log_grafana(user_id, 'Страница Оплата и стоимость', courses_data[course_name_id]['name'])
    return render_template('payment_and_cost.html',
                           course_name_id=course_name_id,
                           course_cost=courses_data[course_name_id]['cost'],
                           course_name=courses_data[course_name_id]['name'],
                           monthly_payment=courses_data[course_name_id]['monthly_payment'],
                           url_path=courses_data[course_name_id]['url_buy_path'],
                           domen_web_app=os.getenv("DOMEN_WEB_APP"))


@app.route('/yookassa_notification', methods=['POST'])
async def yookassa_notification():
    data = request.json
    logger.info(f'yookassa_notification - {str(data)}')
    payment = await save_payment(data)
    if payment.status == "succeeded":
        await update_payment_date(payment)
        await unban_chat_member(payment.user_id)
        await send_telegram_message_succeeded(payment)

    response = make_response(jsonify({'status': 'success'}))
    response.status_code = 200
    return response


async def add_log_grafana(user_id: int, handler_name: str, selected_course: str = None):
    pass
    # async with AsyncSession() as session:
    #     db = GrafanaManager(session)
    #     await db.log_grafana_after(user_id, handler_name, selected_course)


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
