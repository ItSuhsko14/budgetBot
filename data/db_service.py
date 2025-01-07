from data.database import connect_to_database

# Додавання товару в таблицю products
def add_product(chat_id, name, category):
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

def add_expense(chat_id, amount, category, product_ids):
    """
    Додає витрату в таблицю expenses.

    Аргументи:
    chat_id - ID чату
    amount - Сума витрати
    category - Категорія витрати
    product_ids - Список ID товарів
    """
    conn = connect_to_database()
    if conn:
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO expenses (chat_id, amount, category, product_ids)
                VALUES (%s, %s, %s, %s)
                RETURNING expense_id, expense_date;
            """, (chat_id, amount, category, product_ids))
            
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