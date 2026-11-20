from datetime import date

import pytest

from buscador.config import cargar_importacion, cargar_venta
from buscador.costos import calcular_importacion, calcular_margen
from buscador.dato import Dato, desconocido

HOY = date(2026, 11, 20)


@pytest.fixture
def config():
    return cargar_importacion()


def ejemplo_diseno(config, situacion="responsable_inscripto", gastos=None):
    """El ejemplo hipotético de DISENO.md, sección 8."""
    return calcular_importacion(
        fob_usd=Dato(4.0, "estimado", "Ejemplo DISENO.md"),
        flete_seguro_usd=Dato(1.0, "estimado", "Ejemplo DISENO.md"),
        derecho=Dato(0.20, "estimado", "Supuesto del ejemplo"),
        config=config,
        situacion_fiscal=situacion,
        gastos_locales_usd=gastos,
    )


def monto(resultado, inicio):
    return next(l.valor for l in resultado.lineas if l.concepto.startswith(inicio))


def test_reproduce_el_ejemplo_de_diseno(config):
    r = ejemplo_diseno(config)
    assert monto(r, "CIF") == pytest.approx(5.00)
    assert monto(r, "Derecho") == pytest.approx(1.00)
    assert monto(r, "Tasa de estadística") == pytest.approx(0.15)
    assert monto(r, "Base imponible") == pytest.approx(6.15)
    iva_total = monto(r, "IVA (") + monto(r, "IVA adicional")
    assert round(iva_total, 2) == 2.52
    assert round(monto(r, "Percepción de Ganancias"), 2) == 0.37
    # Responsable inscripto: IVA y percepciones son crédito, el costo es 6,15
    assert r.costo_unitario.valor == pytest.approx(6.15)
    assert r.costo_unitario.estado == "estimado"


def test_faltan_gastos_locales_e_iibb_y_se_avisa(config):
    r = ejemplo_diseno(config)
    textos = " ".join(r.faltantes)
    assert "Despachante" in textos and "IIBB" in textos


def test_pago_en_aduana_incluye_creditos(config):
    r = ejemplo_diseno(config)
    assert r.pago_en_aduana.valor == pytest.approx(6.15 + 6.15 * (0.21 + 0.20 + 0.06))


def test_gastos_locales_suman_al_costo(config):
    r = ejemplo_diseno(config, gastos=Dato(0.50, "estimado", "Presupuesto despachante"))
    assert r.costo_unitario.valor == pytest.approx(6.65)


def test_monotributista_el_iva_es_costo(config):
    r = ejemplo_diseno(config, situacion="monotributista")
    # 6,15 + IVA 21% + Ganancias 6% (IVA adicional no aplica, IIBB desconocido)
    assert r.costo_unitario.valor == pytest.approx(6.15 * (1 + 0.21 + 0.06))


def test_sin_precio_de_proveedor_el_costo_es_desconocido(config):
    r = calcular_importacion(desconocido("Pedir cotización en Alibaba"), Dato(1.0, "estimado", "x"),
                             Dato(0.2, "estimado", "x"), config, "responsable_inscripto")
    assert r.costo_unitario.estado == "desconocido"
    assert r.costo_unitario.valor is None
    assert any("Alibaba" in f for f in r.faltantes)


def test_sin_ncm_usa_el_supuesto_conservador(config):
    r = calcular_importacion(Dato(4.0, "verificado", "Cotización", HOY), Dato(1.0, "verificado", "Forwarder", HOY),
                             desconocido("Consultar NCM"), config, "responsable_inscripto")
    assert monto(r, "Derecho") == pytest.approx(5.0 * 0.35)
    assert r.costo_unitario.estado == "estimado"


# ---------- Margen ----------

def venta_con(**cambios):
    venta = cargar_venta()
    venta["tipo_cambio_ars_por_usd"] = Dato(1000.0, "estimado", "Tipo de cambio de prueba")
    venta.update(cambios)
    return venta


def test_margen_responsable_inscripto(config):
    venta = venta_con(
        costo_fijo_ml_ars=Dato(0.0, "estimado", "prueba"),
        envio_ars=Dato(0.0, "estimado", "prueba"),
        publicidad=Dato(0.0, "estimado", "prueba"),
        iibb_venta=Dato(0.0, "estimado", "prueba"),
    )
    r = calcular_margen(Dato(6.15, "estimado", "x"), Dato(24200.0, "estimado", "ML"), venta, config["iva"])
    # ingreso 24200/1,21 = 20000; comisión 15% de 24200 = 3630; producto 6150
    assert r.ganancia_ars.valor == pytest.approx(20000 - 3630 - 6150)
    assert r.margen.valor == pytest.approx((20000 - 3630 - 6150) / 20000)
    assert r.faltantes == []


def test_margen_lista_lo_que_falta(config):
    r = calcular_margen(Dato(6.15, "estimado", "x"), Dato(24200.0, "estimado", "ML"), venta_con(), config["iva"])
    assert r.margen.estado == "estimado"
    assert len(r.faltantes) == 4  # costo fijo, envío, publicidad, IIBB


def test_sin_precio_local_el_margen_es_desconocido(config):
    r = calcular_margen(Dato(6.15, "estimado", "x"), desconocido("Buscar en ML"), venta_con(), config["iva"])
    assert r.margen.estado == "desconocido" and r.margen.valor is None


def test_sin_tipo_de_cambio_el_margen_es_desconocido(config):
    venta = cargar_venta()  # el archivo trae el tipo de cambio sin completar
    r = calcular_margen(Dato(6.15, "estimado", "x"), Dato(24200.0, "estimado", "ML"), venta, config["iva"])
    assert r.margen.estado == "desconocido"
    assert any("Tipo de cambio" in f for f in r.faltantes)
