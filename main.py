import os
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
from telegram.error import TelegramError

from handlers.start_handler import start
from handlers.message_handler import handle_message
from handlers.button_handler import button
from data.database import create_tables
from utils.logger import log


def load_env():
    """Завантаження змінних середовища з .env"""
    if os.path.exists(".env"):
        with open(".env") as f:
            for line in f:
                if line.strip() and not line.startswith("#"):
                    key, value = line.strip().split("=", 1)
                    os.environ[key] = value


async def error_handler(update, context: ContextTypes.DEFAULT_TYPE):
    """Глобальний обробник винятків"""
    log("❌ Виникла помилка в обробці оновлення", exc_info=True)

    # Повідомлення користувачу (опціонально, якщо хочеш зворотній зв'язок)
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text("⚠️ Виникла технічна помилка. Ми вже над цим працюємо.")
    except TelegramError:
        pass  # Не можемо навіть відповісти користувачу


# --- Запуск ---
load_env()

TOKEN = os.getenv("TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 8443))

if __name__ == "__main__":
    try:
        log("🚀 Запуск бота...")

        create_tables()

        application = Application.builder().token(TOKEN).build()

        # Handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        application.add_handler(CallbackQueryHandler(button))

        # Error handler
        application.add_error_handler(error_handler)

        log(f"🌐 Бот працює на порту {PORT}")
        application.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            webhook_url=WEBHOOK_URL,
        )

    except Exception:
        log("❌ Помилка запуску", exc_info=True)
