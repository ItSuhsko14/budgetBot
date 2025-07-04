from operator import truediv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from utils.logger import log
from data.db_service import create_category, delete_category_from_db, get_all_categories
from utils.keyboard import create_keyboard, update_keyboard, delete_keyboard
from data.chat_data import chat_data
from utils.message import write_message

async def add_category(chat_id, context):
    log(f"Запит на додавання категорії")
    # Встановлюємо стан очікування назви категорії
    chat_data[chat_id]['awaiting_category_name'] = True
    
    # Відправляємо запит на введення назви категорії
    await context.bot.send_message(
        chat_id=chat_id,
        text="Введіть назву нової категорії:"
    )

def exist_products_with_category(chat_id, category_id):
    try:
        category_id = int(category_id)
    except ValueError:
        log(f"❌ Помилка в exist_products_with_category: Неможливо привести category_id до числа: {category_id}")
        return False
    
    products = chat_data[chat_id]['list_items']
    for product in products:
        if product[2] == category_id:
            return True
    return False

async def delete_category(chat_id, context):
    selected_categories = chat_data[chat_id]['selected_categories']
    for category_id in selected_categories:
        if exist_products_with_category(chat_id, category_id):
            await write_message(chat_id, f"Категорія не видалена. Спочатку видаліть всі товари з цієї категорії", context)
        else:
            delete_category_from_db(chat_id, category_id)

    chat_data[chat_id]['selected_categories'] = []
    actual_categories = get_all_categories(chat_id)
    log(f"✅ actual_categories: {actual_categories}")
    chat_data[chat_id]['categories'] = actual_categories
    await update_keyboard(chat_id, context)

async def select_category(chat_id, context, category_id):
    chat_data[chat_id]['selected_categories'].append(category_id)

async def unselect_category(chat_id, context, category_id):
    chat_data[chat_id]['selected_categories'].remove(category_id)    