import json
from typing import Tuple, Optional

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Update, InlineKeyboardMarkup, InputMediaPhoto, CallbackQuery, Message
from aiogram import types, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile, Message

from config_data.config import load_config
from keyboards.user.inline import questions_back_menu
from keyboards.user.reply import create_keyboard
from utils.dict_buttons import buttons_questions
# from custom_logger.logger import logger
import logging

config = load_config()


def get_chat_id_from_event(event: Update) -> int:
    if event.message:
        return event.message.chat.id
    elif event.callback_query and event.callback_query.message:
        return event.callback_query.message.chat.id
    elif event.channel_post:
        return event.channel_post.chat.id
    elif event.edited_message:
        return event.edited_message.chat.id


# async def edit_or_send_message(message: types.InlineQueryResult | types.Message, state: FSMContext, bot: Bot,
#                                photo_path: str = None,
#                                course_name_id: str = None,
#                                photo: bool = False,
#                                caption: str = None,
#                                reply_markup: InlineKeyboardMarkup = None,
#                                reply_markup_push: bool = False):
#     data = await state.get_data()
#     edit_message = data.get('edit_message')
#     edit_message_update_data = data.get('update_data', {})
#     course_name_id = course_name_id or data.get('course_name_id', None)
#     image_path = photo_path or (f'./static/images/{course_name_id}.jpg' if course_name_id else None)
#     update_data = {}
#     sent_message: types.Message = None
#
#     serialized_reply_markup = json.dumps(reply_markup.inline_keyboard.__str__(), ensure_ascii=False) if reply_markup else None
#
#     if message.text == '/start':
#         update_data = {}
#         if photo:
#             send_method = message.answer_photo
#             send_args = {'photo': FSInputFile(image_path)}
#             update_data['filename'] = send_args['photo'].filename
#             if caption:
#                 send_args['caption'] = caption
#                 update_data['caption'] = caption
#         else:
#             send_method = message.answer
#             send_args = {'text': caption}
#             update_data['caption'] = caption
#         if reply_markup:
#             send_args['reply_markup'] = reply_markup
#             update_data['reply_markup'] = serialized_reply_markup
#         sent_message: Message = await send_method(**send_args)
#         await state.update_data(edit_message=sent_message.message_id)
#         await state.update_data(course_name_id=course_name_id, update_data=update_data)
#         return
#
#     data = await state.get_data()
#     edit_message = data.get('edit_message')
#
#     if edit_message:
#         if not reply_markup_push and (not reply_markup or serialized_reply_markup == edit_message_update_data.get('reply_markup', None)):
#             reply_markup = None
#         if not image_path or edit_message_update_data.get('filename', None) == (image_path.split('/')[-1] if image_path else None):
#             photo = None
#         if not caption or caption == edit_message_update_data.get('caption', None):
#             caption = None
#
#     if not any([reply_markup, photo, caption]):
#         return
#
#     if edit_message:
#         if photo:
#             media = InputMediaPhoto(media=FSInputFile(image_path))
#             update_data['filename'] = media.media.filename
#             if caption:
#                 media.caption = caption
#                 update_data['caption'] = caption
#             edit_args = {'chat_id': message.chat.id, 'message_id': edit_message, 'media': media}
#             if reply_markup is not None:
#                 edit_args['reply_markup'] = reply_markup
#                 update_data['reply_markup'] = serialized_reply_markup
#             try:
#                 sent_message: Message = await bot.edit_message_media(**edit_args)
#             except TelegramBadRequest:
#                 if message.text == '/start':
#                     update_data = {}
#                     if photo:
#                         send_method = message.answer_photo
#                         send_args = {'photo': FSInputFile(image_path)}
#                         update_data['filename'] = send_args['photo'].filename
#                         if caption:
#                             send_args['caption'] = caption
#                             update_data['caption'] = caption
#                     else:
#                         send_method = message.answer
#                         send_args = {'text': caption}
#                         update_data['caption'] = caption
#                     if reply_markup:
#                         send_args['reply_markup'] = reply_markup
#                         update_data['reply_markup'] = serialized_reply_markup
#                     sent_message: Message = await send_method(**send_args)
#                     await state.update_data(edit_message=sent_message.message_id)
#                     await state.update_data(course_name_id=course_name_id, update_data=update_data)
#                     return
#         else:
#             edit_args = {'chat_id': message.chat.id, 'message_id': edit_message}
#             if caption:
#                 edit_args['text'] = caption
#                 update_data['caption'] = caption
#                 if reply_markup:
#                     edit_args['reply_markup'] = reply_markup
#                     update_data['reply_markup'] = serialized_reply_markup
#                 try:
#                     sent_message: Message = await bot.edit_message_text(**edit_args)
#                 except TelegramBadRequest:
#                     edit_args['caption'] = caption
#                     if edit_args.get('text', None):
#                         edit_args.pop('text')
#                     # if data.get('update_data', {}).get('reply_markup', None):
#                     #     edit_args['reply_markup'] = reply_markup
#                     #     update_data['reply_markup'] = serialized_reply_markup
#                     try:
#                         sent_message: Message = await bot.edit_message_caption(**edit_args)
#                     except TelegramBadRequest:
#                         await state.update_data(edit_message=None, update_data=update_data)
#                         return
#             elif reply_markup:
#                 if serialized_reply_markup == edit_message_update_data.get('reply_markup', None):
#                     return
#                 edit_args['reply_markup'] = reply_markup
#                 sent_message: Message = await bot.edit_message_reply_markup(**edit_args)
#         if sent_message:
#             await state.update_data(edit_message=sent_message.message_id, update_data=update_data)
#     else:
#         if photo:
#             send_method = message.answer_photo
#             send_args = {'photo': FSInputFile(image_path)}
#             update_data['filename'] = send_args['photo'].filename
#             if caption:
#                 send_args['caption'] = caption
#                 update_data['caption'] = caption
#         else:
#             send_method = message.answer
#             send_args = {'text': caption}
#             update_data['caption'] = caption
#         if reply_markup:
#             send_args['reply_markup'] = reply_markup
#             update_data['reply_markup'] = serialized_reply_markup
#         sent_message: Message = await send_method(**send_args)
#         await state.update_data(edit_message=sent_message.message_id)
#     await state.update_data(course_name_id=course_name_id, update_data=update_data)


