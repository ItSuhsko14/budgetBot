import os
import psycopg2
import sys
import time  

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.env_loader import load_env

# Завантаження змінних середовища
load_env()
DATABASE_URL = os.environ.get("DATABASE_URL")

# Підключення до бази даних
def connect_to_database(retries=5, delay=2):
    for attempt in range(1, retries + 1):
        try:
            conn = psycopg2.connect(DATABASE_URL)
            print(f"✅ Підключення успішне (спроба {attempt})")
            return conn
        except Exception as e:
            print(f"❌ Спроба {attempt} не вдалася: {e}")
            if attempt < retries:
                print(f"⏳ Очікування {delay} секунд перед наступною спробою...")
                time.sleep(delay)
            else:
                print("🔴 Вичерпано всі спроби підключення до бази даних.")
    return None

# Створення таблиць
def create_tables():
    print(f"DATABASE_URL: {DATABASE_URL}")
    conn = connect_to_database()
    if conn:
        cur = conn.cursor()

        try:
            # Створення таблиці `products`
            cur.execute("""
            CREATE TABLE IF NOT EXISTS products (
                product_id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                chat_id BIGINT NOT NULL,
                status TEXT NOT NULL CHECK (status IN ('active', 'deleted', 'purchased')) DEFAULT 'active'
            );
            """)

            # Створення таблиці `expenses`
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

            # Створення таблиці `categories`
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
            print("✅ Таблиці створені або оновлені успішно")
        except Exception as e:
            print(f"❌ Помилка створення таблиць: {e}")
        finally:
            if 'cur' in locals() and cur:
                cur.close()
            if 'conn' in locals() and conn:
                conn.close()

# CRUD-функції для витрат
def add_expense(amount, category, product_ids, chat_id):
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
            print(f"✅ Витрата з ID {expense_id} додана.")
            return expense_id
        except Exception as e:
            print(f"❌ Помилка додавання витрати: {e}")
        finally:
            cur.close()
            conn.close()

# Запуск створення таблиць
if __name__ == "__main__":
    create_tables()
