import logging
import os
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from handlers.start_handler import start
from handlers.message_handler import handle_message
from handlers.button_handler import button
from utils.logger import logger
from data.chat_data import chat_data

def load_env():
    if os.path.exists(".env"):
        with open(".env") as f:
            for line in f:
                # Ігноруємо коментарі та порожні рядки
                if line.strip() and not line.startswith("#"):
                    key, value = line.strip().split("=", 1)
                    os.environ[key] = value

# Запуск завантаження змінних
load_env()

# Отримання токена
TOKEN = os.environ.get("TOKEN")

def main():
    logger.info("Запуск бота...")
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(button))
    logger.info("Бот працює!")
    application.run_polling()

if __name__ == "__main__":
    main()
