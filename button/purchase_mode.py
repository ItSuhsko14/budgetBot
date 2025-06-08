# button/purchase_mode.py

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext
from data.chat_data import chat_data
from data.db_service import get_active_products_by_chat, add_expense
# from handlers.message_handler import cleanup_ephemeral_messages
from utils.logger import log



async def finalize_purchasing(update: Update, context: CallbackContext):
    query = update.callback_query
    chat_id = query.message.chat_id
    chat_data[chat_id]['awaiting_cost'] = True
    purchased_products = chat_data[chat_id]['selected_items']

    log(f"✅ Список куплених товарів: {purchased_products}")
    await context.bot.send_message(chat_id, "Введіть вартість обраних товарів:")
    log("finilize_purchasing")