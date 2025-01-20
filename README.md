# Blood Bank Management System

> **_Note:_** *This project is developed as part of a university assignment. It is not intended for public deployment or commercial use.*

The Blood Bank Management System is designed to streamline the process of scheduling blood donations, awarding badges and medals for contributions, and encouraging gamified engagement to promote more donations.

## 📋 Table of Contents

- [Features](#features)
- [Technologies Used](#technologies-used)
- [Installation](#installation)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Database Schema](#database-schema)
- [Backend Code Overview](#backend-code-overview)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)

---

## ⭐ Features

- **User Authentication:** Secure registration and login system with roles for users and admins.
- **Donation Scheduling:** Users can schedule appointments to donate blood, selecting dates, times, hospitals, and blood types.
- **Gamification:** Users earn badges for donations, and medals for every 10 badges.
- **Donation History:** Tracks user donations and displays stats like total donations and random statuses (e.g., Completed, Pending).
- **Email Notifications:** Sends confirmation emails after scheduling a donation.
- **Admin Dashboard:** Admins can manage users and view statistics such as total users and donations.
- **Meal Vouchers:** Users can redeem meal vouchers after a specific number of donations.
- **QR Code Generation:** Users can generate QR codes for meal vouchers.
- **Snake Game - Blood Drop:** Engage in a fun snake game where you collect blood drops to fill the health bar. Winning the game awards a badge.
---

## 🛠️ Technologies Used

- **Backend:**
  - Python 3.8+
  - Flask Framework
  - SQLite (Development)
  - Flask-Mail for email notifications

- **Frontend:**
  - HTML5
  - CSS3
  - JavaScript (ES6)

- **Other Tools:**
  - Git for version control
  - QR Code library for voucher generation

---

## 🚀 Installation

### Prerequisites

- **Python 3.8+**
- **Git**
- **Virtual Environment Tool:** `venv` (included with Python)

### Steps

1. **Clone the Repository**

    ```bash
    git clone https://github.com/GPirate666/blood-bank-management.git
    cd blood-bank-management
    ```

2. **Create a Virtual Environment**

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. **Install Dependencies**

    ```bash
    pip install Flask Flask-Mail qrcode
    ```

4. **Set Up Environment Variables**

    Create a `.env` file in the root directory and add the following configurations:

    ```env
    FLASK_APP=app.py
    FLASK_ENV=development
    SECRET_KEY=your_secret_key
    MAIL_SERVER=smtp.gmail.com
    MAIL_PORT=587
    MAIL_USE_TLS=True
    MAIL_USERNAME=your_email@gmail.com
    MAIL_PASSWORD=your_email_password
    MAIL_DEFAULT_SENDER=your_email@gmail.com
    ```

    **_Note:_** Replace `your_secret_key`, `your_email@gmail.com`, and `your_email_password` with your actual credentials.

5. **Initialize the Database**

    ```bash
    python create-tables.py
    ```

6. **Run the Application**

    ```bash
    python app.py
    ```

7. **Access the Application**

    Open your browser and navigate to [http://localhost:5000](http://localhost:5000).

---

## 📚 Usage

### Scheduling a Donation

1. Log in to your account.
2. Navigate to the "Schedule Donation" page.
3. Select your blood type, preferred date, time, and hospital.
4. Confirm the appointment. You’ll receive an email confirmation.

### Profile

1. View your badges, medals, and donation history on the "Profile" page.
2. Earn badges for each donation and medals for every 10 badges.

### Admin Features

1. Access the admin dashboard to manage users and view donation stats.
2. Monitor user activity and recent appointments.

### Redeeming Meal Vouchers

1. Once you’ve made 10 donations, you’ll be eligible for a meal voucher.
2. Generate a QR code for your voucher on the "Voucher Page."

### Playing the Snake Game

1. Navigate to the "Win a Badge" section from the profile page.
2. Control the snake using the arrow keys to collect blood drops.
3. Fill the health bar to win the game and earn a badge.
4. After earning 10 badges (from games or donations), you will be awarded a medal.

---

## 🔗 API Endpoints

### Schedule Donation

- **URL:** `/schedule`
- **Method:** `POST`
- **Description:** Schedules a new blood donation appointment.
- **Body:**
    ```json
    {
        "user_id": 1,
        "blood_type": "O+",
        "date": "2025-01-20",
        "time": "10:00",
        "hospital_name": "Spitalul Universitar"
    }
    ```

### Gamification Stats

- **URL:** `/gamification`
- **Method:** `GET`
- **Description:** Fetches user stats, badges, medals, and leaderboard information.

### Donation History

- **URL:** `/donation-history`
- **Method:** `GET`
- **Description:** Fetches the logged-in user’s donation history.

---

## 🗄️ Database Schema

### Appointments Table

| Field          | Type    | Description             |
|----------------|---------|-------------------------|
| `appointment_id` | Integer | Primary Key             |
| `user_id`       | Integer | Foreign Key (Users)     |
| `date`          | Date    | Date of the appointment |
| `time`          | Time    | Time of the appointment |
| `hospital_name` | Text    | Selected hospital       |
| `blood_type`    | Text    | User's blood type       |

### Badges Table

| Field         | Type    | Description                |
|---------------|---------|----------------------------|
| `id`          | Integer | Primary Key                |
| `user_id`     | Integer | Foreign Key (Users)        |
| `badges`      | Integer | Total badges earned        |
| `medals`      | Integer | Total medals earned        |
| `donations`   | Integer | Total donations made       |
| `meal_vouchers` | Integer | Total vouchers awarded     |

### Badge Awards Table

| Field         | Type    | Description                   |
|---------------|---------|-------------------------------|
| `id`          | Integer | Primary Key                   |
| `user_id`     | Integer | Foreign Key (Users)           |
| `timestamp`   | DateTime | Timestamp of badge awarding   |

### Users Table

| Field        | Type    | Description                    |
|--------------|---------|--------------------------------|
| `id`         | Integer | Primary Key                    |
| `full_name`  | Text    | Full name of the user          |
| `username`   | Text    | Username                       |
| `email`      | Text    | Unique email address           |
| `password`   | Text    | Encrypted user password        |
| `is_admin`   | Boolean | Admin status (True/False)      |

---

## 🖥️ Backend Code Overview

The backend handles authentication, scheduling, gamification, and email notifications.

### Key Components

#### Email Notifications

```python
msg = Message(
    subject="Appointment Confirmation",
    recipients=[user_email],
    html=email_body
)
mail.send(msg)
```

#### Gamification Badges and Medals

```python
cursor.execute('''
    UPDATE badges
    SET badges = badges + 1, 
        medals = badges // 10
    WHERE user_id = ?
''', (user_id,))
```

#### QR Code Generation for Vouchers

```python
qr_data = f"User ID: {user_id}, Donations: {donations}, Voucher ID: {user_id}-voucher"
qr = qrcode.make(qr_data)
```
#### Snake Game Badge Awarding

The `/win_game` endpoint handles the logic for awarding a badge when the user wins the snake game:

```python
@app.route('/win_game', methods=['POST'])
def win_game():
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE badges
        SET badges = badges + 1
        WHERE user_id = ?
    ''', (user_id,))

    conn.commit()
    conn.close()
    return jsonify({"message": "Badge awarded!"}), 200
```
---

## 📝 Contributing

Follow these steps to contribute:

1. **Fork the Repository**
2. **Clone Your Fork**
3. **Create a Branch**
4. **Commit Your Changes**
5. **Push to the Branch**
6. **Open a Pull Request**

---

## 📝 License

Distributed under the MIT License.

---

## 🎉 Acknowledgments

- **Flask:** For providing a robust and flexible backend framework.
- **SQLite:** For its lightweight database management.
- **Flask-Mail:** For seamless email integration.
- **Team Members and Mentors:** For their invaluable support and collaboration.
- **Community Resources:** Tutorials, forums, and documentation that aided in overcoming technical challenges.

---

Let me know if there are any more tables or adjustments needed!