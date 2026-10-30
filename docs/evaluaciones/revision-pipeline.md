# Revisión del pipeline de texto — Bloque 15

## Ejecución

- Fecha: 29 de octubre de 2026.
- Modelo solicitado: `gemini-3.5-flash-lite`.
- Casos evaluados: 3 de 3.
- Costo estimado acumulado mostrado: USD $0,000875.
- Registro: [Resultados de la ejecución](pipeline-20261029T092711328679Z.json).

Se evaluó el campo `respuesta` del JSON validado, conservando la
respuesta original en el registro.

## Resultados

| Caso | Coincidencia cruda | Coincidencia procesada |
|---|---:|---:|
| Retrato profesional | 92,3 % | 100,0 % |
| Sesión familiar | 84,6 % | 92,3 % |
| Confirmación de reserva | 94,7 % | 94,7 % |

## Revisión manual

- Retrato profesional: informa correctamente $35.000 CLP y 45 minutos.
- Sesión familiar: informa correctamente $55.000 CLP y 60 minutos.
  Usa una redacción diferente de la referencia, sin alterar esos datos.
- Confirmación de reserva: no afirma consultar disponibilidad ni
  confirmar una reserva. Presenta un defecto de escritura:
  La respuesta omite `se` antes de `requiere`; es un detalle de
  redacción que no cambia el límite informado.

## Interpretación y límites

El procesamiento aumentó la coincidencia en los dos primeros casos
al normalizar diferencias de formato.

La métrica mide presencia de palabras únicas de la referencia.
No evalúa significado, orden, repeticiones ni exactitud factual.

La limpieza no separa palabras pegadas ni convierte automáticamente
en equivalentes expresiones como `cuesta` y `tiene un valor`.

Los porcentajes complementan la revisión manual; no la sustituyen.
Los costos son estimaciones basadas en las tarifas configuradas.