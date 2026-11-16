# Sistema de detección de oportunidades comerciales para Argentina — Diseño v1

Nov 15, 2026 · @Bruno

## 1. Evaluación de viabilidad

**Veredicto: viable, pero no como "buscador automático de productos ganadores".** Funciona como un motor que genera hipótesis y te ayuda a verificarlas, con vos decidiendo al final. La meta realista es 10 a 30 oportunidades bien investigadas por mes, no miles de productos con puntaje.

La razón es simple: la parte valiosa (¿se vende en Argentina?, ¿a qué costo llega?, ¿qué barrera explica que no esté?) es justo la que tiene menos datos abiertos. Lo internacional es fácil de conseguir; lo local y lo regulatorio, no.

### Limitaciones de acceso a datos (verificadas en noviembre 2026)

- **Mercado Libre, la fuente más crítica, ya no tiene búsqueda pública abierta para terceros.** La documentación actual muestra la búsqueda con token de usuario, y proyectos que la usaban la deprecaron por cambios de política. Hay que resolverlo con navegador asistido o con scrapers de terceros, con riesgo de términos de uso.
- **Amazon:** la Product Advertising API quedó deprecada y la reemplaza la Creators API, que exige ser afiliado elegible. Ninguna de las dos entrega Best Sellers ni Movers & Shakers como listado; eso requiere herramientas pagas o scraping.
- **Google Trends:** existe una API oficial, pero en alpha cerrada por solicitud. La librería no oficial pytrends fue archivada en abril de 2025.
- **Reddit:** gratis solo para uso no comercial aprobado. Las nuevas solicitudes cerraron el 31/10/2026 y el uso comercial requiere contrato. No conviene que el sistema dependa de Reddit en forma automática.
- **TikTok e Instagram:** útiles como señal temprana, pero miden atención, no ventas. Se usan solo para confirmar, nunca para puntuar demanda.

### Limitaciones comerciales y regulatorias

- **El régimen courier no sirve para un negocio de reventa.** Es para uso personal: 5 envíos por año, franquicia de USD 400, tope de USD 3.000 y hasta 3 unidades de la misma especie por envío. Sirve para traer muestras, no stock.
- **Importar para vender implica importación formal:** alta como importador, clasificación NCM, derecho de importación de 0 a 35% según posición, tasa de estadística de 3%, IVA 21%, más percepciones de IVA, Ganancias e IIBB. El módulo de rentabilidad tiene que modelar esto, no el courier.
- **La ausencia en Mercado Libre muchas veces tiene explicación:** certificaciones obligatorias (seguridad eléctrica, homologación de equipos inalámbricos, registro sanitario en cosméticos o productos de contacto con alimentos), costo logístico por volumen, o simplemente falta de demanda. Estos requisitos los marco como *a verificar con fuentes oficiales y un despachante* en cada ficha.

### Qué cambia respecto de la idea original

No descarto ninguna funcionalidad por inútil, pero sí cambio el orden: primero un pipeline chico y verificable sobre 1 o 2 categorías, después escala. Si el sistema no puede demostrar con evidencia por qué un producto tiene 70 puntos, ese puntaje no sirve.

## 2. Propuesta mejorada del concepto

**Propuesta: un "embudo de evidencia" en 4 etapas, donde cada producto avanza solo si junta pruebas, y la IA trabaja como analista, no como oráculo.**

1. **Descubrir (barato, amplio):** juntar candidatos desde señales de demanda real en el exterior (rankings de marketplaces, crowdfunding con dinero comprometido, búsquedas en crecimiento) y desde problemas de consumidores (reseñas negativas, foros). Salen cientos de candidatos por semana.
2. **Filtrar (automático):** descartar lo inviable antes de gastar tiempo: productos de marca protegida, categorías con barrera regulatoria fuerte, ticket muy bajo (donde el costo fijo de Mercado Libre se come el margen), volumen o peso que hace inviable el flete. Quedan decenas.
3. **Verificar Argentina (semiautomático):** para cada sobreviviente, medir oferta local (publicaciones, vendedores, precios, ventas visibles, calidad) y clasificar en poco explotado, emergente, oferta deficiente o saturado. Quedan 10 a 30.
4. **Modelar y decidir (con vos):** costo puesto en Argentina con importación formal, precio objetivo, margen, capital inicial, riesgos y una recomendación: investigar más, testear chico o descartar.

### Tres ideas que agrego al concepto original

