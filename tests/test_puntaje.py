from dataclasses import replace
from datetime import date

from buscador.dato import Dato, desconocido
from buscador.puntaje import (Evaluacion, SenalCompra, SerieTendencia, calcular_puntaje,
                              clasificar_mercado, clave_ranking)

HOY = date(2026, 11, 20)


def v(valor):
    """Dato verificado (para pruebas)."""
    return Dato(valor, "verificado", "fuente de prueba", HOY)


def e(valor):
    """Dato estimado (para pruebas)."""
    return Dato(valor, "estimado", "fuente de prueba")


def producto_ideal() -> Evaluacion:
    """Un producto inventado con todo verificado y lo mejor en cada criterio."""
    return Evaluacion(
        senales_compra=[SenalCompra("pedidos", "AliExpress", "China", v(20_000)),
                        SenalCompra("ranking", "Amazon", "EE.UU.", v(50))],
        ml_buscado=v(True), vendedores_ml=v(10), ventas_visibles_ml=v(300),
        quejas_calidad_ml=v(True), busquedas_locales=v(True),
        barreras_revisadas=v(True), barrera_ausencia=v("ninguna"),
        margen=v(0.45), ncm=v("3924.90.00"), fob_usd=v(4.0), precio_ml_ars=v(25000),
        problema_concreto=v(True), sustitutos_analizados=v(True), ventaja=v("clara"), resuelve_quejas=v(True),
        peso_kg=v(0.5), fragil=v(False), certificacion=v("no_requiere"), marca_protegida=v(False),
        series_tendencia=[SerieTendencia("EE.UU.", v(0.6)), SerieTendencia("México", v(0.8))],
        en_ml_region=v(True),
    )


def puntos(resultado, nombre):
    return next(c.puntos for c in resultado.criterios if c.nombre.startswith(nombre))


def test_producto_ideal_da_100_y_confianza_alta():
    r = calcular_puntaje(producto_ideal(), HOY)
    assert r.total == 100
    assert r.confianza == "alta"
    assert r.clasificacion_mercado == "oferta deficiente"


def test_producto_sin_datos_da_0_y_confianza_baja():
    r = calcular_puntaje(Evaluacion(), HOY)
    assert r.total == 0 and r.confianza == "baja"


def test_mismo_producto_mismo_puntaje():
    assert calcular_puntaje(producto_ideal(), HOY) == calcular_puntaje(producto_ideal(), HOY)


# --- Demanda: la viralidad no es demanda
def test_solo_redes_no_suma_demanda():
    ev = replace(producto_ideal(), senales_compra=[], senales_redes=[v(5_000_000)])
    r = calcular_puntaje(ev, HOY)
    assert puntos(r, "Demanda") == 0
    assert r.confianza != "alta"


def test_una_sola_senal_de_compra():
    ev = replace(producto_ideal(), senales_compra=[SenalCompra("vendidos", "eBay", "EE.UU.", v(1_500))])
    assert puntos(calcular_puntaje(ev, HOY), "Demanda") == 9


# --- Oportunidad en Argentina
def test_sin_busqueda_en_ml_tope_8_y_confianza_baja():
    ev = replace(producto_ideal(), ml_buscado=desconocido("Buscar en ML Argentina"))
    r = calcular_puntaje(ev, HOY)
    assert puntos(r, "Oportunidad") <= 8
    assert r.confianza == "baja"


def test_ausente_en_ml_sin_revisar_barreras_tope_8():
    ev = replace(producto_ideal(), vendedores_ml=v(0), quejas_calidad_ml=v(False),
                 ventas_visibles_ml=v(0), barreras_revisadas=desconocido("Revisar barreras"))
    r = calcular_puntaje(ev, HOY)
    assert r.clasificacion_mercado == "poco explotado"
    assert puntos(r, "Oportunidad") == 8


def test_ausente_en_ml_con_barreras_revisadas_suma():
    ev = replace(producto_ideal(), vendedores_ml=v(0), quejas_calidad_ml=v(False), ventas_visibles_ml=v(0))
    assert puntos(calcular_puntaje(ev, HOY), "Oportunidad") == 16 + 3


def test_ausencia_explicada_por_barrera_tope_8():
    ev = replace(producto_ideal(), vendedores_ml=v(0), quejas_calidad_ml=v(False),
                 barrera_ausencia=v("certificacion"))
    assert puntos(calcular_puntaje(ev, HOY), "Oportunidad") <= 8


