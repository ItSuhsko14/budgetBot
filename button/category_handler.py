from operator import truediv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from utils.logger import log
from data.db_service import create_category, delete_category_from_db, get_all_categories
from utils.keyboard import create_category_keyboard, create_keyboard, update_keyboard, delete_keyboard
from data.chat_data import chat_data

async def add_category(chat_id, context):
    log(f"Запит на додавання категорії")
    # Встановлюємо стан очікування назви категорії
    chat_data[chat_id]['awaiting_category_name'] = True
    
    # Відправляємо запит на введення назви категорії
    await context.bot.send_message(
        chat_id=chat_id,
        text="Введіть назву нової категорії:"
    )

async def delete_category(chat_id, context):
    log(f"✅ Видалено категорію")
    selected_categories = chat_data[chat_id]['selected_categories']
    log(f"✅ selected_categories: {selected_categories}")
    for category_id in selected_categories:
        log(f"✅ Категорія {category_id} з ID {category_id} видалена")
        delete_category_from_db(chat_id, category_id)
    chat_data[chat_id]['selected_categories'] = []
    actual_categories = get_all_categories(chat_id)
    log(f"✅ actual_categories: {actual_categories}")
    chat_data[chat_id]['categories'] = actual_categories
    await update_keyboard(chat_id, context)

async def show_all_categories(chat_id, context):
    
    try:
        chat_data[chat_id]['category_mode'] = True
        await create_category_keyboard(chat_id, context)
    except Exception as e:
        await context.bot.send_message(
            chat_id=chat_id,
            text="📭 У вас ще немає жодної категорії. Бажаєте створити нову?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("➕ Додати категорію", callback_data="add_category")],
                [InlineKeyboardButton("🔙 Назад", callback_data="back_to_products")]
            ])
        )

async def select_category(chat_id, context, category_id):
    chat_data[chat_id]['selected_categories'].append(category_id)

async def unselect_category(chat_id, context, category_id):
    chat_data[chat_id]['selected_categories'].remove(category_id)

async def category_mode(chat_id, context):
    chat_data[chat_id]["category_mode"] = True
    await create_category_keyboard(chat_id, context)

async def back_to_products(chat_id, context):
    chat_data[chat_id]["category_mode"] = False
    delete_keyboard(chat_id, context)
    await create_keyboard(chat_id, context)
    