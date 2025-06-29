from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from utils.logger import log
from handlers.message_handler import prompt_add_product
from button.delete_mode import finish_deleting
from button.purchase_mode import finalize_purchasing
from utils.initialize_chat import initialize_chat
from button.select import select_product, unselect_product
from button.category_handler import select_category, unselect_category
from utils.keyboard import update_keyboard
from button.category_handler import add_category, delete_category, show_all_categories, category_mode, back_to_products
from button.product_handler import add_product_with_category

hadler_config = {
    "finish_deleting": finish_deleting,
    "finish_purchasing": finalize_purchasing,
    "add_product": prompt_add_product,
    "select": select_product,
    "unselect": unselect_product,
    "select_category": select_category,
    "unselect_category": unselect_category,
    "category_mode": category_mode,
    "add_category": add_category,
    "delete_category": delete_category,
    "show_all_categories": show_all_categories,
    "back_to_products": back_to_products,
    "add_product_with_category": add_product_with_category
}

async def button(update: Update, context: CallbackContext):
    print("✅ Натиснуто кнопку", update.callback_query.data)
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat_id
    item = query.data
    action, *params = item.split(":", 1)
    log(f"✅ Натиснуто кнопку action {action}")
    log(f"✅ params {params}")
    print('item in button_handler:', item)

    # 🛡️ Ініціалізація chat_data для нового чату
    initialize_chat(chat_id)

    handler = hadler_config.get(action)

    await handler(chat_id, context, *params)
    await update_keyboard(chat_id, context)
    return;