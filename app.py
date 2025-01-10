from flask import Flask, render_template, redirect, url_for, request, session, flash, jsonify
import sqlite3
from flask_mail import Mail, Message
from email.mime.text import MIMEText
from datetime import datetime, timedelta
import random

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

@app.route('/')
def index():
    logged_in = 'logged_in' in session
    return render_template('index.html', logged_in=logged_in)

# Combined GET and POST route for /schedule
@app.route('/schedule', methods=['GET', 'POST'])
def schedule():
    if request.method == 'GET':
        if 'logged_in' in session:
            return render_template('schedule.html')
        flash("Please log in to access the schedule page.", 'error')
        return redirect(url_for('login'))
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            user_id = data.get('user_id')
            blood_type = data.get('blood_type')
            date = data.get('date')
            time_slot = data.get('time')
            hospital_name = data.get('hospital_name')

            # Validate all fields are present
            if not all([user_id, blood_type, date, time_slot, hospital_name]):
                return jsonify({'error': 'All fields are required!'}), 400

            # Additional validation for date and time formats
            try:
                datetime.strptime(date, '%Y-%m-%d')
                datetime.strptime(time_slot, '%H:%M')
            except ValueError:
                return jsonify({'error': 'Invalid date or time format.'}), 400

            # Insert into the appointments table
            conn = get_db_connection()
            if conn is None:
                return jsonify({'error': 'Database connection failed.'}), 500
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO appointments (user_id, blood_type, date, time, hospital_name)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, blood_type, date, time_slot, hospital_name))
            conn.commit()
            conn.close()

            # Respond with success message and redirect URL
            return jsonify({'message': 'Appointment successfully scheduled!', 'redirect_url': url_for('donation_history')}), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 500


@app.route('/gamification')
def gamification():
    if 'logged_in' in session:
        user_id = session['user_id']  # Get the logged-in user's ID
        conn = get_db_connection()
        cursor = conn.cursor()

        # Query to get badges, medals, and donations for the logged-in user
        cursor.execute('''
            SELECT badges, medals, donations
            FROM badges
            WHERE user_id = ?
        ''', (user_id,))
        stats = cursor.fetchone()
        badges, medals, donations = stats if stats else (0, 0, 0)

        # Query to get the leaderboard (top 5 users sorted by donations)
        cursor.execute('''
            SELECT u.username, b.donations
            FROM badges b
            JOIN users u ON b.user_id = u.id
            ORDER BY b.donations DESC
            LIMIT 5
        ''')
        leaderboard = cursor.fetchall()

        conn.close()

        # Pass the stats and leaderboard data to the template
        return render_template('gamification.html', 
                               badges=badges, 
                               medals=medals, 
                               donations=donations, 
                               leaderboard=leaderboard)
    
    flash("Please log in to access the gamification page.", 'error')
    return redirect(url_for('login'))

@app.route('/donation-history')
def donation_history():
    if 'logged_in' in session:
        user_id = session['user_id']  # Get the logged-in user's ID
        conn = get_db_connection()
        cursor = conn.cursor()

        # Query to get user's information
        cursor.execute('''
            SELECT username, email
            FROM users
            WHERE id = ?
        ''', (user_id,))
        user_info = cursor.fetchone()

        # Query to get donation history from the appointments table
        cursor.execute('''
            SELECT date, time, hospital_name, blood_type
            FROM appointments
            WHERE user_id = ?
            ORDER BY date DESC
        ''', (user_id,))
        appointments = cursor.fetchall()

        # Generate random statuses for each appointment
        donation_history = []
        statuses = ['Completed', 'In-progress', 'Pending']
        for appointment in appointments:
            donation_history.append({
                'date': appointment['date'],
                'time': appointment['time'],
                'hospital_name': appointment['hospital_name'],
                'blood_type': appointment['blood_type'],
                'order_amount': 400,  # Assuming each donation is 400ml
                'status': random.choice(statuses)  # Random status
            })

        conn.close()

        # Pass data to the template
        return render_template('donation-history.html',
                               user_info=user_info,
                               total_amount=len(donation_history) * 400,
                               donation_history=donation_history)

    flash("Please log in to access your donation history.", 'error')
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE LOWER(email) = LOWER(?)", (email,))
        user = cursor.fetchone()
        conn.close()

        if user is None:
            # Return JSON response for no account found
            return jsonify({"status": "error", "message": "No account found with this email. Please register."})

        if user['password'] != password:
            # Return JSON response for incorrect password
            return jsonify({"status": "error", "message": "Incorrect password. Please try again."})

        # Successful login
        session['logged_in'] = True
        session['user_id'] = user['id']
        session['username'] = user['username']
        return jsonify({"status": "redirect", "redirect_url": url_for('gamification')})

    return render_template('login.html')

# Route for registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash("Passwords do not match. Please try again.", 'error')
            return redirect(url_for('register'))

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash("An account with this email already exists. Please log in.", 'error')
            conn.close()
            return redirect(url_for('register'))

        cursor.execute('''
            INSERT INTO users (username, email, password, full_name)
            VALUES (?, ?, ?, ?)
        ''', (username, email, password, full_name))
        conn.commit()
        conn.close()

        flash("Registration successful! Redirecting to login page...", 'success')
        return render_template('register.html', redirect_to_login=True)

    return render_template('register.html')

# 1. Fixed the get_user route by adding the route decorator
@app.route('/get_user', methods=['GET'])
def get_user():
    user_id = session.get('user_id')  # Retrieve user_id from session
    if user_id:
        return jsonify({'user_id': user_id})
    else:
        return jsonify({'error': 'User not logged in'}), 401



# Route for logout
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
