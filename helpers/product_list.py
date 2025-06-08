from data.db_service import get_active_products_by_chat
from data.chat_data import chat_data
from utils.logger import log

async def send_active_products_message(chat_id, context):
    log(f"Відправка повідомлення зі списком у чаті {chat_id}")
    active_products = get_active_products_by_chat(chat_id)
    await remove_active_products_message(chat_id, context)
    if active_products:
        active_list = "\n".join([f"- {product[1]}" for product in active_products])
        message = await context.bot.send_message(
            chat_id=chat_id,
            text=f"ТОВАРИ ДЛЯ ПОКУПКИ:\n{active_list}"
        )
        chat_data[chat_id]['list_message_id'] = message.message_id
    else:
        message = await context.bot.send_message(
            chat_id=chat_id,
            text="📋 Ваш список покупок порожній!"
        )
        chat_data[chat_id]['list_message_id'] = message.message_id

async def remove_active_products_message(chat_id, context):
    log(f"Видалення повідомлення зі списком у чаті {chat_id}")
    if chat_data[chat_id].get('list_message_id'):
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=chat_data[chat_id]['list_message_id'])
            log(f"Видалено повідомлення id={chat_data[chat_id]['list_message_id']} зі списком у чаті {chat_id}")
            chat_data[chat_id]['list_message_id'] = None
        except Exception as e:
            log(f"Не вдалося видалити повідомлення зі списком: {e}")