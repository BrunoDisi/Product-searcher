"""Costo puesto en Argentina (importación FORMAL) y margen de venta.

Reglas:
- Datos clave (precio del proveedor FOB, flete internacional, precio de venta,
  tipo de cambio): si falta alguno, el resultado es DESCONOCIDO. No se inventa.
- Si falta el derecho de importación (sin NCM), se usa el supuesto conservador de
  config/importacion.toml y el resultado queda ESTIMADO.
- Gastos que faltan (despachante, envío, etc.) no se inventan: se calcula con lo
  que hay, el resultado queda ESTIMADO y se listan en "faltantes".
- Según la situación fiscal, cada impuesto es "costo" (se pierde) o "credito"
  (se paga en aduana pero se recupera).
"""

from dataclasses import dataclass, field

from buscador.dato import DESCONOCIDO, ESTIMADO, Dato, peor_estado


@dataclass
class Linea:
    concepto: str
    valor: float | None
    estado: str
    tratamiento: str  # "costo", "credito", "no_aplica" o "calculado"
    nota: str = ""


@dataclass
class ResultadoImportacion:
    """Todo en USD por unidad."""
    lineas: list[Linea] = field(default_factory=list)
    costo_unitario: Dato = field(default_factory=Dato)  # lo que cuesta de verdad
    pago_en_aduana: Dato = field(default_factory=Dato)  # plata a tener (costo + créditos)
    faltantes: list[str] = field(default_factory=list)


@dataclass
class ResultadoMargen:
    """Todo en ARS por unidad."""
    lineas: list[Linea] = field(default_factory=list)
    ganancia_ars: Dato = field(default_factory=Dato)
    margen: Dato = field(default_factory=Dato)  # ganancia / ingreso neto (0.30 = 30%)
    faltantes: list[str] = field(default_factory=list)


def _faltante(nombre: str, dato: Dato) -> str:
    return f"{nombre}: {dato.nota}" if dato.nota else nombre


def calcular_importacion(fob_usd: Dato, flete_seguro_usd: Dato, derecho: Dato,
                         config: dict, situacion_fiscal: str,
                         gastos_locales_usd: Dato | None = None) -> ResultadoImportacion:
    """Costo unitario de un producto importado en forma formal.

    fob_usd: precio del proveedor por unidad. flete_seguro_usd: flete + seguro
    internacional por unidad. derecho: alícuota según NCM (0.20 = 20%).
    gastos_locales_usd: despachante + depósito + flete local por unidad.
    """
    resultado = ResultadoImportacion()
    tratamiento = config["tratamiento"][situacion_fiscal]
    gastos_locales_usd = gastos_locales_usd or Dato(nota="Pedir presupuesto a despachante y transporte")

    # 1) Datos clave
    for nombre, dato in [("Precio del proveedor (FOB)", fob_usd),
                         ("Flete + seguro internacional", flete_seguro_usd)]:
        if not dato.conocido:
            resultado.faltantes.append(_faltante(nombre, dato))
    if resultado.faltantes:
        return resultado  # sin datos clave no hay costo: queda desconocido

    estados_costo = [fob_usd.estado, flete_seguro_usd.estado]
    estados_pago = list(estados_costo)
    lineas = resultado.lineas

    # 2) CIF
    cif = fob_usd.valor + flete_seguro_usd.valor
    lineas.append(Linea("FOB (precio del proveedor)", fob_usd.valor, fob_usd.estado, "costo", fob_usd.fuente))
    lineas.append(Linea("Flete + seguro internacional", flete_seguro_usd.valor, flete_seguro_usd.estado,
                        "costo", flete_seguro_usd.fuente))
    lineas.append(Linea("CIF", cif, peor_estado(*estados_costo), "calculado"))

    # 3) Derecho de importación (si no hay NCM, supuesto conservador)
    if not derecho.conocido:
        supuesto = config["derecho_supuesto_sin_ncm"]
        derecho = Dato(supuesto.valor, ESTIMADO, supuesto.fuente, supuesto.fecha,
                       "Sin NCM: se usa el supuesto conservador. Confirmar NCM.")
    monto_derecho = cif * derecho.valor
    lineas.append(Linea(f"Derecho de importación ({derecho.valor:.0%})", monto_derecho,
                        derecho.estado, "costo", derecho.nota or derecho.fuente))
    estados_costo.append(derecho.estado)

    # 4) Tasa de estadística
    te = config["tasa_estadistica"]
    if not te.conocido:
        resultado.faltantes.append(_faltante("Tasa de estadística", te))
        return resultado
    monto_te = cif * te.valor
    lineas.append(Linea(f"Tasa de estadística ({te.valor:.0%})", monto_te, te.estado, "costo", te.nota))
    estados_costo.append(te.estado)

    base_iva = cif + monto_derecho + monto_te
    lineas.append(Linea("Base imponible IVA", base_iva, peor_estado(*estados_costo), "calculado"))
    estados_pago = list(estados_costo)

    # 5) IVA y percepciones: costo o crédito según situación fiscal
    costo = base_iva
    creditos = 0.0
    nombres = {"iva": "IVA", "iva_adicional": "IVA adicional (percepción)",
               "percepcion_ganancias": "Percepción de Ganancias", "percepcion_iibb": "Percepción de IIBB"}
    for clave, nombre in nombres.items():
        trato = tratamiento[clave]
        alicuota = config[clave]
        if trato == "no_aplica":
            continue
        if not alicuota.conocido:
            resultado.faltantes.append(_faltante(nombre, alicuota))
            estados_pago.append(ESTIMADO)
            if trato == "costo":
                estados_costo.append(ESTIMADO)
            lineas.append(Linea(nombre, None, DESCONOCIDO, trato, alicuota.nota))
            continue
        monto = base_iva * alicuota.valor
        lineas.append(Linea(f"{nombre} ({alicuota.valor:.0%})", monto, alicuota.estado, trato, alicuota.nota))
        estados_pago.append(alicuota.estado)
        if trato == "costo":
            costo += monto
            estados_costo.append(alicuota.estado)
        else:
            creditos += monto

    # 6) Gastos locales
    if gastos_locales_usd.conocido:
        costo += gastos_locales_usd.valor
        estados_costo.append(gastos_locales_usd.estado)
        estados_pago.append(gastos_locales_usd.estado)
        lineas.append(Linea("Despachante, depósito y flete local", gastos_locales_usd.valor,
                            gastos_locales_usd.estado, "costo", gastos_locales_usd.fuente))
    else:
        resultado.faltantes.append(_faltante("Despachante, depósito y flete local", gastos_locales_usd))
        estados_costo.append(ESTIMADO)
        estados_pago.append(ESTIMADO)
        lineas.append(Linea("Despachante, depósito y flete local", None, DESCONOCIDO, "costo",
                            gastos_locales_usd.nota))

    resultado.costo_unitario = Dato(costo, peor_estado(*estados_costo), "Cálculo (buscador/costos.py)")
    resultado.pago_en_aduana = Dato(costo + creditos, peor_estado(*estados_pago), "Cálculo (buscador/costos.py)")
    return resultado


