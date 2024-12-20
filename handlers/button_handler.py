# handlers/button_handler.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from data.chat_data import chat_data
from utils.logger import logger
from handlers.message_handler import cleanup_ephemeral_messages
from data.db_service import mark_product_as_deleted, get_active_products_by_chat


async def button(update: Update, context: CallbackContext):
    query = update.callback_query
    chat_id = query.message.chat_id
    item = query.data

    # Завершити видалення
    if item == "finish_editing":
            print("Завершення видалення")
            # Очищення ефемерних повідомлень
            await cleanup_ephemeral_messages(chat_id, context)
            
            # Отримання актуальних товарів з бази даних
            products = get_active_products_by_chat(chat_id)
            
            if products:
                # Формування тексту зі списком товарів
                product_list = "\n".join([f"{product[1]} - {product[2]}" for product in products])
                response_text = f"Поточний список товарів:\n{product_list}"
            else:
                response_text = "Ваш список товарів порожній."

            # Відправлення повідомлення користувачу
            await context.bot.send_message(chat_id, response_text)
            
            # Редагування старого повідомлення
            await query.edit_message_text("Видалення товарів завершено.")
            await query.answer()
            return

    # Завершити вибір товарів для покупки
    if item == "finish_purchasing":
        chat_data[chat_id]['purchase_mode'] = False
        purchased_list = "\n".join(chat_data[chat_id]['purchased_items']) if chat_data[chat_id]['purchased_items'] else "порожній"
        text = f"Ви обрали наступні товари як куплені:\n{purchased_list}\nВведіть вартість цих товарів:"
        await cleanup_ephemeral_messages(chat_id, context)
        sent = await context.bot.send_message(chat_id, text)
        chat_data[chat_id]['purchased_message_id'] = sent.message_id
        chat_data[chat_id]['awaiting_cost'] = True
        await query.answer()
        return

    # Перевірка на режим позначення купленими
    if chat_data[chat_id]['purchase_mode']:
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
            await query.edit_message_text(
                text="Список покупок порожній!",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("завершити вибір товарів", callback_data="finish_purchasing")]
                ])
            )
        await query.answer()
        return

    # Режим видалення товарів (оновлення в БД)
    try:
        product_id = int(item)
        print(f"✅ Натиснуто видалення товару з ID: {product_id}")
        mark_product_as_deleted(product_id)
        logger.info(f"Товар з ID {product_id} видалено у чаті {chat_id}.")

        # Оновлення списку після видалення
        products = get_active_products_by_chat(chat_id)
        if products:
            keyboard = [[InlineKeyboardButton(f"{product[1]} ({product[2]})", callback_data=str(product[0]))] for product in products]
            keyboard.append([InlineKeyboardButton("Завершити видалення", callback_data="finish_editing")])
            full_list = "\n".join([f"{product[1]} - {product[2]}" for product in products])
            await query.edit_message_text(
                text=f"Оберіть товар для видалення:\n\nСписок покупок:\n{full_list}",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            await query.edit_message_text(
                text="Список покупок порожній!",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Завершити видалення", callback_data="finish_editing")]
                ])
            )
    except ValueError:
        logger.error(f"Неправильний формат ID товару: {item}")

    await query.answer()
