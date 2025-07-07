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
        cancel_mode_awaiting_cost(chat_id)
        log(f"add_expense amount: {cost}, product_ids: {product_ids}, chat_id: {chat_id}, category: {category}")
        for product_id in product_ids:
            mark_product_as_deleted(product_id)

        # Отримання назв товарів з бази даних за ID
        purchased_products = get_products_by_ids(product_ids)
        log(f"purchased_products: {purchased_products}")
        purchased_names = [product[1] for product in purchased_products if product[1]]
        log(f"purchased_names: {purchased_names}")

        # Формування списку куплених товарів
        purchased_list = "\n • ".join(purchased_names) if purchased_names else "порожній"
        log(f"purchased_list: {purchased_list}")
        text = f"Куплені товари:\n • {purchased_list}\nВартість: {cost:.2f}"
        log(f"text: {text}")
        log(f"chat_data[chat_id]: {chat_data[chat_id]}")

        # Оновлення або створення повідомлення
        sent = await context.bot.send_message(chat_id, text)
        chat_data[chat_id]['purchased_message_id'] = sent.message_id

        # Очищення після завершення купівлі
        chat_data[chat_id]['list_items'] = get_active_products_by_chat(chat_id)
        chat_data[chat_id]['selected_items'] = []

        await delete_keyboard(chat_id, context)
        await create_keyboard(chat_id, context)
        cancel_mode_awaiting_cost(chat_id)
        return
    except ValueError as e:
        log(f"Помилка в handle_awaiting_cost: Введено неправильну числову суму. Error: {e}")
        await context.bot.send_message(chat_id=chat_id, text="Будь ласка, введіть коректну суму у форматі числа (наприклад, 100 або 50.50)")
        return
    except Exception as e:
        log(f"Неочікувана помилка в handle_awaiting_cost: {e}")
        await context.bot.send_message(chat_id=chat_id, text="Сталася неочікувана помилка. Будь ласка, спробуйте ще раз.")
        return