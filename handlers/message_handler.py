from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from data.chat_data import chat_data
from utils.logger import logger
from data.db_service import add_product, get_active_products_by_chat, mark_product_as_deleted


async def make_list_editable(chat_id, context):
    products = get_active_products_by_chat(chat_id)
    
    if products:
        # Формування клавіатури на основі даних з БД
        keyboard = [[InlineKeyboardButton(f"{product[1]} ({product[2]})", callback_data=str(product[0]))] for product in products]
        keyboard.append([InlineKeyboardButton("Завершити видалення", callback_data="finish_editing")])

        full_list = "\n".join([f"{product[1]} - {product[2]}" for product in products])
        msg = await context.bot.send_message(
            chat_id,
            f"Оберіть товар для видалення:\n\nСписок покупок:\n{full_list}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        chat_data[chat_id]['ephemeral_messages'].append(msg.message_id)
    else:
        msg = await context.bot.send_message(chat_id, "Ваш список покупок порожній!")
        chat_data[chat_id]['ephemeral_messages'].append(msg.message_id)

async def make_list_purchasable(chat_id, context):
    chat_data[chat_id]['purchase_mode'] = True
    if chat_data[chat_id]['list_items']:
        keyboard = [[InlineKeyboardButton(item, callback_data=item)] for item in chat_data[chat_id]['list_items']]
        keyboard.append([InlineKeyboardButton("завершити вибір товарів", callback_data="finish_purchasing")])
        full_list = "\n".join(chat_data[chat_id]['list_items'])
        msg = await context.bot.send_message(
            chat_id,
            f"Оберіть товари для позначення купленими:\n\nСписок покупок:\n{full_list}",
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

    # Додаємо логування повідомлення користувача
    print(f"Отримано повідомлення від користувача: {user_text}")

    if chat_id not in chat_data:
        chat_data[chat_id] = {
            'list_items': [],
            'removed_items': [],
            'purchased_items': [],
            'list_message_id': None,
            'purchase_mode': False,
            'awaiting_cost': False,
            'purchased_message_id': None,
            'ephemeral_messages': []
        }

    if chat_data[chat_id]['awaiting_cost']:
        cost = user_text
        chat_data[chat_id]['awaiting_cost'] = False

        purchased_list = "\n".join(chat_data[chat_id]['purchased_items']) if chat_data[chat_id]['purchased_items'] else "порожній"
        text = f"Куплені товари:\n{purchased_list}\nВартість: {cost}"

        if chat_data[chat_id]['purchased_message_id']:
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=chat_data[chat_id]['purchased_message_id'],
                text=text
            )
        else:
            sent = await context.bot.send_message(chat_id, text)
            chat_data[chat_id]['purchased_message_id'] = sent.message_id

        await cleanup_ephemeral_messages(chat_id, context)

        if chat_data[chat_id]['list_message_id']:
            try:
                await context.bot.delete_message(chat_id, chat_data[chat_id]['list_message_id'])
            except Exception as e:
                logger.error(f"Не вдалося видалити старе повідомлення зі списком: {e}")
            chat_data[chat_id]['list_message_id'] = None

        full_list = "\n".join(chat_data[chat_id]['list_items']) if chat_data[chat_id]['list_items'] else "порожній"
        sent_message = await context.bot.send_message(chat_id, f"Список покупок:\n{full_list}")
        chat_data[chat_id]['list_message_id'] = sent_message.message_id

        return

    if user_text == "Додати товар":
        await context.bot.send_message(chat_id, "Введіть товар:")

    elif user_text == "Видалити товар":
        await cleanup_ephemeral_messages(chat_id, context)
        await make_list_editable(chat_id, context)

    elif user_text == "Позначити купленими":
        await cleanup_ephemeral_messages(chat_id, context)
        await make_list_purchasable(chat_id, context)

    elif 'list_items' in chat_data[chat_id]:
        chat_data[chat_id]['list_items'].append(user_text)
        logger.info(f"Товар додано у чат {chat_id}: {user_text}")

        add_product(chat_id, user_text, "Категорія за замовчуванням")

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
