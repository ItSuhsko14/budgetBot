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
    rows = []
    current_row = []
    current_length = 0
    max_row_length = 30  # Можна регулювати

    for product in products:
        btn = createOneProductButton(product, chat_id)
        btn_length = len(btn.text)

        if current_length + btn_length > max_row_length and current_row:
            rows.append(current_row)
            current_row = [btn]
            current_length = btn_length
        else:
            current_row.append(btn)
            current_length += btn_length

    if current_row:
        rows.append(current_row)

    return rows

def createOneCategoryButton(category, chat_id):
    if str(category[0]) in chat_data[chat_id].get('selected_categories', []):
        log(f"{category[0], category[1]} позначено виділеним")
        wide_button = InlineKeyboardButton(f"✅ --- {category[1]} ---", callback_data=f"unselect_category:{category[0]}")
    else:
        wide_button = InlineKeyboardButton(f"--- {category[1]} ---", callback_data=f"select_category:{category[0]}")
    add_btn = InlineKeyboardButton("➕ Додати товар", callback_data=f"add_product_with_category:{category[0]}")
    
    return [wide_button, add_btn]

def create_hide_empty_category_button(chat_id):
    if chat_data[chat_id]['hide_empty_category']:
        return [[InlineKeyboardButton("➕ Показати порожні категорії", callback_data="show_category")]]
    else:
        return [[InlineKeyboardButton("➕ Сховати порожні категорії", callback_data="hide_category")]]

async def create_keyboard_keys(chat_id):
    products = chat_data[chat_id]['list_items']
    categories = chat_data[chat_id]['categories']
    buttons = []

    for category in categories:
        category_products = []
        for p in products:
            try:
                if p[2] is not None and p[2] and p[2] == category[0]:
                    category_products.append(p)
            except (ValueError, TypeError, IndexError):
                continue
        
        show_category = not chat_data[chat_id]['hide_empty_category'] or len(category_products) > 0
        if show_category:
            buttons.append(createOneCategoryButton(category, chat_id))
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
        [InlineKeyboardButton("✅ Позначити купленими", callback_data="finish_purchasing"),
        InlineKeyboardButton("❌ Видалити товар", callback_data="finish_deleting")],
        [InlineKeyboardButton("➕ Додати категорію", callback_data="add_category"),
        InlineKeyboardButton("❌ Видалити категорію", callback_data="delete_category")],
        [InlineKeyboardButton("📊 Показати витрати за місяць", callback_data="show_expenses"),
        InlineKeyboardButton("ℹ️ Довідка", callback_data="info")]
    ]
    hide_empty_category_button = create_hide_empty_category_button(chat_id)
    return InlineKeyboardMarkup(buttons + action_buttons + hide_empty_category_button)

async def create_keyboard(chat_id, context=None):
    # Обʼєднуємо все в одну клавіатуру
    full_keyboard = await create_keyboard_keys(chat_id)

    # Надсилаємо повідомлення
    keyboard_message = await context.bot.send_message(chat_id, "Список продуктів", reply_markup=full_keyboard)
    
    chat_data[chat_id]['keyboard_message_id'] = keyboard_message.message_id
    return keyboard_message

async def update_keyboard(chat_id, context):
    if chat_id not in chat_data or 'keyboard_message_id' not in chat_data[chat_id]:
        log("Повідомлення з клавіатурою не знайдено")
        return

    new_keyboard = await create_keyboard_keys(chat_id)
    
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