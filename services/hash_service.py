import hashlib


def calcular_hash(id_registro: int, timestamp: str, datos: str, prev_hash: str) -> str:
    contenido = f"{id_registro}|{timestamp}|{datos}|{prev_hash}"
    return hashlib.sha256(contenido.encode("utf-8")).hexdigest()