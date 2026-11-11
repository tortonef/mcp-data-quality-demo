"""Crea data/crm.db e lo popola con dati intenzionalmente 'sporchi'
per dimostrare controlli di data quality: completezza, duplicati,
formato/validita, integrita referenziale.

Idempotente: ricrea le tabelle da zero ogni esecuzione.
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "crm.db"

SCHEMA = """
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS customers;

CREATE TABLE customers (
    id INTEGER PRIMARY KEY,
    full_name TEXT,
    email TEXT,
    phone TEXT,
    created_at TEXT
);

CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    amount REAL,
    status TEXT,
    created_at TEXT
);
"""

CUSTOMERS = [
    (1, "Maria Rossi", "maria.rossi@example.com", "+39 333 1234567", "2024-01-10"),
    (2, "Luca Bianchi", "luca.bianchi@example.com", "+39 333 7654321", "2024-02-15"),
    # completezza: nome ed email mancanti
    (3, None, None, "333 0000000", "2024-02-20"),
    (4, "Anna Verdi", "", "+39 334 1112222", "2024-03-01"),
    # duplicato: stessa email di id=1, record diverso
    (5, "Maria Rossi", "maria.rossi@example.com", "+39 333 9998888", "2024-03-05"),
    # formato non valido: email senza @, telefono con lettere
    (6, "Paolo Neri", "paolo.neri_at_example.com", "non-un-numero", "2024-03-10"),
    # formato non valido: data malformata
    (7, "Giulia Ferrari", "giulia.ferrari@example.com", "+39 335 4445555", "10/03/2024???"),
    (8, "Marco Costa", "marco.costa@example.com", "+39 336 5556666", "2024-04-01"),
]

ORDERS = [
    (1, 1, 120.50, "completed", "2024-01-15"),
    (2, 2, 89.90, "completed", "2024-02-20"),
    (3, 8, 45.00, "pending", "2024-04-02"),
    # integrita referenziale: customer_id=99 non esiste in customers
    (4, 99, 230.00, "completed", "2024-04-10"),
]


def main() -> None:
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.executescript(SCHEMA)
        conn.executemany(
            "INSERT INTO customers (id, full_name, email, phone, created_at) VALUES (?, ?, ?, ?, ?)",
            CUSTOMERS,
        )
        conn.executemany(
            "INSERT INTO orders (id, customer_id, amount, status, created_at) VALUES (?, ?, ?, ?, ?)",
            ORDERS,
        )
        conn.commit()
    finally:
        conn.close()
    print(f"Seeded {DB_PATH} with {len(CUSTOMERS)} customers and {len(ORDERS)} orders.")


if __name__ == "__main__":
    main()
