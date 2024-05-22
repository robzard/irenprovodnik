from aiogram import Router, types, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter

from filters.all_filters import ReplyButtonsQuestions
from states.states import FSMGpt, FsmData
from utils.dict_buttons import buttons_questions
from utils.utils import MessageEditor, process_parent_button, process_child_button

router = Router(name=__name__)


@router.message(StateFilter(FSMGpt.wait_question), F.text != '/start')
async def gpt_question(message: types.Message, state: FSMContext):
    await message.reply('Cкоро отвечу')
    # state_data = await state.get_data()
    # gpt: GPT = state_data.get('gpt')
    # user_question = message.text
    # answer, history = await gpt.ask_gigachat(user_question, gpt.history)
    # await state.set_data({'gpt': gpt})
    #
    # await message.reply(answer, reply_markup=support_quit())


@router.message(ReplyButtonsQuestions())
async def handle_message(message: types.Message, bot: Bot, message_editor: MessageEditor, fsm_data: FsmData):
    await message.delete()
    if message.text in buttons_questions:
        await process_parent_button(message, bot, message_editor, fsm_data)
    else:
        await process_child_button(message, message_editor, fsm_data)
