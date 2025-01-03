import os
import psycopg2
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.env_loader import load_env

# Завантаження змінних середовища
load_env()
DATABASE_URL = os.environ.get("DATABASE_URL")

# Підключення до бази даних
def connect_to_database():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        print("✅ Підключення успішне!")
        return conn
    except Exception as e:
        print(f"❌ Помилка підключення: {e}")
        return None

# Створення таблиць
def create_tables():
    print(f"DATABASE_URL: {DATABASE_URL}")
    conn = connect_to_database()
    if conn:
        cur = conn.cursor()

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

        conn.commit()
        print("✅ Таблиці 'products' та 'expenses' створені або оновлені успішно!")
        cur.close()
        conn.close()
    else:
        print("🔴 Не вдалося створити таблиці.")

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
            """, (amount, category, product_ids, chat_id))
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
