import os
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from handlers.start_handler import start
from handlers.message_handler import handle_message
from handlers.button_handler import button
from data.database import create_tables
from utils.logger import logger

# Завантаження змінних середовища
def load_env():
    if os.path.exists(".env"):
        with open(".env") as f:
            for line in f:
                if line.strip() and not line.startswith("#"):
                    key, value = line.strip().split("=", 1)
                    os.environ[key] = value

# Завантаження змінних
load_env()

# Конфігурація
TOKEN = os.getenv("TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 8443))

if __name__ == "__main__":
    try:
        logger.info("Запуск бота...")

        # Створення таблиць у базі даних
        create_tables()

        # Ініціалізація додатку
        application = Application.builder().token(TOKEN).build()

        # Додавання обробників
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        application.add_handler(CallbackQueryHandler(button))

        logger.info(f"Бот працює на порту {PORT}!")

        # Встановлення вебхука
        application.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            webhook_url=WEBHOOK_URL,
        )
    except Exception as e:
        logger.error(f"Помилка запуску: {e}")
