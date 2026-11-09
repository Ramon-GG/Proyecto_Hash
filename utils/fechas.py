from datetime import datetime, timezone, timedelta

FORMATO = "%Y-%m-%dT%H:%M:%SZ"
ZONA_LOCAL = timezone(timedelta(hours=-6))


def a_local(timestamp: str) -> str:
    """Convierte el timestamp guardado (UTC) a hora local, solo para mostrarlo."""
    return a_datetime(timestamp).astimezone(ZONA_LOCAL).strftime(FORMATO)

def ahora_utc() -> str:
    return datetime.now(timezone.utc).strftime(FORMATO)


def a_datetime(timestamp: str) -> datetime:
    return datetime.strptime(timestamp, FORMATO).replace(tzinfo=timezone.utc)
