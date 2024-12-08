from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from data.chat_data import chat_data
from utils.logger import logger

async def make_list_editable(chat_id, context):
    if chat_data[chat_id]['list_items']:
        keyboard = [[InlineKeyboardButton(item, callback_data=item)] for item in chat_data[chat_id]['list_items']]
        keyboard.append([InlineKeyboardButton("Завершити редагування", callback_data="finish_editing")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(chat_id, "Оберіть товар для видалення:", reply_markup=reply_markup)
    else:
        await context.bot.send_message(chat_id, "Ваш список покупок порожній!")

async def handle_message(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_text = update.message.text
    print(user_text)

    if chat_id not in chat_data:
        chat_data[chat_id] = {'list_items': [], 'list_message_id': None}

    if user_text == "Додати товар":
        await context.bot.send_message(chat_id, "Введіть товар:")

    elif user_text == "Редагувати список":
        await make_list_editable(chat_id, context)

    elif 'list_items' in chat_data[chat_id]:
        chat_data[chat_id]['list_items'].append(user_text)
        print(f"Товар додано у чат {chat_id}: {user_text}")

        full_list = "\n".join(chat_data[chat_id]['list_items'])
        if chat_data[chat_id]['list_message_id']:
            try:
                await context.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=chat_data[chat_id]['list_message_id'],
                    text=f"Список покупок:\n{full_list}"
                )
            except Exception as e:
                logger.error(f"Не вдалося оновити повідомлення: {e}")
                sent_message = await context.bot.send_message(chat_id, f"Список покупок:\n{full_list}")
                chat_data[chat_id]['list_message_id'] = sent_message.message_id
        else:
            sent_message = await context.bot.send_message(chat_id, f"Список покупок:\n{full_list}")
            chat_data[chat_id]['list_message_id'] = sent_message.message_id
