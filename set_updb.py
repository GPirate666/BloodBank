import sqlite3
import os

# Path to the database file
db_path = 'database.db'

# Connect to the SQLite database (it will be created if it doesn't exist)
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Drop the existing users table if it exists
cursor.execute("DROP TABLE IF EXISTS users")

# Create a new users table with the updated fields
cursor.execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL 
    )
''')

conn.commit()
conn.close()

print("Users table has been successfully recreated with the updated structure.")
