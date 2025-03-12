import logging
import sqlite3
from contextlib import closing

from config import config

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def create_tables(conn):
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS categories
    (id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products
    (id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    price REAL NOT NULL,
    image TEXT NOT NULL,
    category_id INTEGER,
    FOREIGN KEY(category_id) REFERENCES categories(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cart
    (id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quality INTEGER DEFAULT 1,
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(product_id) REFERENCES products(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders
    (order_id INTEGER PRIMARY KEY,
    user_id INTEGER,
    phone_number TEXT,
    status TEXT DEFAULT "new",
    total_sum REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS order_details 
    (id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    product_name TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price REAL NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id)
    )
    ''')

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS articles(
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT NOT NULL
    )
    """)
    conn.commit()
    logger.debug("Таблицы созданы.")


def insert_product(name, description, price, image, category_id):
    """Добавляет новый продукт в таблицу продуктов."""
    conn = sqlite3.connect(config.database_file.get_secret_value())
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO products (name, description, price, image, category_id)
        VALUES (?, ?, ?, ?, ?)
        """,
        (name, description, price, image, category_id)
    )

    conn.commit()
    conn.close()


def insert_article(title, description):
    """Добавляет новую статью в таблицу статей."""
    conn = sqlite3.connect(config.database_file.get_secret_value())
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO articles (title, description)
        VALUES (?, ?)
        """,
        (title, description)
    )
    conn.commit()
    conn.close()


def get_article(conn):
    """Получает все статьи из базы данных."""
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, description FROM articles")
    return cursor.fetchall()


def get_article_by_id(conn, article_id):
    """Получает статью по её ID из базы данных."""
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, description FROM articles WHERE id = ?", (article_id,))
    return cursor.fetchone()


def get_categories(conn):
    """Получает все категории из базы данных."""
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM categories")
    return cursor.fetchall()


def get_category_by_id(conn, category_id):
    """Получает категорию по её ID из базы данных."""
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, description FROM categories WHERE id = ?", (category_id,))
    return cursor.fetchone()


def get_products(conn):
    """Получает все продукты из базы данных."""
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, description, price, image, category_id FROM products")
    return cursor.fetchall()


def update_cart_quantity(conn, user_id, product_id, operation):
    """Обновляет количество товара в корзине."""
    cursor = conn.cursor()
    cursor.execute("SELECT quality FROM cart WHERE user_id = ? AND product_id = ?", (user_id, product_id))
    result = cursor.fetchone()

    if result is None:
        return False

    current_quantity = result[0]

    if operation == 'inc':
        new_quantity = current_quantity + 1
    elif operation == 'dec':
        new_quantity = max(current_quantity - 1, 1)

    cursor.execute("UPDATE cart SET quality = ? WHERE user_id = ? AND product_id = ?",
                   (new_quantity, user_id, product_id))
    conn.commit()
    return True


def delete_from_cart(conn, user_id, product_id):
    """Удаляет товар из корзины."""
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM cart WHERE user_id = ? AND product_id = ?", (user_id, product_id))
    count_before = cursor.fetchone()[0]

    cursor.execute("DELETE FROM cart WHERE user_id = ? AND product_id = ?", (user_id, product_id))
    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM cart WHERE user_id = ? AND product_id = ?", (user_id, product_id))
    count_after = cursor.fetchone()[0]
    print(conn, user_id, product_id)
    return count_before != count_after


def get_products_by_category(conn, category_id):
    """Получает продукты по категории."""
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, description, price, image FROM products WHERE category_id = ?", (category_id,))
    return cursor.fetchall()


def get_product_by_id(conn, product_id):
    """Получает продукт по его ID."""
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, description, price, image FROM products WHERE id = ?", (product_id,))
    return cursor.fetchone()


def add_to_cart(user_id, product_id):
    """Добавляет товар в корзину."""
    conn = sqlite3.connect(config.database_file.get_secret_value())
    cursor = conn.cursor()

    cursor.execute("SELECT quality FROM cart WHERE user_id = ? AND product_id = ?", (user_id, product_id))
    result = cursor.fetchone()

    if result is None:

        cursor.execute(
            """
            INSERT INTO cart (user_id, product_id, quality)
            VALUES (?, ?, 1)
            """,
            (user_id, product_id)
        )
    else:

        current_quantity = result[0]
        new_quantity = current_quantity + 1
        cursor.execute(
            """
            UPDATE cart
            SET quality = ?
            WHERE user_id = ? AND product_id = ?
            """,
            (new_quantity, user_id, product_id)
        )

    conn.commit()


def get_cart(user_id):
    """Получает содержимое корзины пользователя."""
    with closing(sqlite3.connect(config.database_file.get_secret_value())) as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT product_id, quality FROM cart WHERE user_id = ?", (user_id,))
        cart_items = cursor.fetchall()

        total_sum = 0
        items_info = []

        if cart_items:

            for item in cart_items:
                product_id, quantity = item

                cursor.execute("SELECT id, name, price FROM products WHERE id = ?", (product_id,))
                product_result = cursor.fetchone()

                if product_result:
                    id, product_name, product_price = product_result
                    total_sum += product_price * quantity
                    items_info.append((id, product_name, quantity, product_price))

        print(items_info)
        return items_info, total_sum


def save_order(conn, user_id, phone_number, items_info, total_sum):
    """Сохраняет заказ в базе данных."""
    cursor = conn.cursor()

    print(f"Inserting order: User ID={user_id}, Phone={phone_number}, Total={total_sum}")
    for item in items_info:
        print(f"Item: {item}")

    cursor.execute(
        """
        INSERT INTO orders (user_id, phone_number, total_sum)
        VALUES (?, ?, ?)
        """,
        (user_id, phone_number, total_sum)
    )

    order_id = cursor.lastrowid

    for item in items_info:
        product_name, quantity, product_price, item_total_sum = item
        cursor.execute(
            """
            INSERT INTO order_details (order_id, product_name, quantity, unit_price)
            VALUES (?, ?, ?, ?)
            """,
            (order_id, product_name, quantity, product_price)
        )

    conn.commit()
    return order_id


def clear_cart(conn, user_id):
    """Очищает корзину пользователя."""
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cart WHERE user_id = ?", (user_id,))
    conn.commit()


def get_connection():
    logger.debug("Подключение к базе данных...")
    conn = sqlite3.connect(config.database_file.get_secret_value())
    create_tables(conn)
    logger.debug("Подключение установлено.")
    return conn
