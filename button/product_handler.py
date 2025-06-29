from handlers.message_handler import add_products_from_text, prompt_add_product
from data.chat_data import chat_data
from utils.logger import log

async def add_product_with_category(chat_id, context, category):
    log(f"✅ Натиснуто кнопку категорії з ід {category}")
    
    chat_data[chat_id]['current_category'] = int(category)
    await prompt_add_product(chat_id, context)