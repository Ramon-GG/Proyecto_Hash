==============================================================================
 BASE DE DATOS ENCADENADA CON HASH (MINI-BLOCKCHAIN)
 Registro de ingresos a la biblioteca universitaria
==============================================================================

Proyecto final de la materia IH063 - Criptografía
Universidad de Guadalajara

Integrantes: Juan Ramon Rodriguez Armas, Carlos Samuel Fierros Garcia, Jose Luis Ramon Camacho
Profesor:    Cesar Alejandro Garcia Garcia.
Fecha:       Noviembre de 2026


------------------------------------------------------------------------------
 1. DESCRIPCIÓN GENERAL
------------------------------------------------------------------------------

El registro de ingresos a la biblioteca se llevaba en una hoja de Excel que
solo pedía el código de la persona. Este proyecto lo migra a una base de datos
con interfaz web y, además, protege el historial con una cadena de hashes,
como una versión muy sencilla de una blockchain.

Cada registro guarda el hash del registro anterior. Si alguien modifica un
registro pasado, su hash cambia, el enlace con el registro siguiente se rompe
y la aplicación lo detecta al verificar la cadena.

No es una blockchain completa: no hay consenso distribuido, ni minería, ni
red P2P. El objetivo es demostrar:

  - El cálculo de hashes criptográficos (SHA-256).
  - El encadenamiento entre registros mediante el hash anterior.
  - La detección de alteraciones a partir de los hashes.


------------------------------------------------------------------------------
 2. REQUISITOS E INSTALACIÓN
------------------------------------------------------------------------------

Requisitos:

  - Python 3.10 o superior (desarrollado con Python 3.13).
  - Flask (para la interfaz web).
  - SQLite no requiere instalación: viene incluido con Python (módulo sqlite3),
    igual que hashlib, que se usa para SHA-256.
  - Opcional: la herramienta de línea de comandos "sqlite3" o DB Browser for
    SQLite, para modificar la base a mano en la prueba de alteración.

Instalación de dependencias (desde la carpeta principal del proyecto):

    python -m pip install -r requirements.txt

Si el archivo requirements.txt no existe, instalar Flask directamente y
generarlo:

    python -m pip install flask
    python -m pip freeze > requirements.txt

Se usa "python -m pip" en lugar de "pip" para asegurar que las librerías se
instalen en el mismo Python con el que se ejecuta el proyecto.


------------------------------------------------------------------------------
 3. CÓMO EJECUTARLO
------------------------------------------------------------------------------

Todos los comandos se ejecutan desde la carpeta principal del proyecto.

 a) Versión web

        python app.py

    Abrir en el navegador: http://127.0.0.1:5000

    Páginas:
      /        Registro: captura del código y últimas entradas.
      /cadena  Cadena: tabla completa con los hashes y botón
               "Verificar integridad".

 b) Versión de consola

        python main.py

    Menú:
      1) Registrar entrada
      2) Ver cadena
      3) Verificar integridad
      0) Salir

La base de datos (biblioteca.db) se crea automáticamente la primera vez, junto
con el bloque génesis. Ambas versiones usan los mismos servicios y la misma
base de datos.

Códigos aceptados: 9 dígitos (alumnos) o 7 dígitos (maestros). Cualquier otro
formato se rechaza y no entra a la cadena.


------------------------------------------------------------------------------
 4. ESTRUCTURA DEL PROYECTO
------------------------------------------------------------------------------

El código está separado en capas. Cada capa solo depende de las inferiores:

    Proyecto_biblio/
    |-- app.py                      Arranque de la versión web (Flask)
    |-- main.py                     Interfaz de consola
    |-- config.py                   Constantes: ruta de la BD, hash génesis, etc.
    |-- requirements.txt            Dependencias
    |-- biblioteca.db               Base de datos SQLite (se crea sola)
    |-- database/
    |   '-- connection.py           Conexión y creación de la tabla
    |-- entities/
    |   |-- registro.py             Clase Registro (los 5 campos de la cadena)
    |   '-- resultado_verificacion.py   Resultado de verificar la cadena
    |-- repositories/
    |   '-- registro_repository.py  Único lugar con SQL
    |-- services/
    |   |-- hash_service.py         Cálculo del hash SHA-256
    |   '-- cadena_service.py       Génesis, agregar entradas y verificar
    |-- utils/
    |   |-- fechas.py               Timestamp en UTC y conversión a hora local
    |   '-- validaciones.py         Validación del código (7 o 9 dígitos)
    |-- controller/                 Controlador web (rutas de Flask)
    '-- web/
        |-- templates/              Plantillas HTML (base, registro, cadena)
        '-- static/                 Estilos e imágenes

