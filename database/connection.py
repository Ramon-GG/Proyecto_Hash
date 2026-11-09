import sqlite3
from config import DB_PATH


ESQUEMA = """
CREATE TABLE IF NOT EXISTS registros (
    id           INTEGER PRIMARY KEY,
    timestamp    TEXT NOT NULL,
    datos        TEXT NOT NULL,
    prev_hash    TEXT NOT NULL,
    hash_actual  TEXT NOT NULL UNIQUE
);
"""

def conectar():
    return sqlite3.connect(DB_PATH)

def crear_base():
    with conectar() as con:
        con.execute(ESQUEMA)
    print(f"Base lista en: {DB_PATH}")
