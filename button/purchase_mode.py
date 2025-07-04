# button/purchase_mode.py

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext
from data.chat_data import chat_data
from data.db_service import get_active_products_by_chat, add_expense, mark_product_as_deleted, get_products_by_ids
# from handlers.message_handler import cleanup_ephemeral_messages
from utils.logger import log
from utils.keyboard import create_keyboard, delete_keyboard
from utils.message import write_message

def make_mode_awaiting_cost(chat_id):
    chat_data[chat_id]['awaiting_cost'] = True

def cancel_mode_awaiting_cost(chat_id):
    chat_data[chat_id]['awaiting_cost'] = False

async def finalize_purchasing(chat_id, context: CallbackContext):
    product_ids = set(chat_data[chat_id]['selected_items'])
    log(f"finalize_purchasing product_ids: {product_ids}")
    category_ids = get_category_ids_from_product_ids(product_ids, chat_id)
    if not is_all_categories_equal(category_ids):
        await write_message(chat_id, "Виберіть товари з однієї категорії для покупки", context)
        return
    make_mode_awaiting_cost(chat_id)
    purchased_products = chat_data[chat_id]['selected_items']
    await write_message(chat_id, "Введіть суму покупки:", context)


def get_category_ids_from_product_ids(product_ids, chat_id):
    products = chat_data[chat_id]['list_items']
    category_ids = []
    for product in products:
        if product[0] in product_ids:
            category_ids.append(product[2])
    return category_ids

def is_all_categories_equal(category_ids):
    return len(set(category_ids)) < 2

async def handle_awaiting_cost(chat_id, context: CallbackContext, user_text):
    try:    
        cost = float(user_text)
        product_ids = chat_data[chat_id]['selected_items']
        category_ids = get_category_ids_from_product_ids(product_ids, chat_id)
        category = category_ids[0] if category_ids else None
        # Додавання витрати в базу даних
        add_expense(amount=cost, product_ids=list(product_ids), chat_id=chat_id, category=category)
        for product_id in product_ids:
            mark_product_as_deleted(product_id)

        # Отримання назв товарів з бази даних за ID
        purchased_products = get_products_by_ids(product_ids)
        purchased_names = [product[1] for product in purchased_products if product[1]]

        # Формування списку куплених товарів
        purchased_list = "\n • ".join(purchased_names) if purchased_names else "порожній"
        text = f"Куплені товари:\n • {purchased_list}\nВартість: {cost:.2f}"

        # Оновлення або створення повідомлення
        if chat_data[chat_id].get('purchased_message_id'):
            try:
                await context.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=chat_data[chat_id]['purchased_message_id'],
                    text=text
                )
            except Exception as e:
                log(f"Помилка в handle_awaiting_cost: Не вдалося оновити повідомлення: {e}")
                cancel_mode_awaiting_cost(chat_id)
        else:
            sent = await context.bot.send_message(chat_id, text)
            chat_data[chat_id]['purchased_message_id'] = sent.message_id

            # Очищення після завершення купівлі
            chat_data[chat_id]['list_items'] = get_active_products_by_chat(chat_id)
            chat_data[chat_id]['selected_items'] = []

            await delete_keyboard(chat_id, context)
            await create_keyboard(chat_id, context)
            cancel_mode_awaiting_cost(chat_id)
            return
    except ValueError:
        log(f"Помилка в handle_awaiting_cost: Введено неправильну числову суму.")
        await context.bot.send_message(chat_id, "Введіть правильну числову суму.")
        return