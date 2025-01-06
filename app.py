from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

# Secret key (for session management if needed in the future)
app.secret_key = 'your_secret_key'

# Helper function to connect to the database
def get_db_connection():
    try:
        conn = sqlite3.connect('database.db')  # Adjust path if necessary
        conn.row_factory = sqlite3.Row  # Enable dictionary-like row access
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return None

# Route to create a new user
@app.route('/user', methods=['POST'])
def create_user():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')

    if not username or not email:
        return jsonify({"error": "Username and email are required"}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username, email) VALUES (?, ?)', (username, email))
        conn.commit()
        return jsonify({"message": "User created successfully!"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Username or email already exists"}), 400
    finally:
        conn.close()

# Route to get all users
@app.route('/users', methods=['GET'])
def get_users():
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = conn.cursor()
    cursor.execute('SELECT id, username, email FROM users')
    users = cursor.fetchall()
    conn.close()

    users_list = [{"id": row["id"], "username": row["username"], "email": row["email"]} for row in users]
    return jsonify(users_list), 200

if __name__ == '__main__':
    app.run(debug=True)
