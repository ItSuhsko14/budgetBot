from data.db_service import getExpensesByChatForLastMonth, get_products_by_ids, get_all_categories
from utils.logger import log
from utils.keyboard import create_keyboard

async def show_expenses(chat_id, context):
    expenses = getExpensesByChatForLastMonth(chat_id)
    log(f"Expenses: {expenses}")
    sum_of_expenses_by_category = get_sum_expenses_by_category(chat_id, expenses)
    log(f"Sum of expenses by category: {sum_of_expenses_by_category}")
    expenses_by_category_string = create_string_category_sum(sum_of_expenses_by_category)
    log(f"expenses_by_category_string: {expenses_by_category_string}")
    sum_of_expenses = sum(sum_of_expenses_by_category.values())
    log(f"Sum of expenses: {sum_of_expenses}")
    
    message = "Витрати за місяць:\n" + expenses_by_category_string + f"\nСума всіх витрат: {sum_of_expenses}"
    log(f"Message: {message}")
    
    await send_message_to_chat(chat_id, context, message)
    log(f"Message sent to chat: {message}")
    await create_keyboard(chat_id, context)
    log(f"Keyboard created for chat: {chat_id}")
    return {sum_of_expenses, message}

async def send_message_to_chat(chat_id, context, message):
    await context.bot.send_message(chat_id, message)

def get_sum_expenses_by_category(chat_id, expenses):
    log(f"get_sum_expenses_by_category expenses: {expenses}")
    expenses_by_category = {}
    for expense in expenses:
        log(f"get_sum_expenses_by_category expense: {expense}")
        category = get_category_name_by_id(chat_id, expense[3]) or "Різне"
        amount = expense[2]
        log(f"get_sum_expenses_by_category category: {category}, amount: {amount}")
        if category in expenses_by_category:
            expenses_by_category[category] += amount
        else:
            expenses_by_category[category] = amount
    return expenses_by_category

def create_string_category_sum(sum_of_expenses_by_category):
    string = ''
    for category, amount in sum_of_expenses_by_category.items():
        string += f"• {category}:{amount} грн.\n"
    return string

def get_category_name_by_id(chat_id, category_id):
    categories = get_all_categories(chat_id)
    for category in categories:
        if category[0] == category_id:
            return category[1]
    return None