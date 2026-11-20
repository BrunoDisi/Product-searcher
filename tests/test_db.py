from datetime import date

import pytest

from buscador import db
from buscador.dato import Dato, desconocido


@pytest.fixture
def con():
    conexion = db.conectar(":memory:")  # base temporal, solo para la prueba
    yield conexion
    conexion.close()


def test_guardar_y_leer_datos_con_fuente_fecha_y_estado(con):
    pid = db.agregar_producto(con, "Organizador de prueba", categoria="organizacion")
    db.guardar_dato(con, pid, "fob_usd",
                    Dato(4.0, "verificado", "Cotización proveedor X", date(2026, 11, 20)))
    db.guardar_dato(con, pid, "ncm", desconocido("Consultar despachante"))

    datos = db.datos_del_producto(con, pid)
    assert datos["fob_usd"] == Dato(4.0, "verificado", "Cotización proveedor X", date(2026, 11, 20))
    assert datos["ncm"].estado == "desconocido"
    assert datos["ncm"].nota == "Consultar despachante"


def test_un_dato_nuevo_no_borra_el_historial(con):
    pid = db.agregar_producto(con, "Producto")
    db.guardar_dato(con, pid, "precio_ml_ars", Dato(10000, "estimado", "a ojo"))
    db.guardar_dato(con, pid, "precio_ml_ars", Dato(12000, "verificado", "ML", date(2026, 11, 20)))

    assert db.datos_del_producto(con, pid)["precio_ml_ars"].valor == 12000
    filas = con.execute("SELECT COUNT(*) FROM evidencias WHERE campo = 'precio_ml_ars'").fetchone()[0]
    assert filas == 2


def test_seguimiento_y_favorito(con):
    pid = db.agregar_producto(con, "Producto")
    db.marcar_seguimiento(con, pid, estado="testear", favorito=True)
    fila = con.execute("SELECT * FROM productos WHERE id = ?", (pid,)).fetchone()
    assert fila["estado_seguimiento"] == "testear" and fila["favorito"] == 1
    with pytest.raises(ValueError):
        db.marcar_seguimiento(con, pid, estado="comprar ya")


def test_guardar_puntaje(con):
    pid = db.agregar_producto(con, "Producto")
    db.guardar_puntaje(con, pid, "v1", 55.0, "medio", {"demanda": 10})
    fila = con.execute("SELECT * FROM puntajes").fetchone()
    assert fila["total"] == 55.0 and fila["version_reglas"] == "v1"
