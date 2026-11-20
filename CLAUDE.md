# Reglas del proyecto (Product-searcher)

Herramienta para encontrar IDEAS de productos con potencial para un ecommerce en Argentina.
El diseño completo está en DISENO.md; las decisiones tomadas, en DECISIONES.md.

## Reglas que no se negocian
- No inventar datos. Todo dato se guarda como `Dato` (valor, fuente, fecha, estado: verificado / estimado / desconocido). Si falta, queda desconocido y se dice cómo conseguirlo.
- La viralidad no es demanda: redes sociales no suman puntos de demanda sin una señal de compra (ranking, pedidos, vendidos, crowdfunding financiado).
- No estar en Mercado Libre Argentina no es oportunidad sin revisar barreras (certificación, marca, flete, falta de demanda).
- El puntaje (0–100) sale de reglas fijas en `buscador/puntaje.py`. La IA solo clasifica, interpreta y redacta.
- Costos con importación formal (no courier). Alícuotas en `config/importacion.toml`, con fecha y "a confirmar".
- Mercado Libre Argentina solo mide competencia y precios locales.
- Solo APIs oficiales o métodos que respeten términos. No saltear bloqueos.
- Claves solo en `.env` (está en .gitignore). Nunca en código.
- No gastar dinero: sin servicios pagos ni API de Claude. La parte de IA la hace Claude Code en la sesión.
- Preguntar antes de instalar algo.

## Forma de trabajo
- Usuario principiante: explicar simple, pasos chicos, avisar antes de hacer.
- Python + herramientas gratuitas. No agregar funciones no pedidas.
- Commits chicos con mensajes claros. Correr `python -m pytest` antes de cada commit.
- Anotar decisiones importantes en DECISIONES.md.
