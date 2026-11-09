from dataclasses import dataclass

@dataclass(frozen=True)
class Resultado:
    valida: bool
    registros_revisados: int
    id_roto: int | None = None
    motivo: str | None = None