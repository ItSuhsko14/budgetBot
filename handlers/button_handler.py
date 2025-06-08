from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from data.chat_data import chat_data
from utils.logger import log
from handlers.message_handler import prompt_add_product
from button.delete_mode import finish_deleting
from button.purchase_mode import finalize_purchasing
from button.edit_mode import finalize_editing
from utils.initialize_chat import initialize_chat
from button.select import select_product, unselect_product
from utils.keyboard import update_keyboard

async def button(update: Update, context: CallbackContext):
    print("✅ Натиснуто кнопку", update.callback_query.data)
    query = update.callback_query
    chat_id = query.message.chat_id
    item = query.data
    action, *params = item.split(":", 1)
    log(f"✅ Натиснуто кнопку action {action}")
    log(f"✅ params {params}")
    print('item in button_handler:', item)

    # 🛡️ Ініціалізація chat_data для нового чату
    initialize_chat(chat_id)

    if action == "finish_editing":
        await finalize_editing(update, context)
        return

    if action == "finish_deleting":
        await finish_deleting(update, context)
        return

    if action == "finish_purchasing":
        await finalize_purchasing(update, context)
        return

    if action == "add_product":
        await prompt_add_product(chat_id, context)
        return

    if action == "select":
        await select_product(chat_id, params[0])
        await update_keyboard(chat_id, context)
        return
    
    if action == "unselect":
        await unselect_product(chat_id, params[0])
        await update_keyboard(chat_id, context)
        return