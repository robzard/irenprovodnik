from aiogram import Router, types, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile

from filters.all_filters import MarafonBuyFilter
from keyboards.user import inline
from lexicon.lexicon import LEXICON
from utils.utils import MessageEditor

from common.yookassa_payment.yookassa_handler import YookassaHandler

router = Router(name=__name__)


@router.message(MarafonBuyFilter())
async def course_change_inline(message: types.InlineQueryResult, state: FSMContext):
    yk = YookassaHandler()
    url: str = yk.create_url_pay_marafon(message.chat.id)

    await message.answer(text=LEXICON['pay_marafon'], reply_markup=inline.pay_marafon(url))
