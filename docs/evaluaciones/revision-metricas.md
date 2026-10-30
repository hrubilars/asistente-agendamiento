# Revisión de métricas — Bloque 16

## Procedencia

- Fecha de cálculo: 30 de octubre de 2026.
- Respuestas originales: 29 de octubre de 2026.
- Modelo solicitado: `gemini-3.5-flash-lite`.
- Casos evaluados: 3.
- No se realizaron nuevas llamadas a la API.

Se reutilizaron las respuestas reales del bloque 15, conservando el
registro original.

- [Registro original](pipeline-20261029T092711328679Z.json)
- [Métricas calculadas](metricas-20261030T130947768222Z.json)

## Resultados

| Caso | Precisión | Cobertura | F1 |
|---|---:|---:|---:|
| Sesión familiar | 0,444 | 0,923 | 0,600 |
| Retrato profesional | 0,867 | 1,000 | 0,929 |
| Confirmación de reserva | 1,000 | 0,947 | 0,973 |
| Promedio por caso | 0,770 | 0,957 | 0,834 |

Los valores mostrados están redondeados. El registro JSON conserva
la precisión numérica del cálculo.

## Interpretación

La respuesta sobre sesión familiar informa correctamente el precio
de $55.000 CLP y la duración de 60 minutos. Su precisión léxica es menor
porque utiliza otra redacción e incluye instrucciones adicionales
sobre cómo concretar la reserva.

La respuesta sobre retrato profesional mantiene todos los tokens
de referencia, pero agrega palabras. Esto explica una cobertura de
1,000 y una precisión inferior a 1,000.

La respuesta sobre confirmación respeta el límite de no consultar
disponibilidad ni confirmar reservas. Su puntuación alta indica
similitud léxica; no sustituye esa revisión manual.

## Alcance de la medición

Las coincidencias se cuentan considerando las repeticiones de palabras.

- Precisión: coincidencias divididas por los tokens de la respuesta.
- Cobertura: coincidencias divididas por los tokens de referencia.
- F1: media armónica de precisión y cobertura.

El promedio es la media de los valores individuales de cada caso.

Estas métricas no verifican hechos, significado ni orden de palabras.
Un precio equivocado o una negación ausente pueden coexistir con una
puntuación alta.

Ordenar por F1 permite priorizar la lectura, pero no demuestra que el
caso con menor puntuación tenga peor calidad.

No se modificaron las instrucciones del asistente para mejorar
artificialmente las puntuaciones.