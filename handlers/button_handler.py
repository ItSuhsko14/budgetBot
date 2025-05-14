from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from data.chat_data import chat_data
from utils.logger import logger
from handlers.message_handler import cleanup_ephemeral_messages
from button.delete_mode import handle_delete_product, finish_deleting
from button.purchase_mode import finalize_purchasing, mark_purchased
from button.edit_mode import finalize_editing
from utils.initialize_chat import initialize_chat


async def button(update: Update, context: CallbackContext):
    print("✅ Натиснуто кнопку")
    query = update.callback_query
    chat_id = query.message.chat_id
    item = query.data
    action, *params = item.split(":", 1)
    print('item in button_handler:', item)

    # 🛡️ Ініціалізація chat_data для нового чату
    initialize_chat(chat_id)

    if action == "finish_editing":
        await finalize_editing(update, context)
        return

    if action == "finish_purchasing":
        await finalize_purchasing(update, context)
        return

    if action == "mark_delete":
        await handle_delete_product(update, context)
        return
    
    if action == "unmark_delete":
        await handle_delete_product(update, context)
        return

    if action == "finish_deleting":
        await finish_deleting(update, context)
        return

    if chat_data[chat_id]['purchase_mode']:
        await mark_purchased(update, context)
        return