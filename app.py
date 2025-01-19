from flask import Flask, render_template, redirect, url_for, request, session, flash, jsonify
import sqlite3
from flask_mail import Mail, Message
from email.mime.text import MIMEText
from datetime import datetime, timedelta
import random

app = Flask(__name__)

# Secret key (for session management if needed in the future)
app.secret_key = 'your_secret_key'

# Flask-Mail Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'BbloodBbank@gmail.com'  
app.config['MAIL_PASSWORD'] = 'orpc jhqk rekr wrst'      
app.config['MAIL_DEFAULT_SENDER'] = 'BbloodBbank@gmail.com'

mail = Mail(app)




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

            # Update the badges table for the user
            cursor.execute('SELECT badges, medals FROM badges WHERE user_id = ?', (user_id,))
            user_badges = cursor.fetchone()

            if user_badges:
                # Increment badges and check for medal award
                new_badges = user_badges['badges'] + 1
                new_medals = user_badges['medals']

                if new_badges % 10 == 0:  # Award a medal every 10 badges
                    new_medals += 1

                cursor.execute('''
                    UPDATE badges
                    SET badges = ?, medals = ?, donations = donations + 1
                    WHERE user_id = ?
                ''', (new_badges, new_medals, user_id))
            else:
                # Create a new entry in the badges table
                initial_badges = 1
                initial_medals = 1 if initial_badges % 10 == 0 else 0
                cursor.execute('''
                    INSERT INTO badges (user_id, badges, medals, donations)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, initial_badges, initial_medals, 1))

            # Fetch user email
            cursor.execute('SELECT email FROM users WHERE id = ?', (user_id,))
            user_result = cursor.fetchone()
            if not user_result:
                conn.close()
                return jsonify({'error': 'User email not found.'}), 404

            user_email = user_result[0]

            # Commit transaction
            conn.commit()

            # Send email confirmation
            # Send email confirmation
            email_body = f"""
            <html>
                <body style="margin: 0; padding: 0; background-color: #f4f4f4; font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
                    <table align="center" width="600" style="background-color: #ffffff; border: 1px solid #ddd; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1); margin-top: 20px;">
                        <tr style="background-color: #d9534f; color: #ffffff;">
                            <td style="padding: 20px; text-align: center;">
                                <h1 style="margin: 0; font-size: 24px;">💉 Blood Bank Management</h1>
                                <p style="margin: 5px 0 0; font-size: 16px;">Your life-saving appointment is confirmed!</p>
                            </td>
                        </tr>
                        <tr>
                            <td style="padding: 30px;">
                                <p style="font-size: 18px;">Hello,</p>
                                <p style="font-size: 16px; color: #555;">
                                    Thank you for scheduling your blood donation appointment. Your efforts are invaluable in saving lives. Here are the details of your appointment:
                                </p>
                                <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                                    <tr>
                                        <td style="padding: 10px; background-color: #f9f9f9; font-size: 16px; font-weight: bold; width: 30%;">📅 Date:</td>
                                        <td style="padding: 10px; background-color: #f9f9f9; font-size: 16px;">{date}</td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 10px; font-size: 16px; font-weight: bold;">⏰ Time:</td>
                                        <td style="padding: 10px; font-size: 16px;">{time_slot}</td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 10px; background-color: #f9f9f9; font-size: 16px; font-weight: bold;">🏥 Hospital:</td>
                                        <td style="padding: 10px; background-color: #f9f9f9; font-size: 16px;">{hospital_name}</td>
                                    </tr>
                                </table>
                                <div style="margin: 20px 0; padding: 15px; background-color: #dff0d8; border-left: 5px solid #3c763d; font-size: 16px;">
                                    🎉 <strong>Congratulations!</strong> You have earned a new badge for your donation. Keep making a difference!
                                </div>
                                <p style="font-size: 16px; color: #555;">
                                    If you have any questions or need to make changes to your appointment, don't hesitate to reach out to us at <a href="mailto:bbloodbank@gmail.com" style="color: #d9534f; text-decoration: none;">bbloodbank@gmail.com</a>.
                                </p>
                                <p style="text-align: center; font-size: 14px; color: #999; margin-top: 30px;">
                                    Blood Bank Management Team<br>💉 Saving Lives, One Drop at a Time
                                </p>
                            </td>
                        </tr>
                    </table>
                </body>
            </html>
            """

            try:
                msg = Message(
                    subject="Appointment Confirmation",
                    recipients=[user_email],
                    html=email_body
                )
                mail.send(msg)
                print(f"Email sent successfully to {user_email}")
            except Exception as email_error:
                print("Failed to send email:", email_error)
                return jsonify({'error': 'Failed to send email confirmation.'}), 500

            # Close the database connection
            conn.close()

            # Respond with success message and redirect URL
            return jsonify({
                'message': 'Appointment successfully scheduled! You have received a badge! Confirmation email sent!',
                'redirect_url': url_for('donation_history')
            }), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 500

from datetime import datetime, timedelta

@app.route('/win-badge', methods=['POST'])
def win_badge():
    if 'logged_in' not in session:
        flash("Please log in to win a badge.", 'error')
        return redirect(url_for('login'))
    
    user_id = session.get('user_id')
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Check number of games played today
        today = datetime.now().date()
        cursor.execute('''
            SELECT COUNT(*) as games_today 
            FROM badge_awards 
            WHERE user_id = ? 
            AND date(timestamp) = date(?)
        ''', (user_id, today))
        result = cursor.fetchone()
        games_today = result['games_today'] if result else 0

        if games_today >= 5:
            conn.close()
            flash("You've reached your daily limit of 5 games. Please come back tomorrow!", 'error')
            return redirect(url_for('game'))

        # Verify game completion status from session
        if not session.get('game_completed', False):
            conn.close()
            flash("Complete the game first to earn a badge!", 'error')
            return redirect(url_for('game'))

        # Record badge award timestamp
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS badge_awards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            INSERT INTO badge_awards (user_id)
            VALUES (?)
        ''', (user_id,))

        # Increment the user's badges
        cursor.execute('''
            UPDATE badges
            SET badges = badges + 1
            WHERE user_id = ?
        ''', (user_id,))

        # Check if the user exists in the badges table; if not, insert a new entry
        if cursor.rowcount == 0:
            cursor.execute('''
                INSERT INTO badges (user_id, badges, medals, donations)
                VALUES (?, 1, 0, 0)
            ''', (user_id,))

        # Clear the game completion status
        session.pop('game_completed', None)

        conn.commit()
        conn.close()

        flash("Congratulations! You've won a badge!", 'success')
        return redirect(url_for('gamification'))
        
    except Exception as e:
        conn.close()
        flash("An error occurred while awarding the badge. Please try again.", 'error')
        return redirect(url_for('game'))

