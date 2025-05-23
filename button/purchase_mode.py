# button/purchase_mode.py

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext
from data.chat_data import chat_data
from data.db_service import get_products_by_ids, get_active_products_by_chat, mark_product_as_purchased
# from handlers.message_handler import cleanup_ephemeral_messages
from utils.logger import log

async def handle_purchasing(update: Update, context: CallbackContext):
    query = update.callback_query
    chat_id = query.message.chat_id
    item = query.data
    action, product_id = item.split(":", 1)

    # Ініціалізуємо список куплених товарів
    if 'purchased_items' not in chat_data[chat_id]:
        chat_data[chat_id]['purchased_items'] = []

    # Міняємо статус товара
    if action == "mark_purchased":
        await mark_purchased(chat_id, product_id)
    elif action == "unmark_purchased":
        await unmark_purchased(chat_data[chat_id], product_id)

    # Оновити клавіатуру
    await update_purchasing_keyboard(chat_id, context)

async def update_purchasing_keyboard(chat_id, context):
    keyboard = build_purchasing_keyboard(chat_id)
    
    try:
        await context.bot.edit_message_reply_markup(
            chat_id=chat_id, 
            message_id=chat_data[chat_id]['purchase_message_id'], 
            reply_markup=keyboard
        )
    except Exception as e:
        log(f"Помилка при оновленні клавіатури: {str(e)}")

async def create_purchasing_keyboard(chat_id, context):
    print("✅ Створюємо клавіатуру для вибору товарів") 
    keyboard = build_purchasing_keyboard(chat_id)
    
    sent = await context.bot.send_message(chat_id, "Оберіть товар для видалення:", reply_markup=keyboard)
    chat_data[chat_id]['purchase_message_id'] = sent.message_id

def build_purchasing_keyboard(chat_id):
    products = get_active_products_by_chat(chat_id)
    marked_ids = set(chat_data[chat_id].get('purchased_items', []))
    
    keyboard = []

    for product in products:
        product_id = str(product[0])
        product_name = product[1]

        if product_id in marked_ids:
            keyboard.append([
                InlineKeyboardButton(f"✅ {product_name}", callback_data=f"unmark_purchased:{product_id}")
            ])
        else:
            keyboard.append([
                InlineKeyboardButton(product_name, callback_data=f"mark_purchased:{product_id}")
            ])

    keyboard.append([
        InlineKeyboardButton("✅ Завершити покупку", callback_data="finish_purchasing")
    ])
    

    return InlineKeyboardMarkup(keyboard)

    keyboard = []

    for product in products:
        product_id = str(product[0])
        product_name = product[1]

        if product_id in marked_ids:
            keyboard.append([
                InlineKeyboardButton(f"✅ {product_name}", callback_data=f"unmark_purchased:{product_id}")
            ])
        else:
            keyboard.append([
                InlineKeyboardButton(product_name, callback_data=f"mark_purchased:{product_id}")
            ])

    keyboard.append([
        InlineKeyboardButton("✅ Завершити покупку", callback_data="finish_purchasing")
    ])

    return InlineKeyboardMarkup(keyboard)


async def finalize_purchasing(update: Update, context: CallbackContext):
    # взяти список виділених товарів
    # вивести повідомлення про очікування суми
    # якщо сумма введена - викликати add_expense
    print("finilize_purchasing")

async def mark_purchased(chat_id: int, product_id: str):
    if product_id not in chat_data[chat_id]['purchased_items']:
        chat_data[chat_id]['purchased_items'].append(product_id)
    print(f"✅ Позначено товар {product_id} як куплений")

async def unmark_purchased(chat_data, product_id):
    if product_id in chat_data['purchased_items']:
        chat_data['purchased_items'].remove(product_id)
    print(f"✅ Знято позначку з товару {product_id}")

#     chat_data[chat_id]['purchase_mode'] = False
#     purchased_product_ids = set(chat_data[chat_id]['purchased_items'])
#     purchased_products = get_products_by_ids(purchased_product_ids)
#     purchased_names = [product[1] for product in purchased_products]
#     purchased_list = "\n".join(purchased_names) if purchased_names else "порожній"

#     text = f"Ви обрали наступні товари як куплені:\n{purchased_list}\nВведіть вартість цих товарів:"
#     await cleanup_ephemeral_messages(chat_id, context)
#     sent = await context.bot.send_message(chat_id, text)
#     chat_data[chat_id]['purchased_message_id'] = sent.message_id
#     chat_data[chat_id]['awaiting_cost'] = True
#     await query.answer()


# async def mark_purchased(update, context: CallbackContext):
#     query = update.callback_query
#     chat_id = query.message.chat_id
#     item = query.data

#     try:
#         product_id = int(item)
#         mark_product_as_purchased(product_id)
#         logger.info(f"✅ Товар з ID {product_id} позначено як 'purchased'.")

#         chat_data[chat_id]['list_items'] = [
#             i for i in chat_data[chat_id]['list_items'] if str(i) != str(product_id)
#         ]
#         chat_data[chat_id]['purchased_items'].append(str(product_id))

#         products = get_active_products_by_chat(chat_id)

#         if products:
#             keyboard = [[InlineKeyboardButton(f"{product[1]}", callback_data=str(product[0]))]
#                         for product in products]
#             keyboard.append([InlineKeyboardButton("Завершити вибір товарів", callback_data="finish_purchasing")])
#             await query.edit_message_text(
#                 text=f"Оберіть товари для позначення купленими:\n\n",
#                 reply_markup=InlineKeyboardMarkup(keyboard)
#             )
#         else:
#             await query.edit_message_text(
#                 text="Список покупок порожній!",
#                 reply_markup=InlineKeyboardMarkup([
#                     [InlineKeyboardButton("Завершити вибір товарів", callback_data="finish_purchasing")]
#                 ])
#             )

#     except ValueError:
#         logger.error(f"❌ Неправильний формат ID товару: {item}")

#     await query.answer()