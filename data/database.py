import os
import psycopg2
import sys
import time
import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.env_loader import load_env

# Завантаження змінних середовища
load_env()
DATABASE_URL = os.environ.get("DATABASE_URL")

def log(msg):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {msg}")

# Підключення до бази даних
def connect_to_database(retries=5, delay=2):
    for attempt in range(1, retries + 1):
        log(f"🔌 Спроба підключення до бази даних (спроба {attempt})")
        try:
            conn = psycopg2.connect(DATABASE_URL)
            log("✅ Підключення успішне")
            return conn
        except Exception as e:
            log(f"❌ Помилка підключення: {e}")
            if attempt < retries:
                log(f"⏳ Повторна спроба через {delay} с...")
                time.sleep(delay)
            else:
                log("🔴 Вичерпано всі спроби підключення")
    return None

# Створення таблиць
def create_tables():
    log(f"🌍 DATABASE_URL: {DATABASE_URL}")
    conn = connect_to_database()
    if conn:
        try:
            cur = conn.cursor()
            log("🧱 Створення таблиць...")

            cur.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    product_id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    chat_id BIGINT NOT NULL,
                    status TEXT NOT NULL CHECK (status IN ('active', 'deleted', 'purchased')) DEFAULT 'active'
                );
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS expenses (
                    expense_id SERIAL PRIMARY KEY,
                    expense_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    amount NUMERIC(10, 2) NOT NULL,
                    category TEXT NOT NULL,
                    product_ids INTEGER[] NOT NULL,
                    chat_id BIGINT NOT NULL
                );
            """)


            cur.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    category_id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    chat_id BIGINT NOT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE,
                    UNIQUE(name, chat_id)  -- унікальна пара назва категорії та чат
                );
            """)

            conn.commit()
            log("✅ Таблиці створені або оновлені успішно")
        except Exception as e:
            log(f"❌ Помилка під час створення таблиць: {e}")
        finally:
            cur.close()
            conn.close()
    else:
        log("🔴 Підключення відсутнє — таблиці не створено")

# CRUD-функції для витрат
def add_expense(amount, category, product_ids, chat_id):
    log(f"📥 Додавання витрати: {amount}, категорія: {category}, товари: {product_ids}, чат: {chat_id}")
    conn = connect_to_database()
    if conn:
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO expenses (amount, category, product_ids, chat_id)
                VALUES (%s, %s, %s, %s)
                RETURNING expense_id;
            """, (amount, category, [int(pid) for pid in product_ids], chat_id))
            expense_id = cur.fetchone()[0]
            conn.commit()
            log(f"✅ Витрата з ID {expense_id} додана")
            return expense_id
        except Exception as e:
            log(f"❌ Помилка при додаванні витрати: {e}")
        finally:
            cur.close()
            conn.close()
    else:
        log("🔴 Підключення відсутнє — не вдалося додати витрату")

# Запуск створення таблиць
if __name__ == "__main__":
    create_tables()