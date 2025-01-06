import sqlite3

def create_tables():
    # Conectare la baza de date (se creează dacă nu există)
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS appointments")
    # Crearea tabelei `appointments`
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS appointments (
    appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    date DATE NOT NULL,
    time TIME NOT NULL,
    hospital_name TEXT NOT NULL,
    blood_type TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id)
    )

    """)

    # Confirmare și închidere conexiune
    conn.commit()
    conn.close()
    print("Tabelele au fost create cu succes!")

# Apelarea funcției pentru a crea tabelele
if __name__ == "__main__":
    create_tables()
