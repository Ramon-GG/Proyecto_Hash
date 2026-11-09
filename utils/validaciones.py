import re


def validar_codigo(codigo: str) -> str:
    codigo = codigo.strip()
    if not re.fullmatch(r"[0-9]{9}|[0-9]{7}", codigo):
        raise ValueError("Código inválido: debe tener 9 dígitos (alumno) o 7 (maestro)")
    return codigo