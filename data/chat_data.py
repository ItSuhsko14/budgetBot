# data/chat_data.py

chat_data = {}
# Для кожного chat_id:
# {
#   'list_items': [...],
#   'removed_items': [...],  # Якщо використовували раніше для видалених товарів
#   'purchased_items': [],   # Додаємо для куплених товарів
#   'selected_items': [],    # Додаємо для вибраних товарів
#   'list_message_id': None,
#   'purchase_mode': False,  # Режим позначення куплених
#   'awaiting_cost': False,  # Очікування вводу вартості
#   'purchased_message_id': None  # Повідомлення з купленими товарами
# }

# При ініціалізації (наприклад, у start) встановлюйте всі поля, якщо не існують:
# chat_data[chat_id] = {
#   'list_items': [],
#   'removed_items': [],
#   'purchased_items': [],
#   'list_message_id': None,
#   'purchase_mode': False,
#   'awaiting_cost': False,
#   'purchased_message_id': None
# }

# отримати список активних товарів
def get_active_products(chat_id):
    return chat_data[chat_id]['list_items']
    
# отримати список помічених на видалення
def get_marked_for_deletion(chat_id):
    return chat_data[chat_id]['removed_items']
    
# отримати список помічених на купівлю
def get_marked_for_purchase(chat_id):
    return chat_data[chat_id]['purchased_items']

def get_selected_products(chat_id):
    return chat_data[chat_id]['selected_items']
