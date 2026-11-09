import sqlite3

from entities.registro import Registro

class RegistroRepository:
    def __init__(self, con: sqlite3.Connection):
        self.con = con

    def insertar(self, registro: Registro) -> None:
        self.con.execute(
            "INSERT INTO registros (id, timestamp, datos, prev_hash, hash_actual) "
            "VALUES (?, ?, ?, ?, ?)",
            (registro.id, registro.timestamp, registro.datos,
             registro.prev_hash, registro.hash_actual),
        )

    def obtener_ultimo(self) -> Registro | None:
        fila = self.con.execute(
            "SELECT id, timestamp, datos, prev_hash, hash_actual "
            "FROM registros ORDER BY id DESC LIMIT 1"
        ).fetchone()
        return Registro(*fila) if fila else None

    def listar_todos(self) -> list[Registro]:
        filas = self.con.execute(
            "SELECT id, timestamp, datos, prev_hash, hash_actual "
            "FROM registros ORDER BY id ASC"
        ).fetchall()
        return [Registro(*fila) for fila in filas]
    