(Ajustar los nombres de carpetas y archivos si cambian en la versión final.)

Correspondencia con una arquitectura MVC:
  - Vista:        web/templates y web/static
  - Controlador:  controller (rutas de Flask) y main.py
  - Modelo:       entities, services y repositories


------------------------------------------------------------------------------
 5. FUNCIONAMIENTO DE LA CADENA
------------------------------------------------------------------------------

5.1 Estructura de cada registro (tabla "registros")

    id           Número del registro (0 es el bloque génesis).
    timestamp    Fecha y hora en UTC, formato fijo AAAA-MM-DDTHH:MM:SSZ.
    datos        Texto JSON con el código, por ejemplo {"codigo":"219123456"}.
    prev_hash    Hash del registro anterior (64 caracteres hexadecimales).
    hash_actual  Hash de este registro (64 caracteres hexadecimales).

5.2 Cálculo del hash

    hash_actual = SHA-256( id | timestamp | datos | prev_hash )

Los cuatro campos se unen en un solo texto separados por "|", se codifican en
UTF-8 y se calcula SHA-256. El resultado se guarda en hexadecimal. Una sola
función (calcular_hash en services/hash_service.py) construye ese texto, para
que el formato sea siempre el mismo.

5.3 Bloque génesis

El registro 0 es el primer eslabón. Como no tiene registro anterior, su
prev_hash es un valor fijo: 64 ceros. Se crea una sola vez, cuando la base
está vacía, con un código de prueba (000000000). No corresponde a ninguna
visita real y debe excluirse de reportes y estadísticas.

5.4 Agregar un registro

  1. Se valida el código (9 o 7 dígitos, sin espacios al inicio o al final).
  2. Se abre una transacción exclusiva (BEGIN IMMEDIATE) para que dos
     capturas simultáneas no generen el mismo id.
  3. Se lee el último registro de la cadena.
  4. Se calcula el nuevo id (último + 1), el timestamp actual en UTC, y el
     hash usando como prev_hash el hash_actual del último registro.
  5. Se inserta el registro y se confirma la transacción.

La tabla es de solo anexado: los registros nunca se actualizan desde la
aplicación.

5.5 Verificación de la cadena

La verificación recorre los registros en orden y, para cada uno, comprueba:

  1. Que su id sea el esperado (consecutivo desde 0). Detecta registros
     borrados.
  2. Que su prev_hash coincida con el hash_actual del registro anterior (o
     con los 64 ceros en el génesis).
  3. Que el hash recalculado con sus cuatro campos coincida con el
     hash_actual guardado.

Se detiene en el primer problema y reporta el id del registro y el motivo.

5.6 Persistencia

Los registros se guardan en un archivo SQLite (biblioteca.db). Al cerrar y
volver a abrir la aplicación, los registros siguen ahí y la cadena puede
verificarse.


------------------------------------------------------------------------------
 6. PRUEBA DE ALTERACIÓN (SIMULACIÓN DE ATAQUE)
------------------------------------------------------------------------------

Esta prueba demuestra que la verificación detecta modificaciones hechas
directamente en la base de datos.

Preparación:

  1. Registrar varias entradas y verificar: debe decir "Cadena VÁLIDA".
  2. Cerrar la aplicación (para que la base no quede bloqueada).
  3. Hacer un respaldo:   cp biblioteca.db biblioteca_respaldo.db
     (en el cmd de Windows: copy biblioteca.db biblioteca_respaldo.db)

Modificar la base con la herramienta de SQLite, desde la carpeta del
proyecto:

    sqlite3 biblioteca.db

Casos y resultado esperado al verificar de nuevo:

  CASO 1. Cambiar el contenido de un registro.
      UPDATE registros SET datos = '{"codigo":"999999999"}' WHERE id = 2;
      -> Cadena alterada en el registro 2 (el hash recalculado no coincide).

  CASO 2. Cambiar la fecha de un registro.
      UPDATE registros SET timestamp = '2026-01-01T00:00:00Z' WHERE id = 1;
      -> Cadena alterada en el registro 1.

  CASO 3. Cambiar un registro y recalcular su propio hash_actual.
      -> Cadena alterada en el registro 3: su prev_hash ya no coincide con el
         nuevo hash del registro 2.

  CASO 4. Borrar un registro del medio.
      DELETE FROM registros WHERE id = 2;
      -> Cadena alterada en el registro 3 (falta un registro anterior).

  CASO 5. Cambiar un registro y recalcular los hashes de TODOS los siguientes.
      -> La cadena sigue siendo válida: el ataque NO se detecta. Es la
         limitación principal del diseño (ver sección 7).

