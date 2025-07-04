from data.db_service import getExpensesByChatForLastMonth, get_products_by_ids, get_all_categories
from utils.logger import log
from utils.keyboard import create_keyboard

async def show_expenses(chat_id, context):
    expenses = getExpensesByChatForLastMonth(chat_id)
    log(f"expenses: {expenses}")
    sum_of_expenses_by_category = get_sum_expenses_by_category(chat_id, expenses)
    log(f"sum_of_expenses_by_category: {sum_of_expenses_by_category}")
    expenses_by_category_string = create_string_category_sum(sum_of_expenses_by_category)
    log(f"expenses_by_category_string: {expenses_by_category_string}")
    sum_of_expenses = sum(sum_of_expenses_by_category.values())
    log(f"Сума всіх витрат: {sum_of_expenses}")
    
    message = expenses_by_category_string + f"\n\nСума всіх витрат: {sum_of_expenses}"
    
    await send_message_to_chat(chat_id, context, message)
    await create_keyboard(chat_id, context)
    return {sum_of_expenses, message}

def expense_string(expense):
    expense_sting = ''
    expense_date = expense[1].strftime('%d-%m %H:%M')
    expense_amount = expense[2]
    expense_category = expense[3]
    product_ids = expense[4]
    products = get_products_by_ids(product_ids)
    list_of_products = ''
    for product in products:
        list_of_products += product[1] + ', '
    expense_sting = f"\nДата, час: {expense_date}, Сума: {expense_amount}\nКатегорія: {expense_category}\nТовари: {list_of_products}\n ----------"
    return expense_sting

def get_sum_of_expenses_by_category(expenses):
    sum_by_category_name = {}
    for expense in expenses:
        if expense[3] in sum_by_category_name:
            sum_by_category_name[expense[3]] += expense[2]
        else:
            sum_by_category_name[expense[3]] = expense[2]
    return sum_by_category_name

async def send_message_to_chat(chat_id, context, message):
    await context.bot.send_message(chat_id, message)

def get_sum_expenses_by_category(chat_id, expenses):
    expenses_by_category = {}
    for expense in expenses:
        category = get_category_name_by_id(chat_id, expense[0])
        amount = expense[2]
        if category in expenses_by_category:
            expenses_by_category[category] += amount
        else:
            expenses_by_category[category] = amount
    return expenses_by_category

def create_string_category_sum(sum_of_expenses_by_category):
    string = ''
    for category, amount in sum_of_expenses_by_category.items():
        string += f"\n {category}:{amount} грн."
    return string

def get_category_name_by_id(chat_id, category_id):
    categories = get_all_categories(chat_id)
    for category in categories:
        if category[0] == category_id:
            return category[1]
    return None