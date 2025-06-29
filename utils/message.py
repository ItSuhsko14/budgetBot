from telegram import Update
from telegram.ext import ContextTypes
from data.chat_data import chat_data

async def write_message(chat_id: int, text: str, context: ContextTypes.DEFAULT_TYPE = None, reply_markup=None) -> None:
    """
    Універсальна функція для відправки повідомлень у чат.
    
    Args:
        chat_id: ID чату, куди відправляти повідомлення
        text: Текст повідомлення
        context: Контекст бота (опціонально)
        reply_markup: Об'єкт клавіатури (опціонально)
    """
    try:
        if context:
            # Відправка через контекст бота
            await context.bot.send_message(
                chat_id=chat_id,
                text=text,
                reply_markup=reply_markup
            )
        elif 'bot' in chat_data.get(chat_id, {}):
            # Відправка через збережений об'єкт бота
            await chat_data[chat_id]['bot'].send_message(
                chat_id=chat_id,
                text=text,
                reply_markup=reply_markup
            )
        else:
            print(f"Неможливо відправити повідомлення. Чат ID: {chat_id}, Текст: {text}")
    except Exception as e:
        print(f"Помилка при відправці повідомлення: {e}")