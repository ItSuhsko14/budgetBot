# utils/chat.py

from data.chat_data import chat_data

def initialize_chat(chat_id):
    if chat_id not in chat_data:
        chat_data[chat_id] = {
            'list_items': [],
            'removed_items': [],
            'purchased_items': [],
            'selected_items': [],
            'selected_categories': [],
            'keyboard_message_id': None,
            'list_message_id': None,
            'purchase_mode': False,
            'awaiting_cost': False,
            'current_category': None,
            'purchased_message_id': None,
            'ephemeral_messages': [],
            'prompt_message_id': None, 
            'current_category': None
        }