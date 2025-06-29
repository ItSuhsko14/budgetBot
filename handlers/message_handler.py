from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from data.chat_data import chat_data
from utils.logger import log
from data.db_service import (
    add_product, 
    get_active_products_by_chat,
    get_products_by_ids,
    mark_product_as_deleted, 
    add_expense
)
from utils.initialize_chat import initialize_chat
from utils.keyboard import delete_keyboard, create_keyboard, create_category_keyboard
from utils.product_text_handler import split_text_to_items
from utils.image_recognition import classify_image_from_telegram
from data.db_service import get_all_categories, create_category
from button.purchase_mode import handle_awaiting_cost


async def prompt_add_product(chat_id, context):
    """Функція для виведення повідомлення 'Введіть товар'"""
    if chat_data[chat_id].get('prompt_message_id'):
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=chat_data[chat_id]['prompt_message_id'])
        except Exception as e:
            log(f"Не вдалося видалити повідомлення 'Введіть товар': {e}")

    # Створюємо нове повідомлення "Введіть товар"
    sent_message = await context.bot.send_message(chat_id, "Введіть товар:")
    chat_data[chat_id]['prompt_message_id'] = sent_message.message_id

async def add_product_to_chat(chat_id, product_name, category=None):
    """Додає товар у базу даних та оновлює список товарів у чаті"""
    product_id = add_product(chat_id, product_name, category)
    if product_id:
        products = get_active_products_by_chat(chat_id)
        chat_data[chat_id]['list_items'] = products
        return True
    return False

async def add_products_from_text(chat_id, text, context, category=None):
    """Додає товари з тексту у базу даних та оновлює інтерфейс"""
    # Розділяємо текст на окремі товари
    products_list = split_text_to_items(text)
    
    for product_name in products_list:
        # Додаємо кожен товар у базу даних
        add_product(chat_id, product_name, category)
        log(f"Товар додано у чат {chat_id}: {product_name}, category: {category}")
    
    # Оновлюємо список товарів у пам'яті
    products = get_active_products_by_chat(chat_id)
    chat_data[chat_id]['list_items'] = products
    
    # Оновлюємо інтерфейс
    await delete_keyboard(chat_id, context)
    await create_keyboard(chat_id, context)

async def handle_message(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    initialize_chat(chat_id)

    if update.message.photo:
        log(f"Отримано зображення від користувача: {update.message.photo}")
        try:
            # Беремо найбільше доступне зображення (останнє в масиві)
            photo = update.message.photo[-1]
            # Викликаємо функцію розпізнавання зображення
            result = await classify_image_from_telegram(context.bot, photo.file_id)
            await add_products_from_text(chat_id, result, context)
            
        except Exception as e:
            log(f"Помилка при обробці зображення: {e}")
            await update.message.reply_text("❌ Не вдалося обробити зображення. Спробуйте ще раз.")
        return

    # Якщо це не зображення, перевіряємо чи це текст
    if not update.message.text:
        await update.message.reply_text("Будь ласка, надішліть текст або зображення.")
        return
    user_text = update.message.text

    print(f"Отримано повідомлення від користувача: {user_text}")

    

    if chat_data[chat_id].get('awaiting_category_name'):
        # Обробка введення назви категорії
        category_name = user_text.strip()
        if category_name:
            log(f"category_name: {category_name}")
            # Створюємо категорію в базі даних
            result = create_category(chat_id, category_name)
            log(f"result: {result}")
            categories = get_all_categories(chat_id)
            chat_data[chat_id]['categories'] = categories
            await delete_keyboard(chat_id, context)
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"✅ Категорію '{category_name}' успішно створено!"
            )
            await create_category_keyboard(chat_id, context)
            # Повідомляємо про успішне створення
            
            
            # Скидаємо стан очікування
            chat_data[chat_id]['awaiting_category_name'] = False
            return
        else:
            await context.bot.send_message(
                chat_id=chat_id,
                text="❌ Назва категорії не може бути порожньою. Спробуйте ще раз:"
            )
            return
            
    if chat_data[chat_id]['awaiting_cost']:
        await handle_awaiting_cost(chat_id, context, user_text)
        return

    elif 'list_items' in chat_data[chat_id]:
        category_mode = chat_data[chat_id].get('category_mode', False)
        log(f"category_mode: {category_mode}")
        if not chat_data[chat_id].get('category_mode'):
            category_id = chat_data[chat_id]['current_category']
            log(f"category_id: {category_id}")
            await add_products_from_text(chat_id, user_text, context, category_id)
            chat_data[chat_id]['current_category'] = None
