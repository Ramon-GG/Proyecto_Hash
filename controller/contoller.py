from flask import Blueprint, flash, redirect, render_template, request, url_for

from database.connection import conectar
from services.cadena_service import CadenaService

bp = Blueprint("web", __name__)


@bp.get("/")
def registro():
    con = conectar()
    try:
        registros = CadenaService(con).listar()
    finally:
        con.close()
    # Las últimas 10 entradas, la más reciente primero (sin el génesis)
    recientes = [r for r in registros if r.id != 0][-10:][::-1]
    return render_template("registro.html", recientes=recientes)


@bp.post("/registrar")
def registrar():
    codigo = request.form.get("codigo", "")
    con = conectar()
    try:
        r = CadenaService(con).agregar_entrada(codigo)
        #flash(f"Entrada registrada (registro {r.id})", "ok")
    except ValueError as e:
        flash(str(e), "error")
    finally:
        con.close()
    return redirect(url_for("web.registro"))

@bp.get("/cadena")
def cadena():
    con = conectar()
    try:
        servicio = CadenaService(con)
        registros = servicio.listar()
        # Solo verifica si se pidió con el botón (?verificar=1)
        resultado = servicio.verificar() if request.args.get("verificar") else None
    finally:
        con.close()
    return render_template("cadena.html", registros=registros, resultado=resultado)

    @app.before_request
    def asegurar_base():
        if request.endpoint != "static":   # no hace falta para el CSS ni las imágenes
            preparar_base()