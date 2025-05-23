# button/purchase_mode.py

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from data.chat_data import chat_data
from data.db_service import get_products_by_ids, get_active_products_by_chat, mark_product_as_purchased
from handlers.message_handler import cleanup_ephemeral_messages
from utils.logger import log


async def finalize_purchasing(update, context: CallbackContext):
    query = update.callback_query
    chat_id = query.message.chat_id

    chat_data[chat_id]['purchase_mode'] = False
    purchased_product_ids = set(chat_data[chat_id]['purchased_items'])
    purchased_products = get_products_by_ids(purchased_product_ids)
    purchased_names = [product[1] for product in purchased_products]
    purchased_list = "\n".join(purchased_names) if purchased_names else "порожній"

    text = f"Ви обрали наступні товари як куплені:\n{purchased_list}\nВведіть вартість цих товарів:"
    await cleanup_ephemeral_messages(chat_id, context)
    sent = await context.bot.send_message(chat_id, text)
    chat_data[chat_id]['purchased_message_id'] = sent.message_id
    chat_data[chat_id]['awaiting_cost'] = True
    await query.answer()


async def mark_purchased(update, context: CallbackContext):
    query = update.callback_query
    chat_id = query.message.chat_id
    item = query.data

    try:
        product_id = int(item)
        mark_product_as_purchased(product_id)
        log(f"✅ Товар з ID {product_id} позначено як 'purchased'.")

        chat_data[chat_id]['list_items'] = [
            i for i in chat_data[chat_id]['list_items'] if str(i) != str(product_id)
        ]
        chat_data[chat_id]['purchased_items'].append(str(product_id))

        products = get_active_products_by_chat(chat_id)

        if products:
            keyboard = [[InlineKeyboardButton(f"{product[1]}", callback_data=str(product[0]))]
                        for product in products]
            keyboard.append([InlineKeyboardButton("Завершити вибір товарів", callback_data="finish_purchasing")])
            await query.edit_message_text(
                text=f"Оберіть товари для позначення купленими:\n\n",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            await query.edit_message_text(
                text="Список покупок порожній!",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Завершити вибір товарів", callback_data="finish_purchasing")]
                ])
            )

    except ValueError:
        log(f"❌ Неправильний формат ID товару: {item}")

    await query.answer()