- **Arbitraje regional como señal fuerte.** Si un producto ya funciona en Mercado Libre México, Brasil o Chile y no en Argentina, la evidencia vale más que un viral de TikTok en EE.UU.: mismo canal, consumidor más parecido y proveedores que ya exportan a la región.
- **"Mejorar lo que ya existe" como modalidad propia.** Muchas oportunidades reales en Argentina no son productos nuevos, sino productos que ya se venden mal: reseñas locales con quejas repetidas de calidad, falta de variantes o precio inflado. Es la categoría *oferta deficiente* y suele ser la más rentable para empezar.
- **Bitácora de evidencia por dato.** Cada número de la ficha guarda su fuente, la fecha y su estado (verificado, estimado o desconocido). Eso hace que el puntaje sea auditable y que los datos viejos pierdan peso solos.

### Lo que propongo no hacer (por ahora)

- **Monitoreo masivo y continuo de todas las fuentes:** caro, frágil y genera ruido. Mejor corridas semanales por categoría.
- **Detectar "lo que va a llegar pronto" como función aparte:** sale gratis del arbitraje regional y del historial de tendencias. No necesita un módulo propio.
- **Fabricación propia en la v1:** cambia el modelo de negocio y exige otro tipo de investigación. Queda para cuando haya un producto validado.

## 3. Funcionalidades: imprescindibles vs. posteriores

**La v1 tiene 7 funcionalidades; todo lo demás espera a que la v1 demuestre que encuentra oportunidades reales.**

| Funcionalidad | Versión | Por qué |
| --- | --- | --- |
| Búsqueda por categoría (Modalidad A) | v1 | Es la forma más barata de generar candidatos con datos comparables |
| Búsqueda por necesidad en texto libre (Modalidad B) | v1 | La IA traduce la necesidad a palabras clave y categorías; cuesta poco agregarla |
| Verificación en Mercado Libre Argentina + clasificación de mercado | v1 | Es el núcleo del valor; sin esto el sistema es una lista de Amazon |
| Calculadora de costo puesto y margen (importación formal + comisiones ML) | v1 | Sin margen no hay oportunidad; se alimenta con NCM y supuestos editables |
| Puntaje 0–100 con evidencia y nivel de confianza | v1 | Ordena el trabajo y obliga a justificar cada punto |
| Ficha individual con fuentes y conclusión | v1 | Es el entregable que usás para decidir |
| Favoritos y estado (investigar / testear / descartado) | v1 | Una columna en la base de datos; costo casi nulo |
| Filtros por categoría, país, precio y puntaje | v1.5 | Tiene sentido cuando haya más de 50 fichas |
| Arbitraje regional (ML México, Brasil, Chile) | v1.5 | Señal muy fuerte, misma técnica que ML Argentina |
| Detección de problemas en reseñas y foros | v1.5 | Valiosa pero más ruidosa; empezar con reseñas negativas de Amazon y ML |
| Detección de duplicados y similares | v1.5 | Necesaria cuando las corridas semanales se acumulen |
| Historial de tendencias y re-scoring periódico | v2 | Requiere semanas de datos guardados para tener sentido |
| Alertas por crecimiento de productos ya investigados | v2 | Sale del historial; no antes |
| Comparador de productos lado a lado | v2 | La tabla del dashboard cubre el 80% |
| Informes de oportunidades automáticos | v2 | Al principio, la ficha ya es el informe |
| Kickstarter / Indiegogo como fuente | v2 | Productos con años hasta llegar a mayoristas; más útil para detectar tendencias que para comprar ya |
| TikTok / Instagram automatizado | Descartado en v1 | Acceso restringido y señal de viralidad, no de ventas; uso manual como confirmación |

## 4. Fuentes de datos y cómo acceder

**Solo 3 fuentes tienen API oficial usable hoy sin contrato (AliExpress afiliados, Mercado Libre con token propio y eBay); el resto se resuelve con scrapers pagos por resultado, navegación asistida o carga manual.** Las filas marcadas "no verificado" las confirmo antes de programar.

