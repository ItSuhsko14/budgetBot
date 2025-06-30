from utils.logger import log
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from data.chat_data import chat_data
from telegram import ReplyKeyboardRemove
from telegram.ext import ContextTypes
from telegram.error import BadRequest

def createOneProductButton(product, chat_id):
        if product[0] in chat_data[chat_id].get('selected_items', []):
            log(f"{product[0], product[1]} позначено виділеним")
            return InlineKeyboardButton(f"✅ {product[1]}", callback_data=f"unselect:{product[0]}")
        else:
            return InlineKeyboardButton(product[1], callback_data=f"select:{product[0]}")

def createProductGroupButtons(products, chat_id):
    return [[createOneProductButton(product, chat_id)] for product in products]

def createOneCategoryButton(category, chat_id):
    if str(category[0]) in chat_data[chat_id].get('selected_categories', []):
        log(f"{category[0], category[1]} позначено виділеним")
        wide_button = InlineKeyboardButton(f"✅ --- {category[1]}", callback_data=f"unselect_category:{category[0]}")
    else:
        wide_button = InlineKeyboardButton(f"--- {category[1]}", callback_data=f"select_category:{category[0]}")
    add_btn = InlineKeyboardButton("➕ додати товар", callback_data=f"add_product_with_category:{category[0]}")
    
    return [wide_button, add_btn]

async def create_keyboard_keys(chat_id):
    products = chat_data[chat_id]['list_items']
    categories = chat_data[chat_id]['categories']
    buttons = []

    for category in categories:
        buttons.append(createOneCategoryButton(category, chat_id))
        category_products = []
        for p in products:
            try:
                if p[2] is not None and p[2] and p[2] == category[0]:
                    category_products.append(p)
            except (ValueError, TypeError):
                continue
        product_buttons = createProductGroupButtons(category_products, chat_id)
        buttons.extend(product_buttons)
    
    existing_category_ids = {c[0] for c in categories}

    without_category_products = []
    for product in products:
        if product[2] is None or product[2] not in existing_category_ids:
            without_category_products.append(product)

    without_category_products_group = createProductGroupButtons(without_category_products, chat_id)
    if (len(without_category_products) > 0):
        buttons.append([InlineKeyboardButton("--- Без категорії", callback_data="no_category"), InlineKeyboardButton("➕ Додати товар", callback_data="add_product")])
    buttons.extend(without_category_products_group)
    
    # Додаємо кнопки дій
    # separator = InlineKeyboardButton(" ", callback_data="noop")
    action_buttons = [
        [InlineKeyboardButton("➕ Додати товар", callback_data="add_product"),
        InlineKeyboardButton("❌ Видалити товар", callback_data="finish_deleting")],
        [InlineKeyboardButton("➕ Додати категорію", callback_data="add_category"),
        InlineKeyboardButton("❌ Видалити категорію", callback_data="delete_category")],
        [InlineKeyboardButton("✅ Позначити купленими", callback_data="finish_purchasing")],
    ]
    return InlineKeyboardMarkup(buttons + action_buttons)

async def create_keyboard(chat_id, context=None):
    # Обʼєднуємо все в одну клавіатуру
    full_keyboard = await create_keyboard_keys(chat_id)

    # Надсилаємо повідомлення
    keyboard_message = await context.bot.send_message(chat_id, "Ваш список товарів:", reply_markup=full_keyboard)
    
    chat_data[chat_id]['keyboard_message_id'] = keyboard_message.message_id
    return keyboard_message

async def update_keyboard(chat_id, context):
    if chat_id not in chat_data or 'keyboard_message_id' not in chat_data[chat_id]:
        log("Повідомлення з клавіатурою не знайдено")
        return

    new_keyboard = await create_keyboard_keys(chat_id)
    message_text = "Ваш список товарів:"
    
    # Оновлюємо клавіатуру
    keyboard_message_id = chat_data[chat_id]['keyboard_message_id']
    try:
        await context.bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=keyboard_message_id,
            reply_markup=new_keyboard
        )
        log("Клавіатура успішно оновлена")
    except BadRequest as e:
        if "Message is not modified" in str(e):
            log("Клавіатура вже оновлена")
        else:
            log(f"Помилка при оновленні клавіатури: {e}")
    except Exception as e:
        log(f"Невідома помилка при оновленні клавіатури: {e}")

async def delete_keyboard(chat_id, context):
    if 'keyboard_message_id' in chat_data[chat_id] and chat_data[chat_id]['keyboard_message_id'] is not None:
        try:
            keyboard_message_id = chat_data[chat_id]['keyboard_message_id']
            await context.bot.delete_message(chat_id=chat_id, message_id=keyboard_message_id)
        except Exception as e:
            log(f"Не вдалося видалити клавіатуру: {e}")
        finally:
            chat_data[chat_id]['keyboard_message_id'] = None

async def remove_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        log("Видаляю клавіатуру...")
    except Exception as e:
        log(f"Не вдалося видалити клавіатуру: {e}")