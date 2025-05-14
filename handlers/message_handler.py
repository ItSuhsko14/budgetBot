from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from data.chat_data import chat_data
from utils.logger import logger
from data.db_service import (
    add_product, 
    get_active_products_by_chat,
    get_products_by_ids,
    mark_product_as_deleted, 
    mark_product_as_purchased, 
    add_expense
)
from utils.initialize_chat import initialize_chat
from button.delete_mode import create_delete_keyboard


async def make_list_editable(chat_id, context):
    products = get_active_products_by_chat(chat_id)

    if products:
        keyboard = [[InlineKeyboardButton(f"{product[1]}", callback_data=f"mark_delete:{product[0]}")] for product in products]
        keyboard.append([InlineKeyboardButton("Завершити видалення", callback_data="finish_editing")])

        full_list = "\n".join([f"{product[1]}" for product in products])
        msg = await context.bot.send_message(
            chat_id,
            f"Оберіть товар для видалення:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        chat_data[chat_id]['ephemeral_messages'].append(msg.message_id)
    else:
        msg = await context.bot.send_message(chat_id, "Ваш список покупок порожній!")
        chat_data[chat_id]['ephemeral_messages'].append(msg.message_id)


async def make_list_purchasable(chat_id, context):
    products = get_active_products_by_chat(chat_id)

    if products:
        chat_data[chat_id]['purchase_mode'] = True

        keyboard = [[InlineKeyboardButton(f"{product[1]}", callback_data=str(product[0]))] for product in products]
        keyboard.append([InlineKeyboardButton("Завершити вибір товарів", callback_data="finish_purchasing")])

        full_list = "\n".join([f"{product[1]}" for product in products])

        msg = await context.bot.send_message(
            chat_id,
            f"Оберіть товари для позначення купленими:\n\nТОВАРИ ДЛЯ ПОКУПКИ:\n{full_list}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        chat_data[chat_id]['ephemeral_messages'].append(msg.message_id)
    else:
        msg = await context.bot.send_message(chat_id, "Ваш список покупок порожній!")
        chat_data[chat_id]['ephemeral_messages'].append(msg.message_id)


async def cleanup_ephemeral_messages(chat_id, context: CallbackContext):
    for msg_id in chat_data[chat_id]['ephemeral_messages']:
        try:
            await context.bot.delete_message(chat_id, msg_id)
        except Exception as e:
            logger.error(f"Не вдалося видалити повідомлення {msg_id}: {e}")
    chat_data[chat_id]['ephemeral_messages'] = []


async def handle_message(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_text = update.message.text

    print(f"Отримано повідомлення від користувача: {user_text}")

    initialize_chat(chat_id)

    if chat_data[chat_id]['awaiting_cost']:
        try:
            cost = float(user_text)
            product_ids = set(chat_data[chat_id]['purchased_items'])  # IDs куплених товарів
            category = "Покупки"

            # Додавання витрати в базу даних
            add_expense(amount=cost, category=category, product_ids=list(product_ids), chat_id=chat_id)

            # Отримання назв товарів з бази даних за ID
            purchased_products = get_products_by_ids(product_ids)
            purchased_names = [product[1] for product in purchased_products if product[1]]

            # Формування списку куплених товарів
            purchased_list = "\n".join(purchased_names) if purchased_names else "порожній"
            text = f"Куплені товари:\n{purchased_list}\nВартість: {cost:.2f}"

            # Оновлення або створення повідомлення
            if chat_data[chat_id].get('purchased_message_id'):
                try:
                    await context.bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=chat_data[chat_id]['purchased_message_id'],
                        text=text
                    )
                except Exception as e:
                    logger.error(f"Не вдалося оновити повідомлення: {e}")
            else:
                sent = await context.bot.send_message(chat_id, text)
                chat_data[chat_id]['purchased_message_id'] = sent.message_id

            # Очищення після завершення купівлі
            chat_data[chat_id]['awaiting_cost'] = False
            chat_data[chat_id]['purchased_items'].clear()
            return

        except ValueError:
            await context.bot.send_message(chat_id, "Введіть правильну числову суму.")
            return

    if user_text == "Додати товар":
        if chat_data[chat_id].get('prompt_message_id'):
            try:
                await context.bot.delete_message(chat_id=chat_id, message_id=chat_data[chat_id]['prompt_message_id'])
            except Exception as e:
                logger.error(f"Не вдалося видалити повідомлення 'Введіть товар': {e}")

        # Створюємо нове повідомлення "Введіть товар"
        sent_message = await context.bot.send_message(chat_id, "Введіть товар:")
        chat_data[chat_id]['prompt_message_id'] = sent_message.message_id


    elif user_text == "Видалити товар":
        await cleanup_ephemeral_messages(chat_id, context)
        await create_delete_keyboard(chat_id, context)

    elif user_text == "Позначити купленими":
        await cleanup_ephemeral_messages(chat_id, context)
        await make_list_purchasable(chat_id, context)

    elif 'list_items' in chat_data[chat_id]:
        chat_data[chat_id]['list_items'].append(user_text)
        logger.info(f"Товар додано у чат {chat_id}: {user_text}")

        # Додаємо товар у базу даних
        add_product(chat_id, user_text, "Категорія за замовчуванням")

        # Отримуємо всі активні товари з бази
        products = get_active_products_by_chat(chat_id)

        if products:
            full_list = "\n".join([f"{product[1]}" for product in products])
        else:
            full_list = "Список покупок порожній!"

        # Видаляємо старе повідомлення, якщо воно існує
        if chat_data[chat_id].get('list_message_id'):
            try:
                await context.bot.delete_message(chat_id=chat_id, message_id=chat_data[chat_id]['list_message_id'])
            except Exception as e:
                logger.error(f"Не вдалося видалити повідомлення: {e}")

        # Створюємо нове повідомлення зі списком товарів
        sent_message = await context.bot.send_message(chat_id, f"ТОВАРИ ДЛЯ ПОКУПКИ:\n{full_list}")
        chat_data[chat_id]['list_message_id'] = sent_message.message_id

        # Видаляємо всі старі повідомлення "Введіть товар"
        if chat_data[chat_id].get('prompt_message_id'):
            try:
                await context.bot.delete_message(chat_id=chat_id, message_id=chat_data[chat_id]['prompt_message_id'])
            except Exception as e:
                logger.error(f"Не вдалося видалити повідомлення 'Введіть товар': {e}")

        # Створюємо нове повідомлення "Введіть товар"
        new_prompt_message = await context.bot.send_message(chat_id, "Введіть товар:")
        chat_data[chat_id]['prompt_message_id'] = new_prompt_message.message_id
