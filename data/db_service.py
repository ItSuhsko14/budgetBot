from data.database import connect_to_database
from utils.logger import log

# Додавання товару в таблицю products
def add_product(chat_id, name, category=None):

    conn = connect_to_database()
    if conn:
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO products (chat_id, name, category, status)
                VALUES (%s, %s, %s, %s)
                RETURNING product_id;
            """, (chat_id, name, category, 'active'))
            
            result = cur.fetchone()
            if result:
                product_id = result[0]
                conn.commit()
                print(f"✅ Товар '{name}' додано з ID {product_id}.")
                return product_id
            else:
                print("❌ Помилка: INSERT не повернув ID.")
        except Exception as e:
            print(f"❌ Помилка додавання товару: {e}")
        finally:
            cur.close()
            conn.close()

def make_db_request_by_query(query, params):
    conn = None
    try:
        conn = connect_to_database()
        if not conn:
            log("❌ Помилка підключення до бази даних")
            return None
            
        cur = conn.cursor()
        cur.execute(query, params)
       # Для SELECT запитів повертаємо результати
        if query.strip().upper().startswith('SELECT'):
            result = cur.fetchall()
        # Для інших запитів повертаємо кількість змінених рядків
        else:
            result = cur.rowcount
        conn.commit()
        return result
    except Exception as e:
        log(f"❌ Помилка при запиті в базу: {e}")
        if conn:
            conn.rollback()
        return None
    finally:
        if conn:
            try:
                if 'cur' in locals() and cur:
                    cur.close()
                conn.close()
            except Exception as e:
                log(f"❌ Помилка при закритті з'єднання: {e}")
    
def create_category(chat_id, name):
    return make_db_request_by_query("""
            INSERT INTO categories (chat_id, name)
            VALUES (%s, %s)
            RETURNING category_id;
        """, (chat_id, name))
            

def get_all_categories(chat_id):
    result = make_db_request_by_query("""
        SELECT category_id, name
        FROM categories
        WHERE chat_id = %s
        ORDER BY name;
    """, (chat_id,))
    
    # Повертаємо порожній список, якщо результатів немає
    return result if result else []

def delete_category_from_db(chat_id, category_id):
    category = make_db_request_by_query("""
            SELECT name, category_id
            FROM categories
            WHERE category_id = %s and chat_id = %s;
        """, (category_id, chat_id))
    log(f"✅ Категорія {category} з ID {category_id} видалена")
    return make_db_request_by_query("""
            DELETE FROM categories
            WHERE category_id = %s and chat_id = %s;
        """, (category_id, chat_id))

def get_active_products_by_chat(chat_id):
    conn = connect_to_database()
    if conn:
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT product_id, name, category 
                FROM products 
                WHERE chat_id = %s AND status = 'active';
            """, (chat_id,))
            products = cur.fetchall()
            print(f"📦 Активні товари для чату {chat_id}: {products}")
            return products
        except Exception as e:
            print(f"❌ Помилка отримання активних товарів: {e}")
        finally:
            cur.close()
            conn.close()

def get_products_by_ids(product_ids):
    conn = connect_to_database()
    if conn:
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT product_id, name, category
                FROM products
                WHERE product_id = ANY(%s);
            """, (list(map(int, product_ids)),))
            return cur.fetchall()
        except Exception as e:
            print(f"❌ Помилка отримання товарів за ID: {e}")
        finally:
            cur.close()
            conn.close()
    return []

def mark_product_as_deleted(product_id):
    conn = connect_to_database()
    if conn:
        cur = conn.cursor()
        try:
            cur.execute("""
                UPDATE products
                SET status = 'deleted'
                WHERE product_id = %s;
            """, (product_id,))
            conn.commit()
            print(f"✅ Товар з ID {product_id} успішно відмічено як 'видалений'.")
        except Exception as e:
            print(f"❌ Помилка відмічення товару як 'видалений': {e}")
        finally:
            cur.close()
            conn.close()

def add_expense(amount, product_ids, chat_id, category=None):
    """
    Додає витрату в таблицю expenses.

    Аргументи:
    amount - Сума витрати
    category - Категорія витрати
    product_ids - Список ID товарів
    chat_id - ID чату
    """
    conn = connect_to_database()
    if conn:
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO expenses (amount, category, product_ids, chat_id)
                VALUES (%s, %s, %s, %s)
                RETURNING expense_id, expense_date;
            """, (amount, category, [int(pid) for pid in product_ids], chat_id))
            
            result = cur.fetchone()
            if result:
                expense_id, expense_date = result
                conn.commit()
                print(f"✅ Витрату з ID {expense_id} додано на {expense_date}.")
                return expense_id
            else:
                print("❌ Помилка: INSERT не повернув ID витрати.")
        except Exception as e:
            print(f"❌ Помилка додавання витрати: {e}")
        finally:
            cur.close()
            conn.close()

def mark_product_as_purchased(product_id):
    """
    Оновлює статус товару в таблиці `products` на 'purchased'.
    """
    conn = connect_to_database()
    if conn:
        cur = conn.cursor()
        try:
            cur.execute("""
                UPDATE products
                SET status = 'purchased'
                WHERE product_id = %s;
            """, (product_id,))
            conn.commit()
            print(f"✅ Товар з ID {product_id} позначено як 'purchased'.")
        except Exception as e:
            print(f"❌ Помилка позначення товару як 'purchased': {e}")
        finally:
            cur.close()
            conn.close()