from datetime import date

import pytest

from buscador.config import cargar_categorias, cargar_importacion, cargar_venta
from buscador.dato import Dato, desconocido, peor_estado


def test_dato_desconocido_no_puede_tener_valor():
    with pytest.raises(ValueError):
        Dato(valor=10, estado="desconocido")


def test_dato_estimado_necesita_valor():
    with pytest.raises(ValueError):
        Dato(estado="estimado")


def test_dato_verificado_necesita_fuente_y_fecha():
    with pytest.raises(ValueError):
        Dato(valor=10, estado="verificado")
    Dato(valor=10, estado="verificado", fuente="ML", fecha=date(2026, 11, 20))


def test_estado_invalido():
    with pytest.raises(ValueError):
        Dato(valor=1, estado="seguro")


def test_desconocido_guarda_como_conseguirlo():
    d = desconocido("Pedir cotización al proveedor")
    assert not d.conocido and d.nota == "Pedir cotización al proveedor"


def test_peor_estado():
    assert peor_estado("verificado", "estimado") == "estimado"
    assert peor_estado("verificado", "desconocido", "estimado") == "desconocido"
    assert peor_estado("verificado") == "verificado"


def test_categorias_se_leen_del_archivo():
    categorias = cargar_categorias()
    ids = [c["id"] for c in categorias]
    assert len(categorias) == 13
    assert "mascotas" in ids and "innovadores" in ids


def test_categorias_repetidas_dan_error(tmp_path):
    (tmp_path / "categorias.toml").write_text(
        '[[categoria]]\nid = "a"\nnombre = "A"\n[[categoria]]\nid = "a"\nnombre = "B"\n',
        encoding="utf-8")
    with pytest.raises(ValueError):
        cargar_categorias(tmp_path)


def test_alicuotas_tienen_fuente_y_fecha_o_son_desconocidas():
    config = cargar_importacion()
    for nombre in ["tasa_estadistica", "iva", "iva_adicional", "percepcion_ganancias",
                   "percepcion_iibb", "derecho_supuesto_sin_ncm"]:
        dato = config[nombre]
        assert dato.estado == "desconocido" or (dato.fuente and dato.fecha), nombre


def test_config_venta_tiene_situacion_valida():
    venta = cargar_venta()
    assert venta["situacion_fiscal"] in cargar_importacion()["tratamiento"]
