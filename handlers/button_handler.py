from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from data.chat_data import chat_data
from utils.logger import logger

async def make_list_editable_after_removal(chat_id, context, query):
    if chat_data[chat_id]['list_items']:
        keyboard = [[InlineKeyboardButton(item, callback_data=item)] for item in chat_data[chat_id]['list_items']]
        keyboard.append([InlineKeyboardButton("Завершити редагування", callback_data="finish_editing")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=query.message.message_id,
            text="Оберіть товар для видалення:",
            reply_markup=reply_markup
        )
    else:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=query.message.message_id,
            text="Ваш список покупок порожній!"
        )

    await query.answer()

async def button(update: Update, context: CallbackContext):
    query = update.callback_query
    chat_id = query.message.chat_id
    item = query.data

    # Перевіряємо, чи це клік по кнопці товару, а не "finish_editing"
    if item != "finish_editing" and item in chat_data[chat_id]['list_items']:
        chat_data[chat_id]['list_items'].remove(item)
        logger.info(f"Товар видалено зі списку в чаті {chat_id}: {item}")

    # Після видалення товару або при натисканні "finish_editing" оновлюємо інтерфейс
    await make_list_editable_after_removal(chat_id, context, query)
