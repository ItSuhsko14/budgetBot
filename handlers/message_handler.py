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
from utils.keyboard import delete_keyboard, create_keyboard
from utils.product_text_handler import split_text_to_items
from utils.image_recognition import classify_image_from_telegram
from utils.image_recognition import classify_image_from_telegram


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

async def add_product_to_chat(chat_id, product_name, category="Категорія за замовчуванням"):
    """Додає товар у базу даних та оновлює список товарів у чаті"""
    product_id = add_product(chat_id, product_name, category)
    if product_id:
        products = get_active_products_by_chat(chat_id)
        chat_data[chat_id]['list_items'] = products
        return True
    return False

async def add_products_from_text(chat_id, text, context, update):
    """Додає товари з тексту у базу даних та оновлює інтерфейс"""
    # Розділяємо текст на окремі товари
    products_list = split_text_to_items(text)
    
    for product_name in products_list:
        # Додаємо кожен товар у базу даних
        add_product(chat_id, product_name, "Категорія за замовчуванням")
        log(f"Товар додано у чат {chat_id}: {product_name}")
    
    # Оновлюємо список товарів у пам'яті
    products = get_active_products_by_chat(chat_id)
    chat_data[chat_id]['list_items'] = products
    
    # Оновлюємо інтерфейс
    await delete_keyboard(chat_id, context)
    await create_keyboard(chat_id, update, context)

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
            await add_products_from_text(chat_id, result, context, update)
            
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

    

    if chat_data[chat_id]['awaiting_cost']:
        try:
            cost = float(user_text)
            product_ids = set(chat_data[chat_id]['selected_items'])  # IDs куплених товарів
            category = "Покупки"

            # Додавання витрати в базу даних
            add_expense(amount=cost, category=category, product_ids=list(product_ids), chat_id=chat_id)
            for product_id in product_ids:
                mark_product_as_deleted(product_id)

            # Отримання назв товарів з бази даних за ID
            purchased_products = get_products_by_ids(product_ids)
            purchased_names = [product[1] for product in purchased_products if product[1]]

            # Формування списку куплених товарів
            purchased_list = "\n • ".join(purchased_names) if purchased_names else "порожній"
            text = f"Куплені товари:\n • {purchased_list}\nВартість: {cost:.2f}"

            # Оновлення або створення повідомлення
            if chat_data[chat_id].get('purchased_message_id'):
                try:
                    await context.bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=chat_data[chat_id]['purchased_message_id'],
                        text=text
                    )
                except Exception as e:
                    log(f"Не вдалося оновити повідомлення: {e}")
            else:
                sent = await context.bot.send_message(chat_id, text)
                chat_data[chat_id]['purchased_message_id'] = sent.message_id

            # Очищення після завершення купівлі
            chat_data[chat_id]['list_items'] = get_active_products_by_chat(chat_id)
            chat_data[chat_id]['selected_items'] = []

            await delete_keyboard(chat_id, context)
            await create_keyboard(chat_id, update, context)
            chat_data[chat_id]['awaiting_cost'] = False
            return

        except ValueError:
            await context.bot.send_message(chat_id, "Введіть правильну числову суму.")
            return

    elif 'list_items' in chat_data[chat_id]:
        await add_products_from_text(chat_id, user_text, context, update)
