"""Lee los archivos de configuración de la carpeta config/."""

import tomllib
from pathlib import Path

from buscador.dato import Dato

CARPETA_CONFIG = Path(__file__).resolve().parent.parent / "config"


def leer_toml(nombre: str, carpeta: Path = CARPETA_CONFIG) -> dict:
    with open(carpeta / nombre, "rb") as archivo:
        return tomllib.load(archivo)


def a_dato(bloque: dict) -> Dato:
    """Convierte un bloque del .toml (valor, estado, fuente, fecha, nota) en un Dato."""
    return Dato(
        valor=bloque.get("valor"),
        estado=bloque.get("estado", "desconocido"),
        fuente=bloque.get("fuente", ""),
        fecha=bloque.get("fecha"),
        nota=bloque.get("nota", ""),
    )


def cargar_categorias(carpeta: Path = CARPETA_CONFIG) -> list[dict]:
    """Lista de categorías: [{'id': 'mascotas', 'nombre': 'Mascotas'}, ...]."""
    categorias = leer_toml("categorias.toml", carpeta).get("categoria", [])
    ids = [c["id"] for c in categorias]
    repetidos = {i for i in ids if ids.count(i) > 1}
    if repetidos:
        raise ValueError(f"Categorías repetidas en categorias.toml: {sorted(repetidos)}")
    return categorias


def cargar_importacion(carpeta: Path = CARPETA_CONFIG) -> dict:
    """Alícuotas de importación (como Datos) y tratamiento fiscal."""
    crudo = leer_toml("importacion.toml", carpeta)
    nombres = ["tasa_estadistica", "iva", "iva_adicional", "percepcion_ganancias",
               "percepcion_iibb", "derecho_supuesto_sin_ncm"]
    config = {nombre: a_dato(crudo[nombre]) for nombre in nombres}
    config["tratamiento"] = crudo["tratamiento"]
    config["fecha_ultima_verificacion"] = crudo["fecha_ultima_verificacion"]
    return config


def cargar_venta(carpeta: Path = CARPETA_CONFIG) -> dict:
    """Supuestos de venta (como Datos), situación fiscal y canal."""
    crudo = leer_toml("venta.toml", carpeta)
    nombres = ["tipo_cambio_ars_por_usd", "comision_ml", "iva_sobre_comision",
               "costo_fijo_ml_ars", "envio_ars", "publicidad", "iibb_venta"]
    config = {nombre: a_dato(crudo[nombre]) for nombre in nombres}
    config["situacion_fiscal"] = crudo["situacion_fiscal"]
    config["canal"] = crudo["canal"]
    return config