class MessageEditor:
    def __init__(self, bot: Bot, state: FSMContext):
        self.bot = bot
        self.state = state

    async def handle_message(self, message: types.Message | types.InlineQueryResult, **kwargs):
        if message.text == '/start':
            await self.process_start_message(message, **kwargs)
        else:
            await self.edit_or_resend_message(message, **kwargs)

    async def process_start_message(self, message: types.Message | types.InlineQueryResult, **kwargs):
        data = await self.extract_message_data(**kwargs)
        logging.debug(f'Данные для отправки нового сообщения (start): {data.__str__()}')
        await self.send_message(message, **data)

    async def edit_or_resend_message(self, message: types.Message | types.InlineQueryResult, **kwargs):
        edit_message_id = self.state.edit_message

        if edit_message_id:
            try:
                await self.edit_message(message, edit_message_id, **kwargs)
            except TelegramBadRequest as ex:
                logging.warning(f'Сообщение одинаковое - error {str(ex)}')
            except Exception as ex:
                logging.error(str(ex))
                await self.process_start_message(message, **kwargs)
        else:
            await self.process_start_message(message, **kwargs)

    async def send_message(self, message: types.Message | types.InlineQueryResult, **kwargs):
        if kwargs.get('send_args', {}).get('photo'):
            edit_message = await message.answer_photo(**kwargs['send_args'])
            logging.debug(f'Сообщение успешно отправлено (с фото), message_id - {edit_message.message_id}')
        else:
            edit_message = await message.answer(**kwargs['send_args'])
            logging.debug(f'Сообщение успешно отправлено (без фото), message_id - {edit_message.message_id}')

        await self.update_state(edit_message, **kwargs)

    async def edit_message(self, message: types.Message | types.InlineQueryResult, edit_message_id, **kwargs):
        data = await self.extract_message_data(**kwargs, edit=True)
        logging.debug(f'Данные для изменения сообщения: {data.__str__()}')

        if kwargs.get('photo'):
            edit_message = await self.bot.edit_message_media(chat_id=message.chat.id, message_id=edit_message_id, **data.get('send_args'))
            logging.debug(f'Сообщение успешно изменено (с фото), message_id - {edit_message.message_id}')
        elif kwargs.get('text'):
            edit_message = await self.bot.edit_message_text(chat_id=message.chat.id, message_id=edit_message_id, **data.get('send_args'))
            logging.debug(f'Сообщение успешно изменено (без фото с текстом), message_id - {edit_message.message_id}')
        else:
            edit_message = await self.bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=edit_message_id, **data.get('send_args'))
            logging.debug(f'Сообщение успешно изменено (только reply_markup), message_id - {edit_message.message_id}')

        await self.update_state(edit_message, **kwargs)

    async def extract_message_data(self, photo_path=None, course_name_id=None, photo=False, text=None, reply_markup=None, **kwargs):
        course_name_id = course_name_id or self.state.course_name_id or None
        image_path = photo_path or (f'./static/images/{course_name_id}.jpg' if course_name_id else None)
        edit = kwargs.get('edit')

        send_args = {}

        if photo:
            if edit:
                media = InputMediaPhoto(media=FSInputFile(image_path))
                media.caption = text
                send_args['media'] = media
                logging.debug(f'Изменение сообщения с фото')
            else:
                send_args['photo'] = FSInputFile(image_path)
                send_args['caption'] = text
                logging.debug(f'Отправка нового сообщения с фото')
        else:
            send_args = {'text': text} if text else {}
            logging.debug(f'Изменение сообщения только текста')

        if reply_markup:
            send_args['reply_markup'] = reply_markup

        return {'send_args': send_args, 'update_message_data': kwargs}

    async def update_state(self, message, **kwargs):
        await self.state.update_data(edit_message=message.message_id, **kwargs)


