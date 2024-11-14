import sqlite3


def initiate_db():
    connection = sqlite3.connect("registration.db")
    cursor = connection.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Products(
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    price INT NOT NULL
    );
    ''')
    cursor.execute("DELETE FROM Products")

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users(
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    email TEXT NOT NULL,
    age INT NOT NULL,
    balance INT NOT NULL DEFAULT 1000
    );
    ''')

    connection.commit()
    connection.close()

def add_product(title, description, price):
    connection = sqlite3.connect("registration.db")
    cursor = connection.cursor()
    cursor.execute('INSERT INTO Products (title, description, price) VALUES (?, ?, ?)',
                   (title, description, price))
    connection.commit()


def get_all_products(limit=4):
    connection = sqlite3.connect("registration.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Products LIMIT ?", (limit,))
    products = cursor.fetchall()
    connection.close()
    return products

def add_user(username, email, age):
    connection = sqlite3.connect("registration.db")
    cursor = connection.cursor()
    cursor.execute('INSERT INTO Users (username, email, age, balance) VALUES (?, ?, ?, ?)',
    (username, email, age, 1000))
    connection.commit()

def is_included(username):
    connection = sqlite3.connect("registration.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Users WHERE username = ?", (username,))
    user = cursor.fetchone()

    connection.close()
    return user is not None


