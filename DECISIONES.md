# Decisiones del proyecto

Cada decisión importante, con fecha y por qué se tomó. Lo más nuevo va abajo.

## 2026-11-20 — Plan aprobado

1. **SQLite local en vez de Supabase** (DISENO.md proponía Supabase).
   Por qué: es un solo archivo, sin cuentas ni costo, alcanza para cientos de fichas. Si después lo usan varias personas a la vez, se migra.

2. **Programar en paralelo con la Fase 0 manual** (DISENO.md proponía 2–3 semanas sin programar).
   Por qué: la Etapa 1 no usa fuentes externas; las fichas hechas a mano sirven para calibrar costos y puntaje.

3. **Filtros (país, precio, puntaje) en la Etapa 3** (DISENO.md los dejaba para v1.5). Pedido explícito del usuario y son baratos.

4. **Modo libre con tope de candidatos por corrida** (DISENO.md recomienda no barrer todo masivamente). El tope va en configuración.

5. **Favoritos y estado de seguimiento** (investigar / testear / descartado): solo columnas en la base, sin pantalla propia.

6. **Sin gasto de dinero: no se usa la API de Claude** (DISENO.md estimaba USD 5–20/mes).
   Por qué: el usuario quiere usar solo su plan Claude Pro. La parte de IA (interpretar la frase del modo "por necesidad", clasificar, redactar justificaciones) la hace Claude Code durante la sesión. El programa hace todo lo mecánico sin IA.
   Consecuencia: un compañero puede usar todo lo mecánico (colectores, costos, puntaje, planilla, dashboard); para la parte de IA necesita su propio acceso a Claude Code.

7. **GitHub (repo privado) para guardar y compartir el proyecto.**

## 2026-11-20 — Etapa 1

8. **Configuración en archivos `.toml`.** Python 3.11+ los lee sin instalar nada y son fáciles de editar a mano.

9. **Las alícuotas se cargan como "estimado" y "a confirmar".** Vienen de la investigación de DISENO.md (nov 2026), no de una consulta directa a ARCA. Pasan a "verificado" solo cuando se confirman con fuente oficial o despachante, y se actualiza la fecha.

10. **Si falta el NCM, el derecho de importación se supone en 35%** (el máximo del Arancel Externo Común) y el costo queda "estimado".
    Por qué: es el supuesto conservador; nunca hace ver más rentable un producto de lo que es. Editable en `config/importacion.toml`.

11. **Redes sociales sin señal de compra = 0 puntos de demanda.**
    DISENO.md decía "máx. 6 si solo hay señales de redes"; la regla del usuario es más estricta ("no suman puntos por sí solas") y prevalece.

12. **La clasificación de mercado (poco explotado / emergente / oferta deficiente / saturado) se calcula con reglas en código**, no la decide la IA, porque alimenta el puntaje y tiene que dar siempre lo mismo.

13. **Gastos que faltan no se inventan.** El costo y el margen se calculan con lo que se conoce y la ficha lista lo que falta ("faltantes"). Si falta un dato clave (precio del proveedor o precio local), el resultado queda desconocido.

14. **Umbrales del puntaje (versión `v1-2026-11-20`)** escritos en `buscador/puntaje.py`. Ejemplos: más de 10.000 pedidos = señal fuerte; 5 vendedores o menos en ML = poco explotado; más de 20 = saturado (salvo quejas de calidad: oferta deficiente). Son un punto de partida para calibrar con las fichas de la Fase 0 y la prueba hacia atrás.

15. **Consecuencia buscada: mientras las alícuotas sigan como "estimado", ningún producto llega a confianza alta**, porque el margen hereda el estado de su dato menos confiable. Para destrabarlo hay que confirmar las alícuotas con un despachante y marcarlas "verificado".

16. **Si no se buscó en Mercado Libre Argentina, no cuentan las ventas de ML** (se encontró y corrigió al revisar el ejemplo).
