from utils.logger import log
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from data.chat_data import chat_data

async def create_keyboard_keys(chat_id):
    products = chat_data[chat_id]['list_items']
    log(f"\nProducts: {products}")

    def createOneProductButton(product):
        if str(product[0]) in chat_data[chat_id].get('selected_items', []):
            return InlineKeyboardButton(f"✅ {product[1]}", callback_data=f"unselect:{product[0]}")
        else:
            return InlineKeyboardButton(product[1], callback_data=f"select:{product[0]}")

    # Створюємо список кнопок товарів
    product_buttons = [[createOneProductButton(product)] for product in products]

    # Додаємо кнопки дій
    separator = InlineKeyboardButton(" ", callback_data="noop")
    action_buttons = [
        [separator],
        [InlineKeyboardButton("➕ Додати товар", callback_data="add_product")],
        [InlineKeyboardButton("❌ Видалити товар", callback_data="finish_deleting")],
        [InlineKeyboardButton("✅ Позначити купленими", callback_data="finish_purchasing")]
    ]

    return InlineKeyboardMarkup(product_buttons + action_buttons)

async def create_keyboard(chat_id, update, context=None):
    # Обʼєднуємо все в одну клавіатуру
    full_keyboard = await create_keyboard_keys(chat_id)

    # Надсилаємо повідомлення
    if context is None:
        # Якщо викликано з start_handler
        keyboard_message = await update.message.reply_text("Ваш список товарів:", reply_markup=full_keyboard)
    else:
        # Якщо викликано з message_handler
        keyboard_message = await context.bot.send_message(chat_id, "Ваш список товарів:", reply_markup=full_keyboard)
    
    chat_data[chat_id]['keyboard_message_id'] = keyboard_message.message_id
    return keyboard_message

async def update_keyboard(chat_id, context):
    full_keyboard = await create_keyboard_keys(chat_id)
    keyboard_message_id = chat_data[chat_id]['keyboard_message_id']
    await context.bot.edit_message_reply_markup(chat_id=chat_id, message_id=keyboard_message_id, reply_markup=full_keyboard)

async def delete_keyboard(chat_id, context):
    if 'keyboard_message_id' in chat_data[chat_id] and chat_data[chat_id]['keyboard_message_id'] is not None:
        try:
            keyboard_message_id = chat_data[chat_id]['keyboard_message_id']
            await context.bot.delete_message(chat_id=chat_id, message_id=keyboard_message_id)
        except Exception as e:
            log(f"Не вдалося видалити клавіатуру: {e}")
        finally:
            chat_data[chat_id]['keyboard_message_id'] = None