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

            # Fetch the user's current stats from the badges table
            cursor.execute('''
                SELECT badges, medals, donations
                FROM badges
                 WHERE user_id = ?
                ''', (user_id,))
            user_badges = cursor.fetchone()

            if user_badges:
                    # Update existing user stats
                new_badges = user_badges['badges'] + 1
                new_medals = new_badges // 10  # Calculate medals based on total badges
                new_donations = user_badges['donations'] + 1

                cursor.execute('''
        UPDATE badges
        SET badges = ?, medals = ?, donations = ?
        WHERE user_id = ?
    ''', (new_badges, new_medals, new_donations, user_id))
            else:
               # Create a new entry for a user without existing stats
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

@app.route('/win_game', methods=['POST'])
def win_game():
    if 'user_id' not in session:
        return jsonify({"error": "Not logged in"}), 403

    user_id = session['user_id']
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Increment the badge count for the user
        cursor.execute('''
            UPDATE badges
            SET badges = badges + 1
            WHERE user_id = ?
        ''', (user_id,))

        # Log the game win in the badge_awards table
        cursor.execute('''
            INSERT INTO badge_awards (user_id, timestamp)
            VALUES (?, DATETIME('now'))
        ''', (user_id,))

        conn.commit()
        return jsonify({"message": "Badge awarded and game logged."}), 200

    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500

    finally:
        conn.close()

@app.route('/game')
def game():
    if 'logged_in' not in session:
        flash("Please log in to access the game.", 'error')
        return redirect(url_for('login'))

    # Logic for checking remaining games and rendering the game page
    try:
        user_id = session['user_id']
        conn = get_db_connection()
        cursor = conn.cursor()

        today = datetime.now().date()

        # Check games played today
        cursor.execute('''
            SELECT COUNT(*) as games_today
            FROM badge_awards
            WHERE user_id = ? AND DATE(timestamp) = ?
        ''', (user_id, today))
        result = cursor.fetchone()
        games_today = result[0] if result else 0
        games_remaining = max(0, 5 - games_today)

        conn.close()

        if games_remaining <= 0:
            flash("You have reached the game limit for today.", 'error')
            return redirect(url_for('gamification'))

        return render_template('game.html', games_remaining=games_remaining, games_played=games_today)

    except sqlite3.Error as e:
        flash(f"An error occurred: {e}", 'error')
        return redirect(url_for('dashboard'))

@app.route('/check_game_limit')
def check_game_limit():
    if 'user_id' not in session:
        return jsonify({"error": "Not logged in"}), 403

    user_id = session['user_id']
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Count games played today
        cursor.execute('''
            SELECT COUNT(*) FROM badge_awards
            WHERE user_id = ? AND DATE(timestamp) = DATE('now')
        ''', (user_id,))
        games_today = cursor.fetchone()[0]

        remaining_games = max(0, 5 - games_today)  # Limit is 5 games per day
        return jsonify({"remaining_games": remaining_games})

    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500

    finally:
        conn.close()

@app.route('/gamification')
def gamification():
    if 'logged_in' not in session:
        flash("Please log in to access the gamification page.", 'error')
        return redirect(url_for('login'))

    user_id = session['user_id']  # Get the logged-in user's ID

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch badges, medals, and donations from the badges table
        cursor.execute('''
            SELECT badges, medals, donations
            FROM badges
            WHERE user_id = ?
        ''', (user_id,))
        stats = cursor.fetchone()

        # Extract stats or set defaults
        badges = stats['badges'] if stats else 0
        medals = stats['medals'] if stats else 0
        donations = stats['donations'] if stats else 0

        # Determine if the user is eligible for a voucher
        has_voucher = donations >= 10

        # Dynamically calculate the number of unique hospitals
        cursor.execute('''
            SELECT COUNT(DISTINCT hospital_name) AS unique_hospitals
            FROM appointments
            WHERE user_id = ?
        ''', (user_id,))
        hospitals_result = cursor.fetchone()

        unique_hospitals = hospitals_result['unique_hospitals'] if hospitals_result else 0

        # Query for leaderboard (top 5 users by donations)
        cursor.execute('''
            SELECT u.username, 
                   b.donations AS total_donations
            FROM users u
            LEFT JOIN badges b ON u.id = b.user_id
            ORDER BY total_donations DESC
            LIMIT 5
        ''')
        leaderboard = cursor.fetchall()

        # Pass data to the gamification template
        return render_template(
            'gamification.html',
            badges=badges,
            medals=medals,
            donations=donations,
            unique_hospitals=unique_hospitals,
            leaderboard=leaderboard,
            has_voucher=has_voucher  # Pass eligibility for voucher to the template
        )

    except sqlite3.Error as e:
        flash(f"An error occurred while fetching gamification data: {e}", 'error')
        return redirect(url_for('dashboard'))
    finally:
        conn.close()

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