Entre un caso y otro, restaurar la base sana:

    cp biblioteca_respaldo.db biblioteca.db

La verificación puede ejecutarse desde la opción 3 del menú de consola o con
el botón "Verificar integridad" de la página /cadena, que además resalta la
fila del registro alterado.


------------------------------------------------------------------------------
 7. SUPUESTOS, LIMITACIONES Y POSIBLES MEJORAS
------------------------------------------------------------------------------

7.1 Supuestos

  - El código capturado se asume válido. No existe un catálogo de estudiantes
    en el sistema, porque la universidad ya cuenta con esa información; solo
    se valida el formato (9 dígitos para alumnos, 7 para maestros).
  - Se registran únicamente entradas a la biblioteca, no salidas.
  - El separador "|" es seguro para el cálculo del hash porque "datos" solo
    contiene un JSON con un código numérico validado, que nunca incluye ese
    carácter.
  - El timestamp se guarda como texto en formato fijo y se hashea tal cual
    está guardado. La conversión a hora local (Guadalajara, UTC-6) solo se
    hace al mostrarlo.
  - Se asume un uso local, con un número reducido de capturas simultáneas.
  - El bloque génesis usa un código de prueba que no corresponde a una visita
    real.

7.2 Limitaciones

  - Reescritura completa de la cadena: SHA-256 es público y no usa ningún
    secreto. Quien tenga acceso de escritura a la base puede modificar un
    registro y recalcular todos los hashes siguientes; la verificación no lo
    detectaría (Caso 5).
  - Borrado de los últimos registros: si se eliminan los registros finales,
    no hay ningún registro posterior que delate la falta.
  - Borrado de toda la base: la aplicación recrea la base y un nuevo génesis
    de forma automática, y no hay nada contra qué comparar.
  - Reloj del equipo: el timestamp lo da la computadora donde corre la
    aplicación. Si se altera la hora del equipo, se registraría una hora falsa
    y la cadena seguiría siendo válida.
  - No hay autenticación ni roles: cualquiera con acceso a la aplicación puede
    registrar entradas y verificar la cadena.
  - No es una red distribuida: un solo equipo guarda toda la información, sin
    consenso ni réplicas.
  - El modo debug de Flask (debug=True en app.py) es solo para desarrollo y no
    debe usarse en un entorno real.

7.3 Posibles mejoras

  - Anclaje externo: guardar periódicamente el hash del último registro fuera
    de la base (un archivo firmado, otro equipo, un correo). Permite detectar
    la reescritura completa, el borrado de registros finales y el reinicio de
    la base.
  - HMAC con clave secreta en lugar de SHA-256 simple, para que un atacante
    sin la clave no pueda recalcular hashes válidos.
  - Firmas digitales (por ejemplo, Ed25519) en cada registro o en puntos de
    control.
  - Árbol de Merkle por lotes (por ejemplo, uno por día) para verificar un
    registro individual sin recorrer toda la cadena.
  - Sellado de tiempo de un servicio externo, para no depender del reloj del
    equipo.
  - Autenticación y roles (quién registra y quién audita).
  - Triggers en la base que bloqueen UPDATE y DELETE sobre la tabla de
    registros, como una barrera adicional.
  - Registrar también las salidas de la biblioteca.
  - Cruzar los códigos con el dataset de la universidad para validar que
    existan.
  - Paginación en el servidor si la cadena crece a miles de registros.


------------------------------------------------------------------------------
 8. NOTAS
------------------------------------------------------------------------------

  - Si se trabaja con Git, agregar al archivo .gitignore: biblioteca.db,
    biblioteca_respaldo.db y __pycache__/.
  - Todos los comandos deben ejecutarse desde la carpeta principal, para que
    los imports entre carpetas funcionen.
  - Para empezar de cero, cerrar la aplicación y borrar biblioteca.db; se
    recreará con un nuevo génesis al iniciar.

==============================================================================
