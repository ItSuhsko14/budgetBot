from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import CallbackContext
from data.chat_data import chat_data
from utils.logger import logger

async def start(update: Update, context: CallbackContext):
    logger.info(f"/start від {update.message.from_user.username} у чаті {update.effective_chat.id}")
    chat_id = update.effective_chat.id
    if chat_id not in chat_data:
        chat_data[chat_id] = {'list_items': [], 'list_message_id': None}

    keyboard = [
        [KeyboardButton("Додати товар")],
        [KeyboardButton("Редагувати список")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    await update.message.reply_text(
        "Привіт! Я бот для списків покупок! Натисніть кнопку нижче, щоб додати товар або редагувати список.",
        reply_markup=reply_markup
    )
