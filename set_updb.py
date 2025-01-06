import sqlite3
import os


# Connect to the SQLite database (it will be created if it doesn't exist)
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Create a simple users table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
''')

conn.commit()
conn.close()

print("Database and table created successfully!")
