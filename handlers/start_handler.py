from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from data.chat_data import chat_data
from utils.logger import log
from utils.keyboard import create_keyboard, remove_keyboard
from data.db_service import get_active_products_by_chat, get_all_categories
from utils.initialize_chat import initialize_chat


async def start_message(update: Update, context: CallbackContext):
    chat = update.effective_chat
    if chat.type == "private":
        await context.bot.send_message(
            chat_id=chat.id,
            text=("👋 Привіт! Я BudgetBestBot — трекер витрат у Telegram.\n\n"
                 "📍 Я найкраще працюю в груповому чаті.\n"
                 "Натисни кнопку нижче, щоб додати мене у групу та почати спільно вести бюджет:"),
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("➕ Додати в групу", url="https://t.me/budgetBestBot?startgroup=true")
            ]])
        )
    else:
        await context.bot.send_message(
            chat_id=chat.id,
            text=("👋 Вітаю всіх! Я BudgetBestBot — бот для ведення спільного бюджету.\n\n"
                 "📌 Допоможу вам вести список покупок, фіксувати витрати та аналізувати витрати за категоріями.\n\n"
                 "✏️ Щоб почати, просто додайте товари до списку або створіть категорії для кращого аналізу витрат.")
        )

async def start(update: Update, context: CallbackContext):
    log(f"/start від {update.message.from_user.username} у чаті {update.effective_chat.id}")
    chat_id = update.effective_chat.id

    # Перевіряємо чи існує запис для цього чату, якщо ні — створюємо
    if chat_id not in chat_data:
        initialize_chat(chat_id)

    products = get_active_products_by_chat(chat_id)
    categories = get_all_categories(chat_id)

    # Зберігаємо в локальний стейт
    chat_data[chat_id]['list_items'] = products
    chat_data[chat_id]['categories'] = categories
    await start_message(update, context)
    await remove_keyboard(update, context)
    await create_keyboard(chat_id, context)
    