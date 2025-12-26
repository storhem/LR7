import sqlite3
import csv

conn = sqlite3.connect('orders.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    age INTEGER,
    email TEXT UNIQUE
)''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    product_name TEXT NOT NULL,
    price REAL,
    order_date TEXT,
    FOREIGN KEY (user_id) REFERENCES users (id)
)''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT,
    price REAL
)''')

users_data = [
    ('Иван Иванов', 30, 'ivan@mail.com'),
    ('Мария Петрова', 25, 'maria@mail.com'),
    ('Алексей Сидоров', 35, 'alex@mail.com')
]
cursor.executemany('INSERT INTO users (name, age, email) VALUES (?, ?, ?)', users_data)

products_data = [
    ('Ноутбук', 'Электроника', 50000),
    ('Смартфон', 'Электроника', 30000),
    ('Книга', 'Образование', 1000)
]
cursor.executemany('INSERT INTO products (name, category, price) VALUES (?, ?, ?)', products_data)

cursor.execute('INSERT INTO orders (user_id, product_name, price, order_date) VALUES (1, "Ноутбук", 50000, "2025-01-15")')
cursor.execute('INSERT INTO orders (user_id, product_name, price, order_date) VALUES (2, "Смартфон", 30000, "2025-01-16")')

cursor.execute('''
SELECT u.name, u.age, u.email, o.product_name, o.price, o.order_date
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
ORDER BY u.name
''')
data = cursor.fetchall()

print("Имя | Возраст | Email | Товар | Цена | Дата заказа")
for row in data:
    print(f"{row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} | {row[5]}")