@app.route('/check_donations', methods=['POST'])
def check_donations():
    if 'user_id' not in session:
        return jsonify({"error": "Not logged in"}), 403

    user_id = session['user_id']
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Debug: Log the user ID
        print(f"Checking donations for user_id: {user_id}")

        # Fetch the number of donations and meal vouchers
        cursor.execute('''
            SELECT donations, meal_vouchers FROM badges WHERE user_id = ?
        ''', (user_id,))
        user_data = cursor.fetchone()

        # Debug: Log the user data fetched
        print(f"User data fetched: {user_data}")

        if user_data:
            donations = user_data['donations']
            meal_vouchers = user_data['meal_vouchers']

            # Calculate the new vouchers based on donations
            

            # Debug: Log calculations
            print(f"Donations: {donations}, Meal Vouchers: {meal_vouchers}")

            if meal_vouchers > 0:
                
                cursor.execute('''
                    UPDATE badges
                    SET meal_vouchers = ?
                    WHERE user_id = ?
                ''', (meal_vouchers, user_id))
                conn.commit()

                return jsonify({
                    "message": f"Felicitări! Ai câștigat {meal_vouchers} bonuri de masă.",
                    "total_vouchers": meal_vouchers
                }), 200

        return jsonify({"message": "Nu ai suficient donații pentru a câștiga bonuri de masă."}), 200

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return jsonify({"error": str(e)}), 500

    finally:
        conn.close()



import qrcode
import io
import base64
from flask import send_file

@app.route('/voucher-page')
def voucher_page():
    if 'logged_in' in session:
        user_id = session['user_id']

        conn = get_db_connection()
        cursor = conn.cursor()

        # Get donations for the user
        cursor.execute('''
            SELECT donations
            FROM badges
            WHERE user_id = ?
        ''', (user_id,))
        result = cursor.fetchone()
        donations = result['donations'] if result else 0

        # Check if the user has enough donations to claim a voucher
        if donations < 10:
            flash("You need at least 10 donations to claim a voucher!", "error")
            return redirect(url_for('gamification'))

        # Lists of restaurants/shops
        restaurants = [
            'Caru\' cu Bere',
            'Hanul Berarilor',
            'Zexe Braserie',
            'Hanu\' lui Manuc',
            'Taverna Sârbului',
            'Nor Sky Casual Restaurant',
            'Vivo - Fusion Food Bar',
            'Shift Pub',
            'Sushi Room',
            'Mahala'
        ]

        shops = [
            'AFI Cotroceni - Mall',
            'Mega Mall București',
            'Unirea Shopping Center',
            'Promenada Mall',
            'Băneasa Shopping City',
            'Cărturești Carusel - Librărie',
            'Altex - Unirii',
            'Dedeman - Militari',
            'Emag Showroom - Crângași',
            'Decathlon - Băneasa'
        ]

        # Generate QR code for the voucher
        qr_data = f"User ID: {user_id}, Donations: {donations}, Voucher ID: {user_id}-voucher"
        qr = qrcode.make(qr_data)

        # Save QR code to an in-memory file
        qr_io = io.BytesIO()
        qr.save(qr_io, 'PNG')
        qr_io.seek(0)
        qr_code_base64 = base64.b64encode(qr_io.getvalue()).decode('utf-8')
        qr_code_url = f"data:image/png;base64,{qr_code_base64}"

        return render_template(
            'voucher_page.html',
            restaurants=restaurants,
            shops=shops,
            qr_code_url=qr_code_url
        )
    else:
        flash("Please log in to access the voucher page.", "error")
        return redirect(url_for('login'))




# Route for logout
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

