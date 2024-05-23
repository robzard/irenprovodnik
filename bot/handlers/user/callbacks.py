import json

from aiogram import Router, types, Bot

from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile

from keyboards.user import inline
from keyboards.user.inline import menu
from keyboards.user.reply import create_keyboard

from states.states import FSMGpt
from utils.dict_buttons import buttons_questions
from utils.utils import delete_need_messages, MessageEditor, delete_message_default

from keyboards.user.inline import command_start
from lexicon.lexicon import LEXICON

from filters.all_filters import course_names

from common.db.models import User
from common.yookassa_payment.yookassa_handler import YookassaHandler
import common.db.requests as db

router = Router(name=__name__)


# @router.callback_query(lambda c: c.data == 'start_new')
# async def handle_start_new_callback(callback_query: types.CallbackQuery, state: FSMContext, bot: Bot, state: FSMContext):
#     await callback_query.answer()
#     await delete_need_messages(bot, callback_query.message.chat.id, state)
#     if state.category_message_id:
#         state.msg_need_delete_on_start.append(state.category_message_id)
#     if state.edit_message:
#         state.msg_need_delete_on_start.append(state.edit_message)
#     await state.update_data(edit_message=None, msg_need_delete_on_start=state.msg_need_delete_on_start)
#     await on_start(callback_query.message, state, bot, message_editor, callback_query.from_user.id)

@router.callback_query(lambda c: c.data == 'start')
async def process_what_bot_can_do(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
    image_path = './static/images/iren.jpg'
    media = FSInputFile(image_path)
    await callback_query.message.answer_photo(photo=media, caption=LEXICON['user_command_start'], reply_markup=command_start(callback_query.message.from_user.id))


@router.callback_query(lambda c: c.data == 'support')
async def process_what_bot_can_do(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
    await callback_query.message.answer("Напишите свой вопрос и я вам помогу разобраться с вашей проблемой.")
    await state.set_state(FSMGpt.wait_question)
    # await state.set_data({'history': []})
    await state.update_data(handler_name='Написать менеджеру', history=[])


@router.callback_query(lambda c: c.data == 'support_quit')
async def process_what_bot_can_do(callback_query: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback_query.answer('Вы вышли из чата с ассистентом.')
    await callback_query.message.answer('Вы вышли из консультации с ассистентом. (Тут можно переводить на менеджера)', reply_markup=menu())


@router.callback_query(lambda c: c.data == 'questions')
async def process_what_bot_can_do(callback_query: types.CallbackQuery, state: FSMContext, bot: Bot):
    await callback_query.answer()
    await callback_query.message.answer(text='Выберите что вас интересует..', reply_markup=create_keyboard(buttons_questions, True))


@router.callback_query(lambda c: c.data == 'contacts')
async def process_what_bot_can_do(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.edit_reply_markup(reply_markup=inline.contacts())


@router.callback_query(lambda c: c.data == 'back_to_course')
async def process_what_bot_can_do(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    course_name_id = course_names.get(data.get('selected_course'))
    await callback_query.message.edit_reply_markup(reply_markup=inline.web_query_course(course_name_id, callback_query.from_user.id))


@router.callback_query(lambda c: c.data == 'buy_course')
async def process_what_bot_can_do(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.edit_reply_markup(reply_markup=inline.buy_course_registration())


@router.callback_query(lambda c: c.data == 'questions_back_menu')
async def process_what_bot_can_do(callback_query: types.CallbackQuery, state: FSMContext, bot: Bot):
    image_path = './static/images/iren.jpg'
    media = FSInputFile(image_path)
    await callback_query.message.answer_photo(photo=media, caption=LEXICON['user_command_start'], reply_markup=command_start(callback_query.from_user.id))


@router.callback_query(lambda c: c.data == 'contacts_back_menu')
async def process_what_bot_can_do(callback_query: types.CallbackQuery, state: FSMContext, bot: Bot):
    await callback_query.message.edit_reply_markup(reply_markup=command_start(callback_query.from_user.id))


@router.callback_query(lambda c: c.data == 'chose_another_category')
async def process_what_bot_can_do(callback_query: types.CallbackQuery, state: FSMContext, bot: Bot):
    await callback_query.answer()
    await bot.send_message(chat_id=callback_query.message.chat.id, text="Выберите категорию", reply_markup=create_keyboard(buttons_questions, True))


@router.callback_query(lambda c: c.data == 'subscription')
async def process_what_bot_can_do(callback_query: types.CallbackQuery, state: FSMContext, bot: Bot):
    await callback_query.answer()

    user: User = await db.get_user_data(callback_query.message.chat.id)

    if not user.payment_date:
        yk = YookassaHandler()
        url: str = yk.create_first_payment(callback_query.message.chat.id)
        await callback_query.message.answer("Информация о подписке", reply_markup=inline.payment(url))
    else:
        await callback_query.message.answer(f"У вас оформлена подписка. Она действительна до {user.payment_date}. Следующее списание будет []. Автоплатёж включён.", reply_markup=inline.my_subscription(user))
