from data.db_service import getExpensesByChatForLastMonth, get_products_by_ids
from utils.logger import log
from utils.keyboard import create_keyboard

async def show_expenses(chat_id, context):
    expenses = getExpensesByChatForLastMonth(chat_id)
    expenses_string = ''
    for expense in expenses:
        expenses_string += expense_string(expense)
        log(expenses_string)
    sum_of_expenses = get_sum_of_expenses(expenses)

    log(f"Сума всіх витрат: {sum_of_expenses}")
    
    await send_message_to_chat(chat_id, context, expenses_string + f"\n\nСума всіх витрат: {sum_of_expenses}")
    await create_keyboard(chat_id, context)
    return {sum_of_expenses, expenses_string}

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

def get_sum_of_expenses(expenses):
    return sum(expense[2] for expense in expenses)

async def send_message_to_chat(chat_id, context, message):
    await context.bot.send_message(chat_id, message)