def extract_event_data(event: Update) -> CallbackQuery | Message | None:
    message_text = None
    if event.message:
        message_text = event.message
    elif event.callback_query:
        message_text = event.callback_query
    # Добавьте дополнительные проверки по мере необходимости
    return message_text


def get_event_text(event: Update) -> str:
    message_text = None
    if event.message:
        message_text = event.message.text
    elif event.callback_query:
        message_text = event.callback_query.data
    # Добавьте дополнительные проверки по мере необходимости
    return message_text


async def delete_need_messages(bot: Bot, chat_id: int, state: FSMContext, start=False):
    logging.debug('Удаление сообщений')

    async def delete_messages(message_ids):
        if len(message_ids) > 0:
            for msg_id in message_ids:
                try:
                    await bot.delete_message(chat_id, msg_id)
                except TelegramBadRequest as ex:
                    logging.warning(f'Не удалось удалить сообщение - {str(ex)}')
        else:
            logging.debug('Сообщения для удаления отсутствуют')

    await delete_messages(state.msg_need_delete)
    await state.update_data(msg_need_delete=[])

    if start:
        logging.debug('Удаление сообщений при запуске по msg_need_delete_on_start')
        await delete_messages(state.msg_need_delete_on_start)
        await state.update_data(msg_need_delete_on_start=[])

    return []


async def delete_category_message_id(message, bot, state: FSMContext):
    if state.category_message_id:
        try:
            await bot.delete_message(message.chat.id, state.category_message_id)
            logging.debug(f'Сообщение {state.category_message_id} успешно удалено')
        except TelegramBadRequest:
            state.category_message_id = None
            logging.warning(f'Ошибка при удалении сообщения {state.category_message_id}')


async def delete_edit_message(message: Message, bot: Bot, state: FSMContext):
    if state.edit_message:
        try:
            await bot.delete_message(message.chat.id, state.edit_message)
            logging.debug(f'Сообщение {state.edit_message} успешно удалено')
        except TelegramBadRequest:
            state.edit_message = None
            logging.warning(f'Ошибка при удалении сообщения {state.edit_message}')


async def delete_message_default(chat_id, message_id, bot: Bot):
    try:
        await bot.delete_message(chat_id, message_id)
        logging.debug(f'Сообщение {message_id} успешно удалено')
    except TelegramBadRequest:
        logging.warning(f'Такого сообщения не существует - {message_id}')


async def process_parent_button(message, bot):
    child_buttons = buttons_questions[message.text].get("children", {})
    if child_buttons:
        keyboard = create_keyboard(child_buttons, False)
        await message.answer(f"Выбранная категория: <b>{message.text}</b>", reply_markup=keyboard)


async def process_child_button(message, state: FSMContext):
    for parent_button, parent_data in buttons_questions.items():
        child_buttons = parent_data.get("children", {})
        if message.text in child_buttons:
            text_to_send = child_buttons[message.text].get("text", "Информация не найдена.")
            await message.answer(text=f'✅ Ответ по вопросу <b>"{message.text}"</b>:\n\n{text_to_send}')
            return
