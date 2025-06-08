from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext
from data.db_service import mark_product_as_deleted
from data.db_service import get_active_products_by_chat
from utils.logger import log
from data.chat_data import chat_data
from utils.keyboard import update_keyboard

async def finish_deleting(update: Update, context: CallbackContext):
    query = update.callback_query
    chat_id = query.message.chat_id

    removed_ids = chat_data[chat_id].get('selected_items', [])
    log(f"removed_ids: {removed_ids}")

    if removed_ids:
        for product_id in removed_ids:
            log(f"✅ Товар з ID {product_id} позначено як 'deleted'.")
            mark_product_as_deleted(product_id)
        chat_data[chat_id]['selected_items'] = []
    
    chat_data[chat_id]['list_items'] = get_active_products_by_chat(chat_id)
    chat_data[chat_id]['selected_items'] = []

    await update_keyboard(chat_id, context)