"""Puntaje 0-100 y nivel de confianza, con reglas FIJAS (la IA no decide).

Pesos: demanda internacional 20, oportunidad en Argentina 25, rentabilidad 20,
diferenciación 15, logística y regulación 10, tendencia 10.

Si cambiás una regla o un umbral, subí VERSION_REGLAS: así se sabe con qué
reglas se calculó cada puntaje guardado.
"""

from dataclasses import asdict, dataclass, field
from datetime import date

from buscador.dato import VERIFICADO, Dato

VERSION_REGLAS = "v1-2026-11-20"

ALTA, MEDIA, BAJA = "alta", "media", "baja"
_ORDEN_CONFIANZA = {ALTA: 0, MEDIA: 1, BAJA: 2}

POCO_EXPLOTADO = "poco explotado"
EMERGENTE = "emergente"
OFERTA_DEFICIENTE = "oferta deficiente"
SATURADO = "saturado"
SIN_CLASIFICAR = "sin clasificar"

DIAS_DATO_FRESCO = 30


# ---------------------------------------------------------------- entradas

@dataclass
class SenalCompra:
    """Señal de que la gente COMPRA (no solo mira).

    tipo: "pedidos" o "vendidos" (unidades), "ranking" (puesto en el ranking de
    ventas de su categoría, 1 = el más vendido) o "crowdfunding" (USD financiados).
    """
    tipo: str
    plataforma: str
    pais: str
    dato: Dato


@dataclass
class SerieTendencia:
    """Variación del interés en 12 meses en un país (0.30 = +30%)."""
    pais: str
    variacion_12m: Dato


def _d() -> Dato:
    return field(default_factory=Dato)


@dataclass
class Evaluacion:
    """Todo lo que el puntaje necesita saber de un producto. Lo que no se sabe, queda desconocido."""
    # Demanda internacional
    senales_compra: list[SenalCompra] = field(default_factory=list)
    senales_redes: list[Dato] = field(default_factory=list)  # solo informativo: NO suma puntos
    # Oportunidad en Argentina (Mercado Libre)
    ml_buscado: Dato = _d()          # True si se hizo la búsqueda en ML Argentina
    vendedores_ml: Dato = _d()       # cantidad de vendedores con publicaciones relevantes
    ventas_visibles_ml: Dato = _d()  # suma de "vendidos" visibles
    quejas_calidad_ml: Dato = _d()   # True si hay quejas repetidas de calidad en ML
    busquedas_locales: Dato = _d()   # True si aparece en tendencias de búsqueda de ML Argentina
    barreras_revisadas: Dato = _d()  # True si se revisó por qué no está (o está poco)
    barrera_ausencia: Dato = _d()    # "ninguna", "certificacion", "marca", "flete" o "falta_demanda"
    # Rentabilidad
    margen: Dato = _d()              # sale de costos.calcular_margen (0.30 = 30%)
    ncm: Dato = _d()
    fob_usd: Dato = _d()
    precio_ml_ars: Dato = _d()
    # Diferenciación
    problema_concreto: Dato = _d()   # True si resuelve un problema concreto
    sustitutos_analizados: Dato = _d()
    ventaja: Dato = _d()             # "ninguna", "menor" o "clara" frente a sustitutos locales
    resuelve_quejas: Dato = _d()     # True si resuelve quejas de reseñas de productos actuales
    # Logística y regulación
    peso_kg: Dato = _d()
    fragil: Dato = _d()
    certificacion: Dato = _d()       # "no_requiere", "requiere_factible" o "requiere_inviable"
    marca_protegida: Dato = _d()
    # Tendencia
    series_tendencia: list[SerieTendencia] = field(default_factory=list)
    en_ml_region: Dato = _d()        # True si ya se vende en ML México, Brasil o Chile


# ---------------------------------------------------------------- salidas

@dataclass
class ResultadoCriterio:
    nombre: str
    puntos: float
    maximo: int
    tiene_dato_clave: bool
    verificado: bool  # al menos un dato verificado
    tope: int | None = None
    motivos: list[str] = field(default_factory=list)


