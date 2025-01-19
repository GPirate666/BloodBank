import sqlite3

def create_badges_table():
    try:
        # Connect to the database
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Drop the badges table if it already exists (optional)
        cursor.execute("DROP TABLE IF EXISTS badges")

        # Create the new badges table
        cursor.execute('''
            CREATE TABLE badges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                badges INTEGER DEFAULT 0,
                medals INTEGER DEFAULT 0,
                donations INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')

        # Insert existing users into the badges table with default values
        cursor.execute("SELECT id FROM users")
        users = cursor.fetchall()

        for user in users:
            user_id = user[0]
            # Insert default values for all users
            cursor.execute('''
                INSERT INTO badges (user_id, badges, medals, donations)
                VALUES (?, 0, 0, 0)
            ''', (user_id,))

        conn.commit()
        print("Badges table has been created and populated successfully with default values.")

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

    finally:
        if conn:
            conn.close()

# Run the function to create and populate the table
if __name__ == "__main__":
    create_badges_table()
