import json

from flask import Flask, app, request

from config import SECRET_KEY
from database.connection import conectar, crear_base
from services.cadena_service import CadenaService
from utils.fechas import a_local
from controller.contoller import bp


def crear_app() -> Flask:
    app = Flask(__name__, template_folder="web/templates", static_folder="web/static")
    app.secret_key = SECRET_KEY

    # Filtros para usar dentro de las plantillas
    app.jinja_env.filters["hora_local"] = a_local
    app.jinja_env.filters["codigo"] = _codigo
 

    app.register_blueprint(bp)
    print("Static:", app.static_folder)
    print("Templates:", app.jinja_loader.searchpath)
    # Al arrancar: asegurar que la tabla exista y que haya bloque génesis
    crear_base()
    con = conectar()
    try:
        CadenaService(con).inicializar()
    finally:
        con.close()
    return app

def preparar_base() -> None:
    """Garantiza que existan la tabla y el bloque génesis."""
    crear_base()
    con = conectar()
    try:
        CadenaService(con).inicializar()
    finally:
        con.close()

def _codigo(datos: str) -> str:
    """Extrae el código del JSON de 'datos'; si fue alterado, muestra el texto tal cual."""
    try:
        return json.loads(datos).get("codigo", datos)
    except (ValueError, AttributeError):
        return datos






if __name__ == "__main__":
    crear_app().run(debug=True)