@dataclass
class ResultadoPuntaje:
    total: float
    confianza: str
    clasificacion_mercado: str
    criterios: list[ResultadoCriterio]
    motivos_confianza: list[str]
    version_reglas: str = VERSION_REGLAS

    def como_dict(self) -> dict:
        return asdict(self)


# ---------------------------------------------------------------- ayudas

def _valor(dato: Dato):
    return dato.valor if dato.conocido else None


def _hay_verificado(*datos: Dato) -> bool:
    return any(d.estado == VERIFICADO for d in datos)


def _cerrar(c: ResultadoCriterio, tope: int | None, motivo_tope: str) -> ResultadoCriterio:
    c.puntos = max(0, min(c.puntos, c.maximo))
    if tope is not None and c.puntos > tope:
        c.puntos = tope
    if tope is not None:
        c.tope = tope
        c.motivos.append(f"Tope {tope}: {motivo_tope}")
    return c


# ---------------------------------------------------------------- criterios

def puntuar_demanda(ev: Evaluacion) -> ResultadoCriterio:
    senales = [s for s in ev.senales_compra if s.dato.conocido]
    c = ResultadoCriterio("Demanda internacional", 0, 20, bool(senales),
                          _hay_verificado(*(s.dato for s in senales)))
    if not senales:
        if ev.senales_redes:
            c.motivos.append("Solo hay señales de redes: la viralidad no es demanda (0 puntos).")
        c.motivos.append("Falta una señal de compra: ranking, pedidos, vendidos o crowdfunding.")
        return c

    def fuerza(s: SenalCompra) -> int:
        v = s.dato.valor
        if s.tipo in ("pedidos", "vendidos"):
            return 12 if v >= 10_000 else 9 if v >= 1_000 else 5 if v >= 100 else 2
        if s.tipo == "ranking":
            return 12 if v <= 100 else 8 if v <= 1_000 else 4
        if s.tipo == "crowdfunding":
            return 12 if v >= 500_000 else 8 if v >= 100_000 else 4
        raise ValueError(f"Tipo de señal desconocido: {s.tipo!r}")

    mejor = max(senales, key=fuerza)
    c.puntos = fuerza(mejor)
    c.motivos.append(f"Mejor señal: {mejor.tipo} en {mejor.plataforma} ({mejor.pais}) = {mejor.dato.valor} "
                     f"→ {c.puntos} pts.")
    if len({s.plataforma for s in senales}) >= 2:
        c.puntos += 4
        c.motivos.append("Señales de compra en 2 o más plataformas → +4.")
    if len({s.pais for s in senales}) >= 2:
        c.puntos += 4
        c.motivos.append("Señales de compra en 2 o más países → +4.")
    return _cerrar(c, None, "")


def clasificar_mercado(ev: Evaluacion) -> str:
    """Clasificación del mercado argentino según lo visto en Mercado Libre."""
    if _valor(ev.ml_buscado) is not True or not ev.vendedores_ml.conocido:
        return SIN_CLASIFICAR
    vendedores = ev.vendedores_ml.valor
    if _valor(ev.quejas_calidad_ml) is True:
        return OFERTA_DEFICIENTE
    if vendedores <= 5:
        return POCO_EXPLOTADO
    if vendedores <= 20:
        return EMERGENTE
    return SATURADO


