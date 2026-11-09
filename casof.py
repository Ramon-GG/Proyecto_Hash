from database.connection import conectar
from services.hash_service import calcular_hash

NUEVOS_DATOS = '{"codigo":"999999999"}'

con = conectar()
ts, prev_hash = con.execute(
    "SELECT timestamp, prev_hash FROM registros WHERE id = 2"
).fetchone()

nuevo_hash = calcular_hash(2, ts, NUEVOS_DATOS, prev_hash)

with con:
    con.execute(
        "UPDATE registros SET datos = ?, hash_actual = ? WHERE id = 2",
        (NUEVOS_DATOS, nuevo_hash),
    )
con.close()

print("Registro 2 alterado y su hash reparado:", nuevo_hash)