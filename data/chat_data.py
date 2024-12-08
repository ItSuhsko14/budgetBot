# data/chat_data.py

chat_data = {}
# Для кожного chat_id:
# {
#   'list_items': [...],
#   'removed_items': [...],  # Якщо використовували раніше для видалених товарів
#   'purchased_items': [],   # Додаємо для куплених товарів
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
