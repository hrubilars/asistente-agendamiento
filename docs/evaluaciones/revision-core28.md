# Core 28 — Latencia y consumo del flujo RAG

## Condiciones

- Fecha de ejecución: 18 de noviembre de 2026.
- Modelo solicitado: gemini-3.5-flash-lite.
- Corpus: cinco documentos de ejemplo de fotografía.
- Índice persistido: vectorstore/, colección fotografia.
- Se realizaron cinco consultas reales, sin reconstruir el índice.
- Evidencia: registros_latencia_costo.jsonl, en esta misma carpeta.

La instrumentación reutiliza la recuperación, el prompt de sistema
y la validación de citas del asistente.

## Resultados

| Consulta | k solicitado | Fragmentos | Tokens entrada | Tokens salida | Total ms | Generación estimada USD |
|---|---:|---:|---:|---:|---:|---:|
| Sesión familiar | 2 | 2 | 219 | 17 | 8607.93 | 0.00010820 |
| Retrato profesional | 2 | 2 | 215 | 15 | 2677.21 | 0.00010200 |
| Cancelación | 2 | 2 | 249 | 19 | 3421.58 | 0.00012220 |
| Sesión familiar | 3 | 3 | 262 | 19 | 8605.26 | 0.00012610 |
| Sesión familiar | 6 | 5 | 366 | 19 | 3687.80 | 0.00015730 |

## Interpretación

La comparación de k=3 con k=6 usa exactamente la misma pregunta.
Los tokens de entrada aumentaron de 262 a 366 al incorporar más
fragmentos. El costo estimado de generación aumentó también.

Con k=6 se recuperaron cinco fragmentos, porque el índice contiene
solo cinco. Se distingue el número solicitado del número efectivo.

La generación fue la etapa más lenta en las cinco corridas.
El armado del prompt tomó entre 4.34 y 7.11 milisegundos.

La corrida con más fragmentos fue más rápida que la de k=3.
Esto no demuestra que aumentar k reduzca la latencia: solo hay una
observación por configuración y los tiempos de red y del proveedor
varían.

Se mantiene k=2 en el asistente. La evaluación del Bloque 27 encontró
todos los fragmentos esperados en los nueve casos con fuente.
Estas mediciones no justifican aumentar el contexto por defecto.

## Alcance del costo

Se usaron los tokens reportados por LangChain y las tarifas
configuradas en cliente.py: USD 0.30 por millón de tokens de entrada
y USD 2.50 por millón de tokens de salida.

Son tarifas configuradas en el proyecto, no una verificación de
los precios vigentes ni del importe facturado.

La estimación corresponde a la generación. No incluye el costo del
embedding de la pregunta, que se registra como desconocido.
No se presenta esta cifra como el costo total del RAG.

## Límites y trazabilidad

El tiempo total incluye extracción de texto y validación, por lo que
puede superar la suma de las tres etapas cronometradas.

Las pruebas con respuestas simuladas se ejecutaron por separado
y no se guardaron en el JSONL de corridas reales.

Las consultas usan datos de ejemplo. Antes de publicar, se revisan
las respuestas y las fuentes del JSONL. La validación automática
comprueba que las citas existan; la revisión del respaldo factual
se realiza leyendo el fragmento citado.
