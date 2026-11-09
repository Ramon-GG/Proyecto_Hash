"""from database.connection import conectar, crear_base
from services.cadena_service import CadenaService

crear_base()
con = conectar()
cadena = CadenaService(con)
cadena.inicializar()

while True:
    print("\n1) Registrar entrada  2) Ver cadena  3) Verificar integridad  0) Salir")
    opcion = input("Opción: ").strip()

    if opcion == "1":
        cod = input("Código de alumno (9 dígitos) o maestro (7): ")
        try:
            r = cadena.agregar_entrada(cod)
            print(f"Entrada registrada (id {r.id}) a las {r.timestamp}")
        except ValueError as e:
            print("Rechazado:", e)

    elif opcion == "2":
        for r in cadena.listar():
            print(r)

    elif opcion == "3":
        res = cadena.verificar()
        if res.valida:
            print(f"Cadena VÁLIDA ({res.registros_revisados} registros verificados)")
        else:
            print(f"Cadena ALTERADA en el registro {res.id_roto}: {res.motivo}")

    else:
        break

con.close()"""