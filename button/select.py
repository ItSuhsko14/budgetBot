from data.chat_data import chat_data

async def select_product(chat_id, product_id):
    chat_data[chat_id]['selected_items'].append(product_id)

async def unselect_product(chat_id, product_id):
    chat_data[chat_id]['selected_items'].remove(product_id)
    
        
    