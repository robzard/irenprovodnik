from aiogram import Router, types, Bot

from filters.all_filters import CourseNameFilter, CourseBuyFilter
from keyboards.user import inline
from lexicon.lexicon import LEXICON
from states.states import FsmData
from utils.utils import MessageEditor

router = Router(name=__name__)


@router.message(CourseNameFilter())
async def course_show(message: types.InlineQueryResult, fsm_data: FsmData, course_names: dict, message_editor: MessageEditor):
    course_name_id = course_names[message.text]

    await message.delete()
    await message_editor.handle_message(message, course_name_id=course_name_id, photo=True, text=LEXICON[course_name_id], reply_markup=inline.web_query_course(course_name_id, message.from_user.id))
    await fsm_data.update_data(handler_name=f'Курсы', selected_course=message.text)


@router.message(CourseBuyFilter())
async def course_change_inline(message: types.InlineQueryResult, fsm_data: FsmData, course_name: str, course_names: dict, message_editor: MessageEditor):
    # course_name_id = course_names[course_name]
    await message.delete()
    await message_editor.handle_message(message, reply_markup=inline.buy_course_registration())
    await fsm_data.update_data(handler_name='Купить курс')