| Fuente | Para qué | Acceso recomendado | Costo aprox. | Restricción clave | Uso en v1 |
| --- | --- | --- | --- | --- | --- |
| [Mercado Libre Argentina](https://developers.mercadolibre.com.ar/items-y-busquedas) | Oferta local, precios, vendedores | API con token de tu propia app para ítems y tendencias; búsqueda con navegador asistido o scraper de terceros | USD 0 a 10/mes | Búsqueda pública cerrada para terceros; scraping en zona gris de términos | Sí, núcleo |
| [ML Tendencias (/trends/MLA)](https://global-selling.mercadolibre.com/devsite/trends-gs) | Qué se busca en Argentina | API oficial con token, actualización semanal | USD 0 | Solo lo que ya se busca; no detecta lo ausente | Sí |
| [ML Costos por vender](https://developers.mercadolibre.com.ar/comision-por-vender) | Comisión real por categoría | API oficial con token | USD 0 | Requiere categoría y precio | Sí |
| ML México / Brasil / Chile | Arbitraje regional | Mismo método que Argentina ([scrapers multi-país](https://apify.com/bovi/mercadolibre-scraper.md)) | USD 5 a 20/mes | Tope de \~2.000 ítems por consulta | v1.5 |
| [Amazon](https://affiliate-program.amazon.com/creatorsapi/docs/en-us/paapiv5-deprecation) (Best Sellers, Movers & Shakers) | Demanda internacional | Scraper pago por resultado o herramienta tipo Keepa / Jungle Scout (no verificado) | USD 10 a 50/mes | PA-API deprecada; Creators API exige afiliado elegible y no lista rankings | Sí |
| [AliExpress Affiliate API](https://www.rapidevelopers.com/md/bubble-integrations/aliexpress-api) | Precio de origen, pedidos, productos "hot" | API oficial con cuenta de afiliado | USD 0 | Hot products requiere acceso avanzado | Sí |
| Alibaba / 1688 | Precio mayorista, MOQ, proveedores | Manual o navegador asistido en la etapa 4 | USD 0 | Sin API pública útil para esto (no verificado) | Manual |
| eBay Browse API | Precios y vendidos | API oficial gratuita con cuenta de desarrollador (no verificado) | USD 0 | Cuotas diarias | v1.5 |
| Etsy / Walmart | Nichos y productos artesanales / masivos | APIs con aprobación (no verificado) | USD 0 | Aprobación de la app | v2 |
| [Google Trends](https://developers.google.com/search/apis/trends) | Evolución de interés por país | Postular a la API alpha; mientras tanto, scraper pago o consulta manual | USD 0 a 10/mes | Alpha cerrada; pytrends archivado | Sí, para confirmar |
| [Kickstarter / Indiegogo](https://apify.com/automation-lab/kickstarter-scraper) | Innovación con dinero comprometido | Scraper pago por resultado (desde \~USD 2,6 cada 1.000 proyectos) | USD 1 a 5/mes | Sin API oficial | v2 |
| [Reddit](https://data365.co/blog/reddit-api-pricing) | Problemas y quejas | Lectura manual o agregador pago; nunca la API gratis para un fin comercial | USD 0 a 15/mes | Uso comercial requiere contrato; solicitudes cerradas 31/10/2026 | v1.5, manual |
| TikTok / Instagram / YouTube | Confirmación de interés | Revisión manual de la ficha | USD 0 | APIs restringidas (no verificado en esta ronda) | Manual |
| [ARCA / Arancel integrado](https://servicioscf.afip.gob.ar/publico/sitio/contenido/novedad/ver.aspx?id=5939) | NCM, derechos, régimen | Consulta manual por NCM + despachante para validar | USD 0 | La IA puede sugerir NCM, pero no confirmarlo | Sí, semiautomático |

**Regla de uso:** ninguna señal de redes sociales suma puntos de demanda por sí sola. Para puntuar demanda hace falta al menos una señal de compra: ranking de ventas, pedidos, "vendidos" visibles o dinero comprometido en crowdfunding.

## 5. Arquitectura técnica

**Arquitectura recomendada: 4 módulos independientes en Python que escriben en una sola base PostgreSQL (Supabase), con Claude como asistente de análisis y un dashboard simple encima.** Cada módulo se puede cambiar sin tocar los demás: si mañana Mercado Libre cambia algo, se reemplaza solo su colector.

&#91;embedded content: arquitectura · 4 módulos y una base única\]

Claude interpreta, clasifica y redacta, pero el puntaje y los costos salen de reglas en Python; todo dato queda guardado con su fuente y su fecha.

- **Por qué Python y no todo en n8n:** las reglas de costo, impuestos y puntaje necesitan tests y versiones; en Python se prueban fácil.
- **Por qué Supabase:** PostgreSQL real con plan gratuito, API automática para el dashboard y migración simple si crece.
- **Por qué corridas semanales:** las oportunidades de importación no cambian por hora; semanal baja costos y bloqueos.
- **Tablas principales:** candidatos, evidencias (dato, valor, fuente, fecha, estado verificado / estimado / desconocido), fichas, puntajes por versión de reglas y decisiones tuyas.

## 6. Puntaje, confianza y validación de calidad

**Mantengo tus pesos, pero cada criterio se calcula con reglas fijas en código y la IA solo redacta la justificación.** Así el mismo producto da el mismo puntaje dos veces, y un dato faltante baja el puntaje en vez de inventarse.

| Criterio | Puntos | Evidencia que cuenta | Tope si falta el dato clave |
| --- | --- | --- | --- |
| Demanda internacional | 20 | Ranking de ventas, pedidos, "vendidos", reseñas recientes, crowdfunding financiado | Máx. 6 si solo hay señales de redes |
| Oportunidad en Argentina | 25 | Nº de publicaciones y vendedores en ML, ventas visibles, brecha de precio y calidad, búsquedas locales | Máx. 8 sin búsqueda verificada en ML |
| Rentabilidad potencial | 20 | Margen bruto con costo puesto (importación formal) y precio local de referencia | Máx. 5 sin NCM o sin precio de proveedor |
| Diferenciación y propuesta de valor | 15 | Problema concreto resuelto, ventaja frente a sustitutos locales, quejas de reseñas que resuelve | Máx. 7 si no hay sustitutos analizados |
| Facilidad logística y regulatoria | 10 | Peso/volumen, fragilidad, certificaciones requeridas, marca protegida | 0 si hay certificación obligatoria sin evaluar |
| Tendencia y proyección | 10 | Pendiente de interés a 12 meses en 2 o más países, aparición en ML de la región | Máx. 3 con una sola serie |

### Nivel de confianza

- **Alto:** los 6 criterios con al menos un dato verificado, y precio local y de proveedor con fecha de menos de 30 días.
- **Medio:** falta un criterio o hay datos estimados en rentabilidad.
- **Bajo:** faltan 2 o más criterios, o la oportunidad en Argentina no se verificó en ML. Una ficha de confianza baja nunca aparece por encima de una de confianza media en el ranking, aunque tenga más puntos.

### Cómo validar que el sistema sirve

1. **Prueba hacia atrás:** elegir 10 a 15 productos que se volvieron comunes en Mercado Libre Argentina en los últimos 12 a 24 meses y ver si el sistema los hubiera marcado con datos de antes. Si no marca ninguno, el problema está en las fuentes o en el puntaje.
2. **Auditoría manual:** cada semana revisás 5 fichas al azar. Métrica: porcentaje de datos que coinciden con lo que ves en la fuente original. Objetivo: 90% o más antes de confiar en el ranking.
3. **Precisión del top 10:** de las 10 mejores fichas del mes, ¿cuántas considerás dignas de pedir cotización? Si son menos de 3, se ajustan pesos o filtros.
4. **Prueba de mercado:** la validación final no es técnica. 1 o 2 productos por trimestre pasan a prueba chica (muestras por courier, publicación de prueba o preventa) y el resultado vuelve al sistema para calibrar.

## 7. MVP económico y plan por etapas

**Recomiendo empezar sin programar: 2 a 3 semanas de "MVP manual asistido" donde yo investigo con web y navegador siguiendo exactamente la metodología de este documento.** Si las fichas no te convencen hechas a mano, automatizarlas no las va a mejorar.

### Etapas

1. **Fase 0 — Metodología a mano (semanas 1 a 3, USD 0 extra).** Elegimos 2 categorías (sugerencia: Organización y almacenamiento + Mascotas, por ticket medio y baja barrera regulatoria). Produzco 15 a 20 fichas con el formato final, en una planilla de oportunidades y fichas en este proyecto. Hacemos la prueba hacia atrás. *Criterio para avanzar:* al menos 3 fichas por las que pedirías cotización.
2. **Fase 1 — Pipeline mínimo (semanas 4 a 7, USD 15 a 50/mes).** Scripts en Python que corren una vez por semana: candidatos desde Amazon y AliExpress, verificación en ML Argentina, cálculo de costo y puntaje con reglas fijas, fichas redactadas por Claude. Base en Supabase (plan gratuito) y un dashboard simple. *Criterio:* 90% de exactitud en la auditoría manual.
3. **Fase 2 — Señales más finas (semanas 8 a 12).** Arbitraje regional con ML México, Brasil y Chile; análisis de reseñas negativas; Modalidad B por necesidad; duplicados. *Criterio:* el top 10 mensual tiene 3 o más productos accionables.
4. **Fase 3 — Memoria y alertas (mes 4 en adelante).** Historial semanal, re-scoring, alertas por crecimiento, informes. Solo si las fases anteriores ya generaron al menos una prueba de mercado.

### Costo mensual estimado de la Fase 1

Todos son **estimados**; confirmo precios vigentes antes de contratar.

| Componente | Opción | Costo estimado |
| --- | --- | --- |
| Ejecución de scripts | Tu PC, GitHub Actions o un VPS chico | USD 0 a 6 |
| Base de datos | Supabase plan gratuito (PostgreSQL) | USD 0 |
| Scrapers pagos por resultado | Apify u otro similar, con límite de gasto | USD 5 a 30 |
| IA para clasificar y redactar | API de Claude, modelos chicos para clasificar y uno grande solo para las fichas finales | USD 5 a 20 |
| Interfaz | Streamlit o un dashboard publicado como artefacto | USD 0 |
| **Total** |  | **USD 10 a 56** |

**Sobre n8n:** sirve si preferís no mantener código, pero la lógica de puntaje y costos queda más clara y testeable en Python. Propongo Python para el núcleo y n8n solo si después querés alertas por WhatsApp o mail sin programar.

## 8. Ejemplo de búsqueda y presentación de resultados

**Este ejemplo muestra el recorrido y el formato, no resultados reales:** los números de costo son un cálculo hipotético con las alícuotas vigentes, y los productos se investigan en la Fase 0. No invento ventas ni precios para que el ejemplo luzca mejor.

### Consulta (Modalidad B)

> "Productos para ahorrar espacio en departamentos pequeños, precio internacional menor a USD 30, mirar EE.UU., Japón, Corea y México."

### Qué hace el sistema

1. **Interpreta la necesidad:** la IA la traduce a subnecesidades (guardado vertical, muebles plegables, organización de placard, cocina compacta, baño sin perforar) y a palabras clave en inglés, japonés, coreano y español.
2. **Descubre:** consulta rankings de Amazon EE.UU. y Japón en Hogar y Organización, productos de AliExpress con más pedidos para esas palabras y ML México. Resultado típico: 200 a 400 candidatos.
3. **Filtra:** saca marcas protegidas, productos de más de 5 kg o voluminosos, ticket local estimado muy bajo y lo que necesita certificación eléctrica. Quedan 30 a 60.
4. **Verifica en Argentina:** para cada uno busca en ML Argentina con 2 o 3 formulaciones, cuenta publicaciones relevantes, vendedores, ventas visibles, rango de precio y calidad de las fotos y reseñas. Asigna la clasificación de mercado.
5. **Modela y puntúa:** sugiere NCM (a confirmar), calcula costo puesto, margen y puntaje, y redacta la ficha.

### Cómo se ve el ranking

| # | Producto | Mercado AR | Puntaje | Confianza | Margen bruto est. | Recomendación |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | *(producto real de la Fase 0)* | Oferta deficiente | 0–100 | Alta / media / baja | % con supuestos visibles | Testear chico / investigar / descartar |

Cada fila abre su ficha completa con los 20 puntos que pediste y la conclusión.

### Ejemplo del bloque de rentabilidad en una ficha (hipotético)

Supuestos: lote de 500 unidades, FOB USD 4,00 por unidad, flete y seguro USD 1,00 por unidad, derecho de importación supuesto del 20% (depende del NCM real).

| Concepto | Por unidad (USD) | Estado del dato |
| --- | --- | --- |
| FOB (precio del proveedor) | 4,00 | Estimado: falta cotización |
| Flete + seguro internacional | 1,00 | Estimado: falta cotización de forwarder |
| CIF | 5,00 | Calculado |
| Derecho de importación (20% supuesto) | 1,00 | Desconocido: confirmar NCM |
| Tasa de estadística (3%) | 0,15 | Verificado (alícuota vigente) |
| Base imponible IVA | 6,15 | Calculado |
| IVA 21% + IVA adicional 20% | 2,52 | Verificado; recuperable como crédito fiscal si sos responsable inscripto |
| Percepción Ganancias 6% | 0,37 | Verificado; pago a cuenta |
| Despachante, depósito, flete local | ? | Desconocido: pedir presupuesto |
| **Costo definitivo (sin créditos fiscales ni gastos locales)** | **6,15** | Calculado |

Del lado de la venta, la ficha resta del precio local: comisión de ML según categoría y tipo de publicación (aprox. 12% a 17%), costo fijo por unidad en productos baratos, IVA sobre la comisión, envío y publicidad. Si el precio local de referencia no se pudo verificar, el margen queda como **desconocido** y el criterio de rentabilidad no supera 5 puntos.

### Cierre de la ficha (formato)

- **Por qué podría funcionar:** una o dos frases con la evidencia concreta.
- **Quién lo compraría:** segmento y canal (ML, Instagram, tienda propia).
- **Ventaja frente a lo actual:** precio, calidad, variante o función.
- **Qué validar antes de invertir:** lista de 3 a 5 datos desconocidos, con cómo conseguir cada uno.
- **Recomendación:** investigar más, testear en pequeña escala o descartar.

## 9. Decisiones pendientes y próximos pasos

**Para arrancar la Fase 0 necesito 4 definiciones tuyas; el resto lo puedo avanzar yo.**

- [ ] **Categorías iniciales:** ¿confirmás Organización + Mascotas, o preferís otras 2?
- [ ] **Capital y escala:** rango de capital inicial que estás dispuesto a poner en la primera prueba (define si apuntamos a importación formal propia, a importadores locales o a compra mayorista local).
- [ ] **Situación fiscal:** ¿sos responsable inscripto, monotributista o todavía nada? Cambia qué impuestos son costo y cuáles crédito.
- [ ] **Canal de venta:** ¿solo Mercado Libre, o también Instagram o tienda propia? Cambia las comisiones del modelo.
- [ ] **Postular a la API alpha de Google Trends** con tu cuenta (gratis, sin compromiso).
- [ ] **Crear una app de desarrollador en Mercado Libre** con tu cuenta para habilitar ítems, tendencias y costos por vender.
- [ ] **Conseguir un despachante de aduana de referencia** para validar NCM y gastos locales de las primeras fichas.

## 10. Fuentes consultadas

- [Mercado Libre Developers — Ítems y búsquedas](https://developers.mercadolibre.com.ar/items-y-busquedas)
- [Mercado Libre Developers — Tendencias](https://global-selling.mercadolibre.com/devsite/trends-gs)
- [Mercado Libre Developers — Costos por vender](https://developers.mercadolibre.com.ar/comision-por-vender)
- [mercadolibre-mcp: deprecación de la búsqueda por cambios de política](https://glama.ai/mcp/servers/@lumile/mercadolibre-mcp/blob/af6ee3e6cf55c33745041d8b42cdb82f201bcabf/README.md)
- [Amazon — Deprecación de PA-API 5 y Creators API](https://affiliate-program.amazon.com/creatorsapi/docs/en-us/paapiv5-deprecation)
- [Google — Acceso anticipado a la API alpha de Trends](https://developers.google.com/search/apis/trends)
- [Scrapfly — Estado de la API de Trends y pytrends](https://scrapfly.io/blog/posts/google-trends-api-alternatives)
- [Data365 — Precios y reglas de la API de Reddit 2026](https://data365.co/blog/reddit-api-pricing)
- [ARCA — Régimen de Courier (06/10/2026)](https://servicioscf.afip.gob.ar/publico/sitio/contenido/novedad/ver.aspx?id=5939)
- [iProfesional — Cómo funciona el courier y sus límites](https://www.iprofesional.com/finanzas/463617-como-funciona-el-sistema-de-courier-para-compras-en-shein-y-temu.amp)
- [Chilat — Aranceles China–Argentina 2026](https://www.chilat.com/blog/2094245127212392449)
- [Arancely — Impuestos de importación explicados](https://www.arancely.com/blog/impuestos-importacion-argentina-explicados)
- [Algoritmo Digital — Comisiones de Mercado Libre 2026](https://algoritmodigital.com.ar/cuanto-es-la-comision-de-mercado-libre-por-vender/)
- [AliExpress API — niveles de acceso](https://www.rapidevelopers.com/md/bubble-integrations/aliexpress-api)
- [Apify — Kickstarter Scraper](https://apify.com/automation-lab/kickstarter-scraper)
