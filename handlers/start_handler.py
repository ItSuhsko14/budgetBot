from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import CallbackContext
from data.chat_data import chat_data
from utils.logger import logger

async def start(update: Update, context: CallbackContext):
    logger.info(f"/start від {update.message.from_user.username} у чаті {update.effective_chat.id}")
    chat_id = update.effective_chat.id

    # Перевіряємо чи існує запис для цього чату, якщо ні — створюємо
    if chat_id not in chat_data:
        chat_data[chat_id] = {
            'list_items': [],
            'removed_items': [],
            'purchased_items': [],
            'list_message_id': None,
            'purchase_mode': False,
            'awaiting_cost': False,
            'purchased_message_id': None,
            'ephemeral_messages': []  # Ініціалізуємо порожній список для ефемерних повідомлень
        }

    keyboard = [
        [KeyboardButton("Додати товар")],
        [KeyboardButton("Видалити товар")],
        [KeyboardButton("Позначити купленими")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    await update.message.reply_text(
        "Привіт! Я бот для списків покупок! Оберіть дію:",
        reply_markup=reply_markup
    )
