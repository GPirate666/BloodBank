import sqlite3

def alter_table_add_is_admin():
    try:
        # Conectare la baza de date
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Adaugă coloana `is_admin` dacă nu există
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'is_admin' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT 0")
            print("Coloana `is_admin` a fost adăugată în tabelul `users`.")
        else:
            print("Coloana `is_admin` există deja.")

        conn.commit()
    except sqlite3.Error as e:
        print(f"Eroare la modificarea tabelului: {e}")
    finally:
        if conn:
            conn.close()

def add_admin(full_name, username, email, password):
    try:
        # Conectare la baza de date
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Verifică dacă email-ul sau username-ul există deja
        cursor.execute("SELECT * FROM users WHERE email = ? OR username = ?", (email, username))
        existing_user = cursor.fetchone()

        if existing_user:
            print("Un utilizator cu acest email sau username există deja.")
            return

        # Inserare utilizator cu rol de admin
        cursor.execute("""
        INSERT INTO users (full_name, username, email, password, is_admin)
        VALUES (?, ?, ?, ?, ?)
        """, (full_name, username, email, password, 1))  # `is_admin` setat pe 1
        conn.commit()
        print("Adminul a fost adăugat cu succes!")

    except sqlite3.Error as e:
        print(f"Eroare la conectarea sau inserarea în baza de date: {e}")
    finally:
        if conn:
            conn.close()

# Apelează funcțiile
if __name__ == "__main__":
    # Pasul 1: Adaugă coloana `is_admin` dacă nu există
    alter_table_add_is_admin()

    # Pasul 2: Adaugă un utilizator cu rol de admin
    full_name = "Admin User"
    username = "admin"
    email = "admin@example.com"
    password = "securepassword"

    add_admin(full_name, username, email, password)