@app.route('/game')
def game():
    if 'logged_in' not in session:
        flash("Please log in to access the game.", 'error')
        return redirect(url_for('login'))

    try:
        user_id = session['user_id']
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check number of games played today
        today = datetime.now().date()
        
        # First, ensure the badge_awards table exists
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS badge_awards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            SELECT COUNT(*) as games_today 
            FROM badge_awards 
            WHERE user_id = ? 
            AND date(timestamp) = date(?)
        ''', (user_id, today))
        
        result = cursor.fetchone()
        games_today = result[0] if result else 0  # Changed from result['games_today']
        games_remaining = 5 - games_today

        conn.close()

        # Reset game completion status when starting a new game
        session.pop('game_completed', None)

        # Always return the template regardless of games_remaining
        return render_template(
            'game.html',
            games_remaining=games_remaining,
            games_played=games_today
        )

    except Exception as e:
        print(f"Error in game route: {e}")  # Add debugging
        if 'conn' in locals():
            conn.close()
        flash("An error occurred while loading the game.", 'error')
        return redirect(url_for('gamification'))

# Add this new route to handle game completion
@app.route('/complete-game', methods=['POST'])
def complete_game():
    if 'logged_in' not in session:
        return jsonify({'success': False, 'message': 'Please log in'}), 401
    
    # Set the game completion flag
    session['game_completed'] = True
    return jsonify({'success': True, 'message': 'Game completion recorded'})

@app.route('/gamification')
def gamification():
    if 'logged_in' in session:
        user_id = session['user_id']  # Get the logged-in user's ID

        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch badges, medals, and donations from the badges table
        cursor.execute('''
            SELECT badges, medals, donations
            FROM badges
            WHERE user_id = ?
        ''', (user_id,))
        stats = cursor.fetchone()

        # Game badges directly from the table
        badges_from_game = stats['badges'] if stats else 0
        total_donations = stats['donations'] if stats else 0
        total_medals = stats['medals'] if stats else 0

        # Donations from the appointments table
        cursor.execute('''
            SELECT COUNT(*) AS donations
            FROM appointments
            WHERE user_id = ?
        ''', (user_id,))
        donations_result = cursor.fetchone()
        appointments_donations = donations_result['donations'] if donations_result else 0

        # Synchronize the donations in the badges table
        if total_donations != appointments_donations:
            cursor.execute('''
                UPDATE badges
                SET donations = ?
                WHERE user_id = ?
            ''', (appointments_donations, user_id))
            conn.commit()
            total_donations = appointments_donations

        # Total badges = game badges + donations
        total_badges = badges_from_game + total_donations

        # Dynamically calculate the number of unique hospitals
        cursor.execute('''
            SELECT COUNT(DISTINCT hospital_name) AS unique_hospitals
            FROM appointments
            WHERE user_id = ?
        ''', (user_id,))
        hospitals_result = cursor.fetchone()
        unique_hospitals = hospitals_result['unique_hospitals'] if hospitals_result else 0

        # Query to get the leaderboard (top 5 users sorted by donations)
        cursor.execute('''
            SELECT u.username, 
                   b.donations AS total_donations
            FROM users u
            LEFT JOIN badges b ON u.id = b.user_id
            ORDER BY total_donations DESC
            LIMIT 5
        ''')
        leaderboard = cursor.fetchall()

        conn.close()

        # Pass the stats and leaderboard data to the template
        return render_template('gamification.html', 
                               badges=total_badges,  # Use total badges
                               medals=total_medals, 
                               donations=total_donations,  # Donations directly reflect appointments
                               unique_hospitals=unique_hospitals, 
                               leaderboard=leaderboard)
    print(f"Game badges: {badges_from_game}, Donations: {total_donations}, Total Badges: {total_badges}")

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

        # Count the total number of donations (ignoring status)
        total_donations = len(appointments)

        # Generate statuses for each appointment (random for display only)
        donation_history = []
        statuses = ['Completed', 'In-progress', 'Pending']
        for appointment in appointments:
            donation_history.append({
                'date': appointment['date'],
                'time': appointment['time'],
                'hospital_name': appointment['hospital_name'],
                'blood_type': appointment['blood_type'],
                'status': random.choice(statuses)  # Random status for display
            })

        conn.close()

        # Pass data to the template
        return render_template('donation-history.html',
                               user_info=user_info,
                               total_donations=total_donations,
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
            return jsonify({"status": "error", "message": "No account found with this email. Please register."})

        if user['password'] != password:
            return jsonify({"status": "error", "message": "Incorrect password. Please try again."})

        # Successful login
        session['logged_in'] = True
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['is_admin'] = bool(user['is_admin'])  # Convert SQLite integer to boolean

        # Redirect based on user role
        if session['is_admin']:
            return jsonify({"status": "redirect", "redirect_url": url_for('admin_dashboard')})
        else:
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

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('logged_in') or not session.get('is_admin'):
        flash("Access Denied. Admins Only!", "danger")
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    # Obține totalul utilizatorilor
    cursor.execute("SELECT COUNT(*) AS total_users FROM users")
    total_users = cursor.fetchone()['total_users']

    # Obține totalul donațiilor
    cursor.execute("SELECT COUNT(*) AS total_donations FROM appointments")
    total_donations = cursor.fetchone()['total_donations']

    # Obține totalul programărilor active (în viitor)
    cursor.execute("""
        SELECT COUNT(*) AS active_appointments
        FROM appointments
        WHERE date >= DATE('now')
    """)
    active_appointments = cursor.fetchone()['active_appointments']

    # Obține activitatea recentă
    cursor.execute("""
        SELECT u.username AS user, 
               'Scheduled donation' AS action, 
               a.date || ' ' || a.time AS date
        FROM appointments a
        JOIN users u ON a.user_id = u.id
        ORDER BY a.date DESC, a.time DESC
        LIMIT 10
    """)
    recent_activity = cursor.fetchall()

    conn.close()

    # Trimite datele către template
    return render_template(
        'admin_dashboard.html',
        total_users=total_users,
        total_donations=total_donations,
        active_appointments=active_appointments,
        recent_activity=recent_activity
    )

@app.route('/admin/users')
def admin_users():
    if not session.get('logged_in') or not session.get('is_admin'):
        flash("Access Denied. Admins Only!", "danger")
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    # Obține lista utilizatorilor
    cursor.execute("""
        SELECT id, username, email, 
               CASE WHEN is_admin = 1 THEN 'Admin' ELSE 'User' END AS role
        FROM users
        ORDER BY username
    """)
    users = cursor.fetchall()

    conn.close()

    # Trimite datele către template
    return render_template('users.html', users=users)

@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if not session.get('logged_in') or not session.get('is_admin'):
        flash("Access Denied. Admins Only!", "danger")
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    # Șterge utilizatorul din baza de date
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()

    flash("User deleted successfully.", "success")
    return redirect(url_for('admin_users'))

@app.route('/admin/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if not session.get('logged_in') or not session.get('is_admin'):
        flash("Access Denied. Admins Only!", "danger")
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        # Obține datele din formular
        username = request.form.get('username')
        email = request.form.get('email')
        is_admin = 1 if request.form.get('is_admin') == 'on' else 0

        # Actualizează utilizatorul în baza de date
        cursor.execute("""
            UPDATE users
            SET username = ?, email = ?, is_admin = ?
            WHERE id = ?
        """, (username, email, is_admin, user_id))
        conn.commit()
        conn.close()

        flash("User updated successfully.", "success")
        return redirect(url_for('admin_users'))
    else:
        # Obține datele utilizatorului
        cursor.execute("SELECT id, username, email, is_admin FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        conn.close()

        return render_template('edit_user.html', user=user)

# Gestionare donații
@app.route('/admin/donations')
def admin_donations():
    # Verifică dacă utilizatorul este autentificat și are rol de admin
    if not session.get('logged_in') or not session.get('is_admin'):
        flash("Access Denied. Admins Only!", "danger")
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    # Interogare SQL pentru a obține toate donațiile
    cursor.execute("""
        SELECT 
            u.username AS donor,
            a.date,
            a.time,
            '400ml' AS amount,  
            CASE
                WHEN a.date < DATE('now') THEN 'Completed'
                WHEN a.date = DATE('now') THEN 'In-progress'
                ELSE 'Pending'
            END AS status
        FROM appointments a
        JOIN users u ON a.user_id = u.id
        ORDER BY a.date DESC
    """)
    donations = cursor.fetchall()

    conn.close()

    # Trimite datele către template
    return render_template('donations.html', donations=donations)








# Route for logout
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

