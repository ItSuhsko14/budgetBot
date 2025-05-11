# handlers/button_handler.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from data.chat_data import chat_data
from utils.logger import logger
from handlers.message_handler import cleanup_ephemeral_messages
from data.db_service import (
    mark_product_as_deleted, 
    get_active_products_by_chat,
    get_products_by_ids, 
    mark_product_as_purchased
)


async def button(update: Update, context: CallbackContext):
    query = update.callback_query
    chat_id = query.message.chat_id
    item = query.data

    # Завершити видалення
    if item == "finish_editing":
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
        await query.edit_message_text("Видалення товарів завершено.")
        await query.answer()
        return

   # Завершити вибір товарів для покупки
    if item == "finish_purchasing":
        chat_data[chat_id]['purchase_mode'] = False

        # IDs куплених товарів
        purchased_product_ids = set(chat_data[chat_id]['purchased_items'])  # Забираємо ID куплених товарів
        print(f"IDs куплених товарів: {purchased_product_ids}")

        # Отримуємо товари за їх ID
        purchased_products = get_products_by_ids(purchased_product_ids)  
        print(f"📦 Куплені товари: {purchased_products}")

        # Формуємо список назв куплених товарів
        purchased_names = [product[1] for product in purchased_products]

        # Формуємо текст для списку куплених товарів
        purchased_list = "\n".join(purchased_names) if purchased_names else "порожній"

        # Формуємо відповідь
        text = f"Ви обрали наступні товари як куплені:\n{purchased_list}\nВведіть вартість цих товарів:"
        await cleanup_ephemeral_messages(chat_id, context)
        sent = await context.bot.send_message(chat_id, text)
        chat_data[chat_id]['purchased_message_id'] = sent.message_id
        chat_data[chat_id]['awaiting_cost'] = True
        await query.answer()
        return


    # Позначення товару як купленого
    if chat_data[chat_id]['purchase_mode']:
        try:
            product_id = int(item)
            
            # Оновлення в базі даних
            mark_product_as_purchased(product_id)
            logger.info(f"✅ Товар з ID {product_id} позначено як 'purchased'.")

            # Видалення товару з локального списку
            chat_data[chat_id]['list_items'] = [
                i for i in chat_data[chat_id]['list_items'] if str(i) != str(product_id)
            ]
            chat_data[chat_id]['purchased_items'].append(str(product_id))

            # Оновлення списку товарів
            products = get_active_products_by_chat(chat_id)

            if products:
                # Формування нових кнопок
                keyboard = [
                    [InlineKeyboardButton(f"{product[1]}", callback_data=str(product[0]))]
                    for product in products
                ]
                keyboard.append([InlineKeyboardButton("Завершити вибір товарів", callback_data="finish_purchasing")])

                # Формування нового списку товарів
                full_list = "\n".join([f"{product[1]}" for product in products])

                # Оновлення повідомлення з товарами
                await query.edit_message_text(
                    text=f"Оберіть товари для позначення купленими:\n\n",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            else:
                # Якщо товари відсутні
                await query.edit_message_text(
                    text="Список покупок порожній!",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("Завершити вибір товарів", callback_data="finish_purchasing")]
                    ])
                )
        except ValueError:
            logger.error(f"❌ Неправильний формат ID товару: {item}")

        await query.answer()
        return


    # Видалення товару з бази даних
    try:
        product_id = int(item)
        print(f"✅ Натиснуто видалення товару з ID: {product_id}")
        mark_product_as_deleted(product_id)
        logger.info(f"Товар з ID {product_id} видалено у чаті {chat_id}.")

        # Оновлення списку після видалення
        products = get_active_products_by_chat(chat_id)
        if products:
            keyboard = [
                [InlineKeyboardButton(f"{product[1]}", callback_data=str(product[0]))]
                for product in products
            ]
            keyboard.append([InlineKeyboardButton("Завершити видалення", callback_data="finish_editing")])
            full_list = "\n".join([f"{product[1]}" for product in products])

            await query.edit_message_text(
                text=f"Оберіть товар для видалення:",
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
