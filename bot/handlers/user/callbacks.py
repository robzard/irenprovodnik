import json

from aiogram import Router, types, Bot

from aiogram.fsm.context import FSMContext

from handlers.user.commands import on_start
from keyboards.user import inline
from keyboards.user.inline import menu
from keyboards.user.reply import create_keyboard

from states.states import FSMGpt, FsmData
from utils.dict_buttons import buttons_questions
from utils.utils import delete_need_messages, MessageEditor, delete_message_default

router = Router(name=__name__)


@router.callback_query(lambda c: c.data == 'start')
async def handle_start_callback(callback_query: types.CallbackQuery, state: FSMContext, bot: Bot, message_editor: MessageEditor, fsm_data: FsmData):
    await callback_query.answer()
    await delete_need_messages(bot, callback_query.message.chat.id, fsm_data)
    await on_start(callback_query.message, fsm_data, bot, message_editor, callback_query.from_user.id)


@router.callback_query(lambda c: c.data == 'start_new')
async def handle_start_new_callback(callback_query: types.CallbackQuery, state: FSMContext, bot: Bot, message_editor: MessageEditor, fsm_data: FsmData):
    await callback_query.answer()
    await delete_need_messages(bot, callback_query.message.chat.id, fsm_data)
    if fsm_data.category_message_id:
        fsm_data.msg_need_delete_on_start.append(fsm_data.category_message_id)
    if fsm_data.edit_message:
        fsm_data.msg_need_delete_on_start.append(fsm_data.edit_message)
    await fsm_data.update_data(edit_message=None, msg_need_delete_on_start=fsm_data.msg_need_delete_on_start)
    await on_start(callback_query.message, fsm_data, bot, message_editor, callback_query.from_user.id)


@router.callback_query(lambda c: c.data == 'support')
async def process_what_bot_can_do(callback_query: types.CallbackQuery, state: FSMContext, fsm_data: FsmData):
    await callback_query.answer()
    await callback_query.message.answer("Напишите свой вопрос и я вам помогу разобраться с вашей проблемой.")
    await state.set_state(FSMGpt.wait_question)
    # await state.set_data({'history': []})
    await fsm_data.update_data(handler_name='Написать менеджеру', history=[])


@router.callback_query(lambda c: c.data == 'support_quit')
async def process_what_bot_can_do(callback_query: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback_query.answer('Вы вышли из чата с ассистентом.')
    await callback_query.message.answer('Вы вышли из консультации с ассистентом. (Тут можно переводить на менеджера)', reply_markup=menu())


@router.callback_query(lambda c: c.data == 'questions')
async def process_what_bot_can_do(callback_query: types.CallbackQuery, fsm_data: FsmData, bot: Bot):
    await callback_query.answer()
    await delete_message_default(callback_query.message.chat.id, fsm_data.edit_message, bot)
    fsm_data.edit_message = None
    msg: types.Message = await callback_query.message.answer(text='Выберите что вас интересует..', reply_markup=create_keyboard(buttons_questions))
    fsm_data.msg_need_delete.append(msg.message_id)
    await fsm_data.update_data(handler_name='Часто задаваемые вопросы', msg_need_delete=fsm_data.msg_need_delete)


@router.callback_query(lambda c: c.data == 'contacts')
async def process_what_bot_can_do(callback_query: types.CallbackQuery, fsm_data: FsmData):
    await callback_query.message.edit_reply_markup(reply_markup=inline.contacts())
    await fsm_data.update_data(handler_name='Контакты')


@router.callback_query(lambda c: c.data == 'back_to_course')
async def process_what_bot_can_do(callback_query: types.CallbackQuery, fsm_data: FsmData):
    await callback_query.message.edit_reply_markup(reply_markup=inline.web_query_course(fsm_data.course_name_id, callback_query.from_user.id))
    await fsm_data.update_data(handler_name='Назад')


@router.callback_query(lambda c: c.data == 'buy_course')
async def process_what_bot_can_do(callback_query: types.CallbackQuery, fsm_data: FsmData):
    await callback_query.message.edit_reply_markup(reply_markup=inline.buy_course_registration())
    await fsm_data.update_data(handler_name='Купить курс')


@router.callback_query(lambda c: c.data == 'questions_back_menu')
async def process_what_bot_can_do(callback_query: types.CallbackQuery, fsm_data: FsmData, bot: Bot, message_editor: MessageEditor):
    await callback_query.answer()
    if fsm_data.category_message_id:
        await delete_message_default(callback_query.message.chat.id, fsm_data.category_message_id, bot)
        await fsm_data.update_data(category_message_id=None)

    await delete_need_messages(bot, callback_query.message.chat.id, fsm_data)
    await callback_query.message.delete()
    await fsm_data.update_data(edit_message=None)
    await on_start(callback_query.message, fsm_data, bot, message_editor, callback_query.from_user.id)


@router.callback_query(lambda c: c.data == 'chose_another_category')
async def process_what_bot_can_do(callback_query: types.CallbackQuery, fsm_data: FsmData, bot: Bot):
    await callback_query.answer()
    await delete_need_messages(bot, callback_query.message.chat.id, fsm_data)
    await delete_message_default(callback_query.message.chat.id, fsm_data.category_message_id, bot)
    await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=fsm_data.edit_message)
    msg = await bot.send_message(chat_id=callback_query.message.chat.id, text="Выберите категорию", reply_markup=create_keyboard(buttons_questions))
    await fsm_data.update_data(edit_message=None, category_message_id=msg.message_id)