def test_ausencia_por_falta_de_demanda_da_0():
    ev = replace(producto_ideal(), vendedores_ml=v(0), quejas_calidad_ml=v(False),
                 barrera_ausencia=v("falta_demanda"))
    assert puntos(calcular_puntaje(ev, HOY), "Oportunidad") == 0


def test_clasificacion_de_mercado():
    base = replace(producto_ideal(), quejas_calidad_ml=v(False))
    assert clasificar_mercado(replace(base, vendedores_ml=v(3))) == "poco explotado"
    assert clasificar_mercado(replace(base, vendedores_ml=v(15))) == "emergente"
    assert clasificar_mercado(replace(base, vendedores_ml=v(80))) == "saturado"
    assert clasificar_mercado(replace(base, vendedores_ml=v(80), quejas_calidad_ml=v(True))) == "oferta deficiente"
    assert clasificar_mercado(replace(base, ml_buscado=desconocido())) == "sin clasificar"


# --- Rentabilidad
def test_sin_ncm_rentabilidad_tope_5():
    ev = replace(producto_ideal(), ncm=desconocido("Consultar despachante"), margen=e(0.45))
    assert puntos(calcular_puntaje(ev, HOY), "Rentabilidad") == 5


def test_margen_desconocido_rentabilidad_0():
    ev = replace(producto_ideal(), margen=desconocido("Falta precio local"))
    assert puntos(calcular_puntaje(ev, HOY), "Rentabilidad") == 0


def test_margen_estimado_baja_la_confianza_a_media():
    r = calcular_puntaje(replace(producto_ideal(), margen=e(0.45)), HOY)
    assert r.confianza == "media"


# --- Diferenciación
def test_sin_sustitutos_analizados_tope_7():
    ev = replace(producto_ideal(), sustitutos_analizados=desconocido())
    assert puntos(calcular_puntaje(ev, HOY), "Diferenciación") == 7


# --- Logística
def test_certificacion_sin_evaluar_da_0():
    ev = replace(producto_ideal(), certificacion=desconocido("Consultar si requiere certificación"))
    assert puntos(calcular_puntaje(ev, HOY), "Logística") == 0


def test_marca_protegida_da_0():
    ev = replace(producto_ideal(), marca_protegida=v(True))
    assert puntos(calcular_puntaje(ev, HOY), "Logística") == 0


def test_pesado_y_fragil_resta():
    ev = replace(producto_ideal(), peso_kg=v(4.0), fragil=v(True))
    assert puntos(calcular_puntaje(ev, HOY), "Logística") == 4 + 1 + 2 - 2


# --- Tendencia
def test_una_sola_serie_tope_3():
    ev = replace(producto_ideal(), series_tendencia=[SerieTendencia("EE.UU.", v(0.9))])
    assert puntos(calcular_puntaje(ev, HOY), "Tendencia") == 3


# --- Confianza y ranking
def test_un_criterio_sin_dato_da_confianza_media():
    r = calcular_puntaje(replace(producto_ideal(), certificacion=desconocido()), HOY)
    assert r.confianza == "media"


def test_dos_criterios_sin_dato_dan_confianza_baja():
    ev = replace(producto_ideal(), certificacion=desconocido(), series_tendencia=[])
    assert calcular_puntaje(ev, HOY).confianza == "baja"


def test_precios_viejos_no_dan_confianza_alta():
    viejo = Dato(25000, "verificado", "ML", date(2026, 9, 1))
    r = calcular_puntaje(replace(producto_ideal(), precio_ml_ars=viejo), HOY)
    assert r.confianza == "media"


def test_confianza_baja_nunca_arriba_de_media():
    # Confianza media pero pocos puntos (le falta solo la certificación, margen flojo)
    media_flojo = calcular_puntaje(replace(producto_ideal(), certificacion=desconocido(), margen=e(0.12),
                                           series_tendencia=[SerieTendencia("EE.UU.", v(-0.1)),
                                                             SerieTendencia("México", v(-0.1))]), HOY)
    # Confianza baja pero muchos puntos (no se buscó en ML)
    baja_alto = calcular_puntaje(replace(producto_ideal(), ml_buscado=desconocido()), HOY)
    assert media_flojo.confianza == "media" and baja_alto.confianza == "baja"
    assert baja_alto.total > media_flojo.total
    ranking = sorted([baja_alto, media_flojo], key=clave_ranking)
    assert ranking[0] is media_flojo
