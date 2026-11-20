# Product-searcher

Herramienta para encontrar ideas de productos con potencial para vender en Argentina.
Diseño: [DISENO.md](DISENO.md) · Decisiones: [DECISIONES.md](DECISIONES.md)

## Instalación (una sola vez)

Necesitás Python 3.11 o más nuevo.

```bash
pip install -r requirements.txt
```

## Comandos

Correr las pruebas automáticas:

```bash
python -m pytest
```

Ver el ejemplo de costos y puntaje:

```bash
python -m buscador.demo
```

## Dónde se edita cada cosa

| Archivo | Qué tiene |
| --- | --- |
| `config/categorias.toml` | Lista de categorías para el modo "por categoría" |
| `config/importacion.toml` | Alícuotas de importación formal, con fecha y estado |
| `config/venta.toml` | Situación fiscal, tipo de cambio, comisiones y gastos de venta |
