from aiogram import Router, types, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile

from filters.all_filters import CourseNameFilter, CourseBuyFilter
from keyboards.user import inline
from lexicon.lexicon import LEXICON
from utils.utils import MessageEditor

router = Router(name=__name__)


@router.message(CourseNameFilter())
async def course_show(message: types.InlineQueryResult, state: FSMContext, course_names: dict):
    course_name_id = course_names[message.text]
    image_path = f'./static/images/{course_name_id}.jpg'
    media = FSInputFile(image_path)
    await message.answer_photo(photo=media, caption=LEXICON[course_name_id], reply_markup=inline.web_query_course(course_name_id, message.from_user.id))
    await state.update_data(selected_course=message.text)


@router.message(CourseBuyFilter())
async def course_change_inline(message: types.InlineQueryResult, state: FSMContext, course_name: str, course_names: dict):
    course_name_id = course_names[course_name]
    image_path = f'./static/images/{course_name_id}.jpg'
    media = FSInputFile(image_path)
    await message.answer_photo(photo=media, caption=LEXICON[course_name_id], reply_markup=inline.buy_course_registration())
    await state.update_data(selected_course=course_name)

