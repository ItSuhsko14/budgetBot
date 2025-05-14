Telegram бот для ведення списку покупок з інтеграцією в PostgreSQL та розгортанням через Docker.

---

### ♻Установка

1. Клонувати репозиторій:

```bash
git clone https://github.com/ItSuhsko14/budgetBot.git
cd budgetBot
```

2. Створити `.env` файл на основі прикладу:

```bash
cp .env.example .env
```

3. Встановити потрібні змінні середовища в `.env`

---

### 🚀Розгортання (Dev)

#### За допомогою ngrok:

1. Встановити [ngrok](https://ngrok.com/)
2. Запустити тунель:

```bash
ngrok http 8443
```

3. Взяти URL і оновити `WEBHOOK_URL` в `.env`

```env
WEBHOOK_URL=https://<your-ngrok-subdomain>.ngrok.io/webhook
```

4. Запустити локально:

```bash
python main.py
```

Або використовувати dev-скрипт:

```bash
bash start_dev.sh
```

---

### 🚫 Production через GitHub Actions

Застосунок буде автоматично оновлюватись на Raspberry Pi через self-hosted GitHub runner. Необхідно лише налаштувати Secrets.



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

For a description of the Bot API, see this page: https://core.telegram.org/bots/api

# Create webhook

# Delete webhook
curl -X POST "https://api.telegram.org/bot<BOT_TOKEN>/deleteWebhook"

# Test webhook
curl -X GET "https://api.telegram.org/bot<BOT_TOKEN>/getWebhookInfo"

# Get bot
curl -X GET "https://api.telegram.org/bot<BOT_TOKEN>/getMe"

# create tunel by ngrok

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

 List of databases
     Name     | Owner  | Encoding | Collate | Ctype | Access privileges 
--------------+--------+----------+---------+-------+-------------------
 budgettestdb | andriy | UTF8     | C       | C     | 
 postgres     | andriy | UTF8     | C       | C     | 
 template0    | andriy | UTF8     | C       | C     | =c/andriy        +
              |        |          |         |       | andriy=CTc/andriy
 template1    | andriy | UTF8     | C       | C     | =c/andriy        +
              |        |          |         |       | andriy=CTc/andriy

# connect to database from terminal
psql -h localhost -p 5432 -U botuser -d budgettestdb

