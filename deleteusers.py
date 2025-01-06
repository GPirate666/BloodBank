import sqlite3

# Function to delete a user by ID
def delete_user_by_id(user_id):
    try:
        # Connect to the database
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Check if the user exists
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()

        if user is None:
            print(f"No user found with ID: {user_id}")
            return

        # Delete the user
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        print(f"User with ID '{user_id}' has been deleted successfully.")

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

    finally:
        if conn:
            conn.close()

# Input: ID of the user to be deleted
if __name__ == "__main__":
    try:
        user_id_to_delete = int(input("Enter the ID of the user to delete: "))
        delete_user_by_id(user_id_to_delete)
    except ValueError:
        print("Invalid ID. Please enter a valid integer.")
