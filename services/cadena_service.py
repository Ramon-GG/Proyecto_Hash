import json
import sqlite3

from config import CODIGO_GENESIS, HASH_GENESIS
from entities.registro import Registro
from repositories.registro_repository import RegistroRepository
from services.hash_service import calcular_hash
from utils.fechas import ahora_utc
from utils.validaciones import validar_codigo
from entities.resultado import Resultado


def _armar_datos(codigo: str) -> str:
    return json.dumps({"codigo": codigo}, separators=(",", ":"))


class CadenaService:
    def __init__(self, con: sqlite3.Connection):
        self.con = con
        self.repo = RegistroRepository(con)

    def inicializar(self) -> None:
        """Crea el bloque génesis si la cadena está vacía."""
        if self.repo.obtener_ultimo() is not None:
            return
        datos = _armar_datos(CODIGO_GENESIS)
        ts = ahora_utc()
        h = calcular_hash(0, ts, datos, HASH_GENESIS)
        with self.con:
            self.repo.insertar(Registro(0, ts, datos, HASH_GENESIS, h))

    def agregar_entrada(self, codigo: str) -> Registro:
        """Agrega una entrada al final de la cadena."""
        codigo = validar_codigo(codigo)
        self.con.execute("BEGIN IMMEDIATE")
        try:
            ultimo = self.repo.obtener_ultimo()
            if ultimo is None:
                raise RuntimeError("La cadena no está inicializada")
            nuevo_id = ultimo.id + 1
            datos = _armar_datos(codigo)
            ts = ahora_utc()
            h = calcular_hash(nuevo_id, ts, datos, ultimo.hash_actual)
            nuevo = Registro(nuevo_id, ts, datos, ultimo.hash_actual, h)
            self.repo.insertar(nuevo)
            self.con.commit()
            return nuevo
        except Exception:
            self.con.rollback()
            raise

    def listar(self) -> list[Registro]:
        return self.repo.listar_todos()

    def verificar(self) -> Resultado:
        """Recorre la cadena, recalcula cada hash y revisa los enlaces."""
        registros = self.repo.listar_todos()
        if not registros:
            return Resultado(
                False, 0, None, "La cadena está vacía (falta el bloque génesis)"
            )

        anterior = None
        for posicion, r in enumerate(registros):
            # 1. Los id deben ser consecutivos desde 0 (detecta registros borrados)
            if r.id != posicion:
                return Resultado(
                    False, posicion, r.id,
                    f"Falta un registro antes de este (se esperaba el id {posicion})",
                )

            # 2. El prev_hash debe coincidir con el hash del registro anterior
            esperado = HASH_GENESIS if anterior is None else anterior.hash_actual
            if r.prev_hash != esperado:
                return Resultado(
                    False, posicion, r.id,
                    "El prev_hash no coincide con el hash del registro anterior",
                )

            # 3. El hash guardado debe coincidir con el recalculado
            recalculado = calcular_hash(r.id, r.timestamp, r.datos, r.prev_hash)
            if recalculado != r.hash_actual:
                return Resultado(
                    False, posicion, r.id,
                    "El hash guardado no coincide con el recalculado (contenido alterado)",
                )

            anterior = r

        return Resultado(True, len(registros))

    