# Webhook setting
https://api.telegram.org/bot<BOT_TOKEN>/setWebhook?url=https://budgetbot-eavg.onrender.com

# Start environment
python3 -m venv venv
source venv/bin/activate

# Start project
phyton3 main.py

# Create bot
Bot father
Done! Congratulations on your new bot. You will find it at t.me/testingBudgetBot. You can now add a description, about section and profile picture for your bot, see /help for a list of commands. By the way, when you've finished creating your cool bot, ping our Bot Support if you want a better username for it. Just make sure the bot is fully operational before you do this.

Use this token to access the HTTP API:
7948478174:AAEzlOM1Dpw_IVXozyIio__5NPeyDyGdH-E
Keep your token secure and store it safely, it can be used by anyone to control your bot.

For a description of the Bot API, see this page: https://core.telegram.org/bots/api

# Create webhook
curl -X POST "https://api.telegram.org/bot7948478174:AAEzlOM1Dpw_IVXozyIio__5NPeyDyGdH-E/setWebhook?url=https://b886-80-92-232-25.ngrok-free.app"


# Delete webhook
curl -X POST "https://api.telegram.org/bot7948478174:AAEzlOM1Dpw_IVXozyIio__5NPeyDyGdH-E/deleteWebhook"

# Test webhook
curl -X GET "https://api.telegram.org/bot7948478174:AAEzlOM1Dpw_IVXozyIio__5NPeyDyGdH-E/getWebhookInfo"

# Get bot
curl -X GET "https://api.telegram.org/bot7948478174:AAEzlOM1Dpw_IVXozyIio__5NPeyDyGdH-E/getMe"


                                                                                                
## Структура даних

Мутабельна Таблиця products:
Зберігає актуальний стан товарів з полями status (потрібно купити, куплено, видалено).
Використовується для швидкого доступу до активних товарів.

Іммутована Таблиця products_history:
Зберігає всі дії з товарами, включаючи створення, видалення, купівлю.
Використовується для звітування та аналітики.

Таблиця expenses:
Фіксує витрати користувача, включаючи дату, суму та категорію витрати.
Витрати пов’язані з конкретними товарами через таблицю expense_products.
Таблиця categories:

Зберігає категорії товарів для класифікації та звітування.

CREATE botUser WHITH PASSWORD '123456'

 List of databases
     Name     | Owner  | Encoding | Collate | Ctype | Access privileges 
--------------+--------+----------+---------+-------+-------------------
 budgettestdb | andriy | UTF8     | C       | C     | 
 postgres     | andriy | UTF8     | C       | C     | 
 template0    | andriy | UTF8     | C       | C     | =c/andriy        +
              |        |          |         |       | andriy=CTc/andriy
 template1    | andriy | UTF8     | C       | C     | =c/andriy        +
              |        |          |         |       | andriy=CTc/andriy

GRANT ALL PRIVILEGES ON DATABASE budgettestdb TO botUser;