def calcular_margen(costo_unitario_usd: Dato, precio_venta_ars: Dato, config_venta: dict,
                    iva: Dato) -> ResultadoMargen:
    """Ganancia y margen por unidad vendida en Mercado Libre.

    precio_venta_ars: precio final al público (con IVA). iva: alícuota de IVA de
    la venta (se toma de config/importacion.toml).
    El margen es ganancia / ingreso neto (sin IVA si sos responsable inscripto).
    """
    resultado = ResultadoMargen()
    tc = config_venta["tipo_cambio_ars_por_usd"]
    situacion = config_venta["situacion_fiscal"]

    for nombre, dato in [("Costo unitario puesto en Argentina", costo_unitario_usd),
                         ("Precio de venta en Argentina", precio_venta_ars),
                         ("Tipo de cambio (config/venta.toml)", tc)]:
        if not dato.conocido:
            resultado.faltantes.append(_faltante(nombre, dato))
    if situacion == "responsable_inscripto" and not iva.conocido:
        resultado.faltantes.append(_faltante("IVA", iva))
    if resultado.faltantes:
        return resultado  # sin datos clave el margen queda desconocido

    precio = precio_venta_ars.valor
    estados = [costo_unitario_usd.estado, precio_venta_ars.estado, tc.estado]
    lineas = resultado.lineas
    lineas.append(Linea("Precio de venta (con IVA)", precio, precio_venta_ars.estado, "calculado",
                        precio_venta_ars.fuente))

    if situacion == "responsable_inscripto":
        ingreso = precio / (1 + iva.valor)
        estados.append(iva.estado)
        lineas.append(Linea("Ingreso neto (sin IVA)", ingreso, peor_estado(*estados), "calculado"))
    else:
        ingreso = precio  # el monotributista no discrimina IVA

    costos = costo_unitario_usd.valor * tc.valor
    lineas.append(Linea("Costo del producto en pesos", costos, peor_estado(costo_unitario_usd.estado, tc.estado),
                        "costo"))

    def restar(nombre: str, dato: Dato, monto_si_conocido):
        nonlocal costos
        if dato.conocido:
            monto = monto_si_conocido(dato.valor)
            costos += monto
            estados.append(dato.estado)
            lineas.append(Linea(nombre, monto, dato.estado, "costo", dato.fuente or dato.nota))
        else:
            resultado.faltantes.append(_faltante(nombre, dato))
            estados.append(ESTIMADO)
            lineas.append(Linea(nombre, None, DESCONOCIDO, "costo", dato.nota))

    comision = config_venta["comision_ml"]
    restar("Comisión de Mercado Libre", comision, lambda v: precio * v)
    if situacion != "responsable_inscripto" and comision.conocido:
        # Para monotributo, el IVA de la comisión es costo (para RI es crédito fiscal).
        restar("IVA sobre la comisión", config_venta["iva_sobre_comision"], lambda v: precio * comision.valor * v)
    restar("Costo fijo de Mercado Libre", config_venta["costo_fijo_ml_ars"], lambda v: v)
    restar("Envío a cargo del vendedor", config_venta["envio_ars"], lambda v: v)
    restar("Publicidad", config_venta["publicidad"], lambda v: precio * v)
    restar("Ingresos brutos sobre la venta", config_venta["iibb_venta"], lambda v: ingreso * v)

    ganancia = ingreso - costos
    estado = peor_estado(*estados)
    resultado.ganancia_ars = Dato(ganancia, estado, "Cálculo (buscador/costos.py)")
    resultado.margen = Dato(ganancia / ingreso, estado, "Cálculo (buscador/costos.py)")
    return resultado