def puntuar_oportunidad(ev: Evaluacion) -> ResultadoCriterio:
    buscado = _valor(ev.ml_buscado) is True
    c = ResultadoCriterio("Oportunidad en Argentina", 0, 25, buscado,
                          _hay_verificado(ev.ml_buscado, ev.vendedores_ml, ev.ventas_visibles_ml))
    clasificacion = clasificar_mercado(ev)
    base = {POCO_EXPLOTADO: 16, EMERGENTE: 13, OFERTA_DEFICIENTE: 17, SATURADO: 3, SIN_CLASIFICAR: 0}
    c.puntos = base[clasificacion]
    c.motivos.append(f"Mercado: {clasificacion} → {c.puntos} pts.")
    if buscado and (_valor(ev.ventas_visibles_ml) or 0) > 0:
        c.puntos += 5
        c.motivos.append("Hay ventas visibles en ML Argentina → +5.")
    if _valor(ev.busquedas_locales) is True:
        c.puntos += 3
        c.motivos.append("Aparece en búsquedas de ML Argentina → +3.")

    if not buscado:
        return _cerrar(c, 8, "no se verificó la búsqueda en Mercado Libre Argentina.")
    barrera = _valor(ev.barrera_ausencia)
    if barrera == "falta_demanda":
        c.puntos = 0
        c.motivos.append("La poca presencia se explica por falta de demanda → 0.")
        return c
    if clasificacion == POCO_EXPLOTADO:
        if _valor(ev.barreras_revisadas) is not True:
            return _cerrar(c, 8, "no estar en ML no es oportunidad hasta revisar barreras.")
        if barrera not in (None, "ninguna"):
            return _cerrar(c, 8, f"la ausencia se explica por una barrera ({barrera}).")
    return _cerrar(c, None, "")


def puntuar_rentabilidad(ev: Evaluacion) -> ResultadoCriterio:
    margen = _valor(ev.margen)
    c = ResultadoCriterio("Rentabilidad potencial", 0, 20, margen is not None,
                          _hay_verificado(ev.margen, ev.fob_usd, ev.precio_ml_ars, ev.ncm))
    if margen is None:
        c.motivos.append("Margen desconocido: falta precio del proveedor, precio local o tipo de cambio.")
        return c
    c.puntos = 20 if margen >= 0.40 else 16 if margen >= 0.30 else 11 if margen >= 0.20 else 5 if margen >= 0.10 else 0
    c.motivos.append(f"Margen {margen:.0%} → {c.puntos} pts.")
    if not ev.ncm.conocido or not ev.fob_usd.conocido:
        return _cerrar(c, 5, "falta NCM o precio del proveedor.")
    return _cerrar(c, None, "")


def puntuar_diferenciacion(ev: Evaluacion) -> ResultadoCriterio:
    analizados = _valor(ev.sustitutos_analizados) is True
    c = ResultadoCriterio("Diferenciación", 0, 15, analizados,
                          _hay_verificado(ev.problema_concreto, ev.sustitutos_analizados, ev.ventaja,
                                          ev.resuelve_quejas))
    if _valor(ev.problema_concreto) is True:
        c.puntos += 4
        c.motivos.append("Resuelve un problema concreto → +4.")
    ventaja = _valor(ev.ventaja)
    if ventaja == "clara":
        c.puntos += 6
        c.motivos.append("Ventaja clara frente a sustitutos → +6.")
    elif ventaja == "menor":
        c.puntos += 3
        c.motivos.append("Ventaja menor frente a sustitutos → +3.")
    if _valor(ev.resuelve_quejas) is True:
        c.puntos += 5
        c.motivos.append("Resuelve quejas de reseñas de productos actuales → +5.")
    if not analizados:
        return _cerrar(c, 7, "no se analizaron los sustitutos locales.")
    return _cerrar(c, None, "")


def puntuar_logistica(ev: Evaluacion) -> ResultadoCriterio:
    cert = _valor(ev.certificacion)
    c = ResultadoCriterio("Logística y regulación", 0, 10, cert is not None,
                          _hay_verificado(ev.certificacion, ev.peso_kg, ev.marca_protegida))
    if cert is None:
        c.motivos.append("Certificación sin evaluar → 0.")
        return c
    if cert == "requiere_inviable":
        c.motivos.append("Requiere certificación inviable → 0.")
        return c
    if _valor(ev.marca_protegida) is True:
        c.motivos.append("Marca protegida → 0.")
        return c
    c.puntos += 4 if cert == "no_requiere" else 1
    c.motivos.append(f"Certificación: {cert}.")
    peso = _valor(ev.peso_kg)
    if peso is not None:
        c.puntos += 4 if peso <= 1 else 3 if peso <= 3 else 1 if peso <= 5 else 0
        c.motivos.append(f"Peso {peso} kg.")
    else:
        c.motivos.append("Peso desconocido (0 pts por peso).")
    if _valor(ev.marca_protegida) is False:
        c.puntos += 2
        c.motivos.append("Sin marca protegida → +2.")
    if _valor(ev.fragil) is True:
        c.puntos -= 2
        c.motivos.append("Frágil → -2.")
    return _cerrar(c, None, "")


