import sqlite3

def update_badges_and_donations(database_path):
    try:
        # Connect to the database
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()

        # Input the ID, badges, and donations from the user
        user_id = int(input("Enter the user ID: "))
        badges_value = int(input("Enter the badges value: "))
        donations_value = int(input("Enter the donations value: "))
        medals=int(input("Enter the medals number: "))
        # Update the badges and donations for the specified user_id
        cursor.execute('''
            UPDATE badges
            SET badges = ?, donations = ?, medals=?
            WHERE user_id = ?
        ''', (badges_value, donations_value,medals, user_id))

        # Commit the transaction
        conn.commit()

        # Check if the row was updated
        if cursor.rowcount > 0:
            print(f"Successfully updated user_id {user_id}: badges={badges_value}, donations={donations_value}")
        else:
            print(f"No rows were updated for user_id {user_id}. Ensure the user_id exists in the table.")

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

    finally:
        # Close the connection
        conn.close()

# Main program
if __name__ == "__main__":
    database_path = "database.db"  # Replace with your database file path
    update_badges_and_donations(database_path)
