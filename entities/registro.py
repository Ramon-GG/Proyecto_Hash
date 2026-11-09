from dataclasses import dataclass


@dataclass(frozen=True)
class Registro:
    id: int
    timestamp: str
    datos: str
    prev_hash: str
    hash_actual: str

    