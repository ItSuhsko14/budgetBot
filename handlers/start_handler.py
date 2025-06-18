from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from data.chat_data import chat_data
from utils.logger import log
from utils.keyboard import create_keyboard, remove_keyboard
from data.db_service import get_active_products_by_chat


async def start(update: Update, context: CallbackContext):
    log(f"/start від {update.message.from_user.username} у чаті {update.effective_chat.id}")
    chat_id = update.effective_chat.id

    # Перевіряємо чи існує запис для цього чату, якщо ні — створюємо
    if chat_id not in chat_data:
        chat_data[chat_id] = {
            'list_items': [],
            'removed_items': [],
            'purchased_items': [],
            'selected_items': [],
            'keyboard_message_id': None,
            'list_message_id': None,
            'purchase_mode': False,
            'awaiting_cost': False,
            'purchased_message_id': None,
            'ephemeral_messages': [],
            'prompt_message_id': None
        }

    products = get_active_products_by_chat(chat_id)

    # Зберігаємо в локальний стейт
    chat_data[chat_id]['list_items'] = products
    await remove_keyboard(update, context)
    await create_keyboard(chat_id, update)
    