import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from handlers.start_handler import start
from handlers.message_handler import handle_message
from handlers.button_handler import button
from utils.logger import logger
from data.chat_data import chat_data

# Ваш токен
TOKEN = '7863397132:AAHAdiMFE1H5jbffiPP0vYcjga6qSUu7C4A'

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
