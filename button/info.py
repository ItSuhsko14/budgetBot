raw_text = [
    "📌 *Як працює цей бот?*\n",
    "👥 *Для всіх учасників чату:*",
    "• Додавати та видаляти товари",
    "• Створювати та керувати категоріями\n",
    
    "🛒 *Як додати товар?*",
    "1. Без категорії: просто надішліть назву товару",
    "2. З категорією: натисніть '➕ Додати товар' біля потрібної категорії\n",
    
    "📊 *Статистика витрат*",
    "• Додавайте товари до категорій для аналізу витрат",
    "• Переглядайте звіти за місяць у розрізі категорій\n",
    
    "🗑 *Як видалити?*",
    "• *Товари*: оберіть потрібні та натисніть '❌ Видалити товар'",
    "• *Категорії*: оберіть категорії та натисніть '❌ Видалити категорію'\n",
    
    "💸 *Фіксація витрат*",
    "1. Виберіть куплені товари",
    "2. Натисніть '✅ Позначити купленими'",
    "3. Введіть загальну суму витрат\n",
    
    "ℹ️ *Корисні поради*",
    "• Використовуйте категорії для кращого аналізу витрат",
    "• Регулярно переглядайте статистику витрат",
    "• Не забувайте фіксувати купівлі для точної статистики"
]

info_text = "\n".join(raw_text)

async def send_info_message(chat_id, context):
    await context.bot.send_message(chat_id, info_text)   

async def send_card_number(chat_id, context) :
    await context.bot.send_message(chat_id, "`1111 2222 3333 4444`", parse_mode='MarkdownV2') 