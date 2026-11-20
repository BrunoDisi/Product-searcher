"""Un "Dato": un valor con su fuente, su fecha y su estado.

Regla del proyecto: ningún número anda suelto. Todo precio, venta, costo o
impuesto se guarda como Dato, para saber de dónde salió y cuánto confiar.
"""

from dataclasses import dataclass
from datetime import date
from typing import Any

VERIFICADO = "verificado"
ESTIMADO = "estimado"
DESCONOCIDO = "desconocido"
ESTADOS = (VERIFICADO, ESTIMADO, DESCONOCIDO)

# Orden de "gravedad": cuanto más alto, menos confiable.
_GRAVEDAD = {VERIFICADO: 0, ESTIMADO: 1, DESCONOCIDO: 2}


@dataclass(frozen=True)
class Dato:
    valor: Any = None
    estado: str = DESCONOCIDO
    fuente: str = ""
    fecha: date | None = None
    nota: str = ""  # aclaración, o cómo conseguir el dato si falta

    def __post_init__(self):
        if self.estado not in ESTADOS:
            raise ValueError(f"Estado inválido: {self.estado!r}. Usá uno de {ESTADOS}.")
        if self.estado == DESCONOCIDO and self.valor is not None:
            raise ValueError("Un dato desconocido no puede tener valor.")
        if self.estado != DESCONOCIDO and self.valor is None:
            raise ValueError(f"Un dato {self.estado} necesita un valor.")
        if self.estado == VERIFICADO and not (self.fuente and self.fecha):
            raise ValueError("Un dato verificado necesita fuente y fecha.")

    @property
    def conocido(self) -> bool:
        return self.estado != DESCONOCIDO


def desconocido(como_conseguirlo: str = "") -> Dato:
    """Atajo para crear un dato que falta, diciendo cómo conseguirlo."""
    return Dato(estado=DESCONOCIDO, nota=como_conseguirlo)


def peor_estado(*estados: str) -> str:
    """El estado menos confiable de la lista (un cálculo vale lo que su peor dato)."""
    if not estados:
        return VERIFICADO
    return max(estados, key=lambda e: _GRAVEDAD[e])
