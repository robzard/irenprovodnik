from aiogram import Router, types, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.types import FSInputFile, ReplyKeyboardRemove

from filters.all_filters import ReplyButtonsQuestions
from states.states import FSMGpt
from utils.dict_buttons import buttons_questions
from utils.utils import MessageEditor, process_parent_button, process_child_button

from keyboards.user.reply import create_keyboard

from keyboards.user.inline import command_start
from lexicon.lexicon import LEXICON

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
async def handle_message(message: types.Message, bot: Bot, state: FSMContext):
    await message.delete()
    if message.text in buttons_questions:
        await process_parent_button(message, bot)
    else:
        await state.update_data({'questions_category': message.text})
        await process_child_button(message, state)


@router.message(F.text == 'Назад')
async def gpt_question(message: types.Message, bot: Bot, state: FSMContext):
    await message.answer(text='Выберите что вас интересует..', reply_markup=create_keyboard(buttons_questions, True))


@router.message(F.text == 'Меню')
async def gpt_question(message: types.Message, bot: Bot, state: FSMContext):
    image_path = './static/images/iren.jpg'
    media = FSInputFile(image_path)
    msg = await message.answer("Возврат в меню", reply_markup=ReplyKeyboardRemove())
    await msg.delete()
    await message.answer_photo(photo=media, caption=LEXICON['user_command_start'], reply_markup=command_start(message.from_user.id))
