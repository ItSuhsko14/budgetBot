from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext
from data.db_service import mark_product_as_deleted
from data.db_service import get_active_products_by_chat
from utils.logger import logger
from data.chat_data import chat_data


async def handle_delete_product(update: Update, context: CallbackContext):
    query = update.callback_query
    chat_id = query.message.chat_id
    item = query.data
    action, product_id = item.split(":", 1)

    # Ініціалізуємо список видалених товарів, якщо він ще не існує
    removed = chat_data[chat_id].setdefault('removed_items', [])

    if action == "mark_delete":
        mark_for_deletion(chat_id, product_id)
    elif action == "unmark_delete":
        unmark_for_deletion(chat_id, product_id)

    # Оновити клавіатуру
    await update_delete_keyboard(chat_id)

def mark_for_deletion(chat_id, product_id):
    if product_id not in chat_data[chat_id]['removed_items']:
        chat_data[chat_id]['removed_items'].append(product_id)

    if 'list_items' in chat_data[chat_id]:
        chat_data[chat_id]['list_items'] = [
            i for i in chat_data[chat_id]['list_items'] if str(i) != str(product_id)
        ]

def unmark_for_deletion(chat_id, product_id):
    if product_id in chat_data[chat_id]['removed_items']:
        chat_data[chat_id]['removed_items'].remove(product_id)

    if 'list_items' in chat_data[chat_id]:
        chat_data[chat_id]['list_items'].append(product_id)

def build_delete_keyboard(chat_id):
    products = get_active_products_by_chat(chat_id)
    marked_ids = set(chat_data[chat_id].get('removed_items', []))

    keyboard = []

    for product in products:
        product_id = str(product[0])
        product_name = product[1]

        if product_id in marked_ids:
            keyboard.append([
                InlineKeyboardButton(f"❌ {product_name}", callback_data=f"unmark_delete:{product_id}")
            ])
        else:
            keyboard.append([
                InlineKeyboardButton(product_name, callback_data=f"mark_delete:{product_id}")
            ])

    keyboard.append([
        InlineKeyboardButton("✅ Видалити", callback_data="finish_deleting")
    ])

    return InlineKeyboardMarkup(keyboard)

async def create_delete_keyboard(chat_id, context):
    keyboard = build_delete_keyboard(chat_id)
    
    sent = await context.bot.send_message(chat_id, "Оберіть товар для видалення:", reply_markup=keyboard)
    chat_data[chat_id]['delete_message_id'] = sent.message_id

async def update_delete_keyboard(chat_id):
    keyboard = build_delete_keyboard(chat_id)

    await context.bot.edit_message_reply_markup(chat_id=chat_id, message_id=chat_data[chat_id]['delete_message_id'], reply_markup=keyboard)

async def finish_deleting(update: Update, context: CallbackContext):
    query = update.callback_query
    chat_id = query.message.chat_id

    removed_ids = chat_data[chat_id].get('removed_items', [])
    if removed_ids:
        for product_id in removed_ids:
            logger.info(f"✅ Товар з ID {product_id} позначено як 'deleted'.")
            mark_product_as_deleted(product_id)
        chat_data[chat_id]['removed_items'] = []

    # 🧹 Видалення повідомлення з клавіатурою
    try:
        message_id = chat_data[chat_id].get('delete_message_id')
        if message_id:
            await context.bot.delete_message(chat_id, message_id)
            chat_data[chat_id].pop('delete_message_id', None)
    except Exception as e:
        logger.warning(f"⚠️ Не вдалося видалити повідомлення: {e}")

    # 📋 Вивід нового списку товарів
    products = get_active_products_by_chat(chat_id)
    if products:
        product_list = "\n".join([f"{product[1]}" for product in products])
        response_text = f"Доступні товари для покупки:\n{product_list}"
    else:
        response_text = "Список товарів порожній."

    await context.bot.send_message(chat_id, response_text)
    await query.answer("Видалення завершено.")
    