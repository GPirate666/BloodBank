import sqlite3

def add_meal_vouchers_column():
    try:
        # Connect to the database
        conn = sqlite3.connect('database.db')  # Replace 'database.db' with your actual database name
        cursor = conn.cursor()

        # Check if the column already exists
        cursor.execute("PRAGMA table_info(badges)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'meal_vouchers' not in columns:
            # Add the `meal_vouchers` column
            cursor.execute('''
                ALTER TABLE badges ADD COLUMN meal_vouchers INTEGER DEFAULT 0
            ''')
            conn.commit()
            print("Column 'meal_vouchers' added successfully.")
        else:
            print("Column 'meal_vouchers' already exists.")

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

    finally:
        if conn:
            conn.close()

# Run the function
if __name__ == "__main__":
    add_meal_vouchers_column()
