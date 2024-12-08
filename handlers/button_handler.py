# handlers/button_handler.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from data.chat_data import chat_data
from utils.logger import logger
from handlers.message_handler import cleanup_ephemeral_messages

async def button(update: Update, context: CallbackContext):
    query = update.callback_query
    chat_id = query.message.chat_id
    item = query.data

    # Завершити видалення
    if item == "finish_editing":
        # Завершуємо редагування: видаляємо ефемерні повідомлення
        await cleanup_ephemeral_messages(chat_id, context)
        # Просто оновлюємо список покупок. Ефемерні повідомлення вже видалені.
        await query.edit_message_text("Видалення товарів завершено.")
        await query.answer()
        return

    # Завершити вибір товарів для покупки
    if item == "finish_purchasing":
        # Вимикаємо purchase_mode
        chat_data[chat_id]['purchase_mode'] = False
        # Надсилаємо повідомлення з купленими товарами
        purchased_list = "\n".join(chat_data[chat_id]['purchased_items']) if chat_data[chat_id]['purchased_items'] else "порожній"
        text = f"Ви обрали наступні товари як куплені:\n{purchased_list}\nВведіть вартість цих товарів:"

        # Видаляємо ефемерні повідомлення перед надсиланням фінального повідомлення
        await cleanup_ephemeral_messages(chat_id, context)
        sent = await context.bot.send_message(chat_id, text)
        chat_data[chat_id]['purchased_message_id'] = sent.message_id
        chat_data[chat_id]['awaiting_cost'] = True
        await query.answer()
        return

    if chat_data[chat_id]['purchase_mode']:
        # Режим позначення купленими
        if item in chat_data[chat_id]['list_items']:
            chat_data[chat_id]['list_items'].remove(item)
            chat_data[chat_id]['purchased_items'].append(item)
            logger.info(f"Товар позначено купленим у чаті {chat_id}: {item}")

        if chat_data[chat_id]['list_items']:
            keyboard = [[InlineKeyboardButton(i, callback_data=i)] for i in chat_data[chat_id]['list_items']]
            keyboard.append([InlineKeyboardButton("завершити вибір товарів", callback_data="finish_purchasing")])
            full_list = "\n".join(chat_data[chat_id]['list_items'])
            await query.edit_message_text(
                text=f"Оберіть товари для позначення купленими:\n\nСписок покупок:\n{full_list}",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            keyboard = [[InlineKeyboardButton("завершити вибір товарів", callback_data="finish_purchasing")]]
            await query.edit_message_text(
                text="Список покупок порожній!",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        await query.answer()
        return
    else:
        # Режим видалення товарів
        if item in chat_data[chat_id]['list_items']:
            chat_data[chat_id]['list_items'].remove(item)
            logger.info(f"Товар видалено у чаті {chat_id}: {item}")

            if chat_data[chat_id]['list_items']:
                keyboard = [[InlineKeyboardButton(i, callback_data=i)] for i in chat_data[chat_id]['list_items']]
                keyboard.append([InlineKeyboardButton("Завершити видалення", callback_data="finish_editing")])
                full_list = "\n".join(chat_data[chat_id]['list_items'])
                await query.edit_message_text(
                    text=f"Оберіть товар для видалення:\n\nСписок покупок:\n{full_list}",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            else:
                keyboard = [[InlineKeyboardButton("Завершити видалення", callback_data="finish_editing")]]
                await query.edit_message_text(
                    text="Список покупок порожній!",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
        await query.answer()