def puntuar_tendencia(ev: Evaluacion) -> ResultadoCriterio:
    series = [s for s in ev.series_tendencia if s.variacion_12m.conocido]
    region = _valor(ev.en_ml_region) is True
    c = ResultadoCriterio("Tendencia", 0, 10, bool(series),
                          _hay_verificado(ev.en_ml_region, *(s.variacion_12m for s in series)))
    if series:
        promedio = sum(s.variacion_12m.valor for s in series) / len(series)
        c.puntos = 7 if promedio >= 0.5 else 5 if promedio >= 0.2 else 3 if promedio >= 0 else 0
        c.motivos.append(f"Variación promedio a 12 meses {promedio:+.0%} en {len(series)} país(es) → {c.puntos} pts.")
    if region:
        c.puntos += 3
        c.motivos.append("Ya se vende en ML de la región → +3.")
    if len(series) < 2:
        return _cerrar(c, 3, "menos de 2 series de tendencia.")
    return _cerrar(c, None, "")


# ---------------------------------------------------------------- total

def _fresco(dato: Dato, hoy: date) -> bool:
    return dato.estado == VERIFICADO and dato.fecha is not None and (hoy - dato.fecha).days < DIAS_DATO_FRESCO


def calcular_confianza(ev: Evaluacion, criterios: list[ResultadoCriterio], hoy: date) -> tuple[str, list[str]]:
    motivos = []
    sin_dato = [c.nombre for c in criterios if not c.tiene_dato_clave]
    if sin_dato:
        motivos.append(f"Criterios sin dato clave: {', '.join(sin_dato)}.")
    if _valor(ev.ml_buscado) is not True:
        motivos.append("La oportunidad en Argentina no se verificó en Mercado Libre.")
    if len(sin_dato) >= 2 or _valor(ev.ml_buscado) is not True:
        return BAJA, motivos

    todos_verificados = all(c.verificado for c in criterios)
    precios_frescos = _fresco(ev.precio_ml_ars, hoy) and _fresco(ev.fob_usd, hoy)
    if not todos_verificados:
        motivos.append("No todos los criterios tienen al menos un dato verificado.")
    if not precios_frescos:
        motivos.append(f"Precio local y de proveedor verificados hace menos de {DIAS_DATO_FRESCO} días: no.")
    margen_verificado = ev.margen.estado == VERIFICADO
    if not margen_verificado:
        motivos.append("La rentabilidad usa datos estimados.")
    if not sin_dato and todos_verificados and precios_frescos and margen_verificado:
        return ALTA, motivos
    return MEDIA, motivos


def calcular_puntaje(ev: Evaluacion, hoy: date | None = None) -> ResultadoPuntaje:
    hoy = hoy or date.today()
    criterios = [puntuar_demanda(ev), puntuar_oportunidad(ev), puntuar_rentabilidad(ev),
                 puntuar_diferenciacion(ev), puntuar_logistica(ev), puntuar_tendencia(ev)]
    confianza, motivos = calcular_confianza(ev, criterios, hoy)
    total = sum(c.puntos for c in criterios)
    return ResultadoPuntaje(total, confianza, clasificar_mercado(ev), criterios, motivos)


def clave_ranking(resultado: ResultadoPuntaje):
    """Para ordenar: primero la confianza (alta > media > baja), después el puntaje.
    Una ficha de confianza baja nunca queda arriba de una de confianza media."""
    return (_ORDEN_CONFIANZA[resultado.confianza], -resultado.total)
