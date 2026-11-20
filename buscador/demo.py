"""Ejemplo para revisar a ojo los módulos de costos y puntaje.

Uso:  python -m buscador.demo

TODO lo que muestra es HIPOTÉTICO (datos de ejemplo, no de un producto real).
"""

from dataclasses import replace
from datetime import date

from buscador.config import cargar_importacion, cargar_venta
from buscador.costos import calcular_importacion, calcular_margen
from buscador.dato import Dato, desconocido
from buscador.puntaje import Evaluacion, SenalCompra, SerieTendencia, calcular_puntaje

HOY = date.today()


def num(valor, decimales=2):
    """Formato argentino: 24.200,00"""
    texto = f"{valor:,.{decimales}f}"
    return texto.replace(",", "_").replace(".", ",").replace("_", ".")


def mostrar_lineas(lineas, moneda):
    for l in lineas:
        valor = f"{num(l.valor):>12}" if l.valor is not None else f"{'?':>12}"
        print(f"  {l.concepto:<42} {moneda} {valor}  [{l.estado}, {l.tratamiento}]")


def mostrar_faltantes(faltantes):
    if faltantes:
        print("  Falta (no se inventa):")
        for f in faltantes:
            print(f"   - {f}")


def mostrar_puntaje(titulo, r):
    print(f"\n{titulo}")
    print(f"  PUNTAJE: {r.total:.0f}/100 · CONFIANZA: {r.confianza} · MERCADO: {r.clasificacion_mercado}")
    for c in r.criterios:
        print(f"  {c.nombre:<26} {c.puntos:>4.0f}/{c.maximo:<3}  " + " ".join(c.motivos))
    for m in r.motivos_confianza:
        print(f"  · Confianza: {m}")


def main():
    importacion = cargar_importacion()
    venta = cargar_venta()
    print("=" * 78)
    print("EJEMPLO HIPOTÉTICO — no son datos de un producto real")
    print("=" * 78)

    # 1) Costos: el ejemplo de DISENO.md, sección 8
    print("\n1) COSTO PUESTO EN ARGENTINA (ejemplo de DISENO.md, responsable inscripto)")
    print("   FOB USD 4,00 · flete+seguro USD 1,00 · derecho supuesto 20%\n")
    costo = calcular_importacion(
        fob_usd=Dato(4.0, "estimado", "Ejemplo DISENO.md"),
        flete_seguro_usd=Dato(1.0, "estimado", "Ejemplo DISENO.md"),
        derecho=Dato(0.20, "estimado", "Supuesto del ejemplo"),
        config=importacion, situacion_fiscal=venta["situacion_fiscal"],
    )
    mostrar_lineas(costo.lineas, "USD")
    print(f"\n  COSTO UNITARIO (lo que se pierde):      USD {num(costo.costo_unitario.valor)}"
          f"  [{costo.costo_unitario.estado}]")
    print(f"  PLATA A PAGAR EN ADUANA (con créditos): USD {num(costo.pago_en_aduana.valor)}"
          f"  [{costo.pago_en_aduana.estado}]")
    mostrar_faltantes(costo.faltantes)

    # 2) Margen con supuestos hipotéticos
    print("\n2) MARGEN EN MERCADO LIBRE (tipo de cambio y precio HIPOTÉTICOS)\n")
    venta_demo = dict(venta, tipo_cambio_ars_por_usd=Dato(1000.0, "estimado", "HIPOTÉTICO para el ejemplo"))
    margen = calcular_margen(costo.costo_unitario, Dato(24200.0, "estimado", "HIPOTÉTICO"),
                             venta_demo, importacion["iva"])
    mostrar_lineas(margen.lineas, "ARS")
    print(f"\n  GANANCIA POR UNIDAD: ARS {num(margen.ganancia_ars.valor, 0)} · MARGEN: {margen.margen.valor:.0%}"
          f"  [{margen.margen.estado}]")
    mostrar_faltantes(margen.faltantes)

    # 3) Puntaje: el mismo producto inventado, con datos completos y con datos faltantes
    def v(valor):
        return Dato(valor, "verificado", "HIPOTÉTICO", HOY)

    completo = Evaluacion(
        senales_compra=[SenalCompra("pedidos", "AliExpress", "China", v(5_000)),
                        SenalCompra("ranking", "Amazon", "EE.UU.", v(400))],
        senales_redes=[v(2_000_000)],
        ml_buscado=v(True), vendedores_ml=v(4), ventas_visibles_ml=v(120), quejas_calidad_ml=v(False),
        busquedas_locales=v(False), barreras_revisadas=v(True), barrera_ausencia=v("ninguna"),
        margen=margen.margen, ncm=desconocido("Consultar despachante"), fob_usd=v(4.0), precio_ml_ars=v(24200),
        problema_concreto=v(True), sustitutos_analizados=v(True), ventaja=v("menor"), resuelve_quejas=v(False),
        peso_kg=v(0.8), fragil=v(False), certificacion=v("no_requiere"), marca_protegida=v(False),
        series_tendencia=[SerieTendencia("EE.UU.", v(0.25)), SerieTendencia("México", v(0.35))],
        en_ml_region=v(True),
    )
    incompleto = replace(
        completo,
        senales_compra=[],  # solo queda la viralidad en redes
        ml_buscado=desconocido("Buscar en ML Argentina"),
        certificacion=desconocido("Consultar si requiere certificación"),
        series_tendencia=completo.series_tendencia[:1],
    )
    print("\n3) PUNTAJE (producto inventado)")
    mostrar_puntaje("A) Con datos completos:", calcular_puntaje(completo, HOY))
    mostrar_puntaje("B) El MISMO producto con datos faltantes (solo redes, sin ML, sin certificación, 1 serie):",
                    calcular_puntaje(incompleto, HOY))


if __name__ == "__main__":
    main()
