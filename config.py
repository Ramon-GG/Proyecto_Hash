from pathlib import Path

# Carpeta principal del proyecto (donde está este archivo)
BASE_DIR = Path(__file__).parent

# Ruta de la base de datos SQLite
DB_PATH = BASE_DIR / "biblioteca.db"

# prev_hash del primer registro (bloque génesis): 64 ceros
HASH_GENESIS = "0" * 64

# codigo inicial para el primer registro
CODIGO_GENESIS = "000000000"

# Clave secreta para firmar las cookies de sesión de Flask
SECRET_KEY = "cambia-esta-clave-en-produccion"