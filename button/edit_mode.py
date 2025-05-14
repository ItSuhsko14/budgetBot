# button/edit_mode.py

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext
from data.chat_data import chat_data
from data.db_service import get_active_products_by_chat
from handlers.message_handler import cleanup_ephemeral_messages

async def finalize_editing(update: Update, context: CallbackContext):
    query = update.callback_query
    chat_id = query.message.chat_id

    print("Завершення видалення")
    await cleanup_ephemeral_messages(chat_id, context)

    # Отримання оновленого списку товарів
    print(f"🔍 Отримання активних товарів для чату {chat_id}")
    products = get_active_products_by_chat(chat_id)
    print(f"📦 Отримані товари: {products}")

    if products:
        product_list = "\n".join([f"{product[1]}" for product in products])
        response_text = f"ТОВАРИ ДЛЯ ПОКУПКИ:\n{product_list}"
    else:
        response_text = "Ваш список товарів порожній."

    print(f"📢 Відправлення повідомлення: {response_text}")
    await context.bot.send_message(chat_id, response_text)
    await query.answer()