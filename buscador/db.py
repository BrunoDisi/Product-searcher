"""Base de datos SQLite local (un solo archivo en datos/).

Tablas:
- productos:  cada idea de producto, con su estado de seguimiento y favorito.
- evidencias: cada dato del producto (valor + fuente + fecha + estado). Nunca se
              pisa: si un dato cambia, se agrega una fila nueva y se usa la última.
- puntajes:   cada cálculo de puntaje, con la versión de las reglas usadas.
"""

import json
import sqlite3
from datetime import date, datetime
from pathlib import Path

from buscador.dato import ESTADOS, Dato

RUTA_POR_DEFECTO = Path(__file__).resolve().parent.parent / "datos" / "buscador.sqlite"

ESTADOS_SEGUIMIENTO = ("nuevo", "investigar", "testear", "descartado")

_ESQUEMA = f"""
CREATE TABLE IF NOT EXISTS productos (
    id INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL,
    categoria TEXT,
    descripcion TEXT,
    estado_seguimiento TEXT NOT NULL DEFAULT 'nuevo'
        CHECK (estado_seguimiento IN {ESTADOS_SEGUIMIENTO}),
    favorito INTEGER NOT NULL DEFAULT 0,
    creado TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS evidencias (
    id INTEGER PRIMARY KEY,
    producto_id INTEGER NOT NULL REFERENCES productos(id),
    campo TEXT NOT NULL,
    valor TEXT,
    estado TEXT NOT NULL CHECK (estado IN {ESTADOS}),
    fuente TEXT,
    fecha TEXT,
    nota TEXT,
    registrado TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS puntajes (
    id INTEGER PRIMARY KEY,
    producto_id INTEGER NOT NULL REFERENCES productos(id),
    version_reglas TEXT NOT NULL,
    total REAL NOT NULL,
    confianza TEXT NOT NULL,
    detalle TEXT NOT NULL,
    calculado TEXT NOT NULL
);
"""


def _ahora() -> str:
    return datetime.now().isoformat(timespec="seconds")


def conectar(ruta: Path | str = RUTA_POR_DEFECTO) -> sqlite3.Connection:
    """Abre (o crea) la base y se asegura de que existan las tablas."""
    if str(ruta) != ":memory:":
        Path(ruta).parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(ruta)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    con.executescript(_ESQUEMA)
    return con


def agregar_producto(con, nombre: str, categoria: str = "", descripcion: str = "") -> int:
    cursor = con.execute(
        "INSERT INTO productos (nombre, categoria, descripcion, creado) VALUES (?, ?, ?, ?)",
        (nombre, categoria, descripcion, _ahora()),
    )
    con.commit()
    return cursor.lastrowid


def guardar_dato(con, producto_id: int, campo: str, dato: Dato) -> None:
    con.execute(
        "INSERT INTO evidencias (producto_id, campo, valor, estado, fuente, fecha, nota, registrado)"
        " VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (
            producto_id,
            campo,
            json.dumps(dato.valor, ensure_ascii=False),
            dato.estado,
            dato.fuente,
            dato.fecha.isoformat() if dato.fecha else None,
            dato.nota,
            _ahora(),
        ),
    )
    con.commit()


def datos_del_producto(con, producto_id: int) -> dict[str, Dato]:
    """El dato más reciente de cada campo de un producto."""
    filas = con.execute(
        "SELECT * FROM evidencias WHERE producto_id = ? ORDER BY id", (producto_id,)
    ).fetchall()
    datos = {}
    for fila in filas:  # en orden: el último registrado pisa a los anteriores
        datos[fila["campo"]] = Dato(
            valor=json.loads(fila["valor"]),
            estado=fila["estado"],
            fuente=fila["fuente"] or "",
            fecha=date.fromisoformat(fila["fecha"]) if fila["fecha"] else None,
            nota=fila["nota"] or "",
        )
    return datos


def guardar_puntaje(con, producto_id: int, version_reglas: str, total: float,
                    confianza: str, detalle: dict) -> None:
    con.execute(
        "INSERT INTO puntajes (producto_id, version_reglas, total, confianza, detalle, calculado)"
        " VALUES (?, ?, ?, ?, ?, ?)",
        (producto_id, version_reglas, total, confianza,
         json.dumps(detalle, ensure_ascii=False), _ahora()),
    )
    con.commit()


def marcar_seguimiento(con, producto_id: int, estado: str | None = None,
                       favorito: bool | None = None) -> None:
    """Cambia el estado (nuevo / investigar / testear / descartado) o el favorito."""
    if estado is not None:
        if estado not in ESTADOS_SEGUIMIENTO:
            raise ValueError(f"Estado inválido: {estado!r}. Usá uno de {ESTADOS_SEGUIMIENTO}.")
        con.execute("UPDATE productos SET estado_seguimiento = ? WHERE id = ?", (estado, producto_id))
    if favorito is not None:
        con.execute("UPDATE productos SET favorito = ? WHERE id = ?", (int(favorito), producto_id))
    con.commit()
