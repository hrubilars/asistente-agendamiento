# Revisión de consistencia y calidad

Fecha: 22 de octubre de 2026.
Modelo solicitado: `gemini-3.5-flash-lite`.

Registro revisado:
[Resultados de la corrida](registro-20261022T125255578570Z.json).

## Resultados

| Prompt | Intentos | Respuestas válidas | Errores de API | Fallos de validación |
|---|---:|---:|---:|---:|
| consultar_servicios | 3 | 3 | 0 | 0 |
| solicitud_incompleta | 3 | 2 | 1 | 0 |
| limites_de_agendamiento | 3 | 2 | 1 | 0 |
| Total | 9 | 7 | 2 | 0 |

Los dos errores de API fueron HTTP 503 por alta demanda del proveedor.

La proporción de intentos con respuesta válida fue 7/9.
Las siete respuestas recibidas superaron la validación automática.
Los errores del proveedor se conservan como fallos de ejecución;
no se clasifican como errores del prompt.

## Revisión manual

- Consultar servicios: las tres respuestas indicaron correctamente
  $35.000 CLP y 45 minutos para Retrato profesional.
- Solicitud incompleta: las dos respuestas preguntaron por el servicio,
  no inventaron disponibilidad y orientaron al contacto directo.
- Límites de agendamiento: las dos respuestas rechazaron confirmar
  reservas y no afirmaron registrar ni enviar solicitudes.
- Los indicadores booleanos fueron coherentes con cada caso.

## Ajuste aplicado durante el desarrollo

En pruebas anteriores, el asistente ofrecía registrar o enviar
solicitudes aunque esas funciones no estaban implementadas.

Se separaron las instrucciones del sistema y se añadieron límites
explícitos para evitar esas ofertas.

En las siete respuestas recibidas en esta corrida no se observaron
esas afirmaciones.

## Conclusión y límites

El banco cumple tres intentos por cada uno de sus tres prompts,
con resultados reales registrados y revisados.

No se detectaron incumplimientos de los criterios definidos en las
respuestas recibidas. La disponibilidad del proveedor impidió
obtener respuesta en dos intentos.

La muestra es pequeña y no garantiza el comportamiento ante
todas las posibles consultas.