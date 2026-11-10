# Límites de autonomía del agente de fotografía

## Herramientas y nivel de riesgo

El agente de `agente_con_herramientas.py` puede elegir entre dos herramientas.
Ambas leen el catálogo local. El historial conserva el contexto de cada
sesión en memoria; no concede permisos adicionales al agente.

| Herramienta | Nivel y tipo | Justificación |
|---|---|---|
| `consultar_servicio` | Bajo · solo lectura | Consulta el precio y, si se solicita, la duración de un servicio. Una elección equivocada puede informar el precio de otro servicio, pero no modifica el catálogo ni crea una reserva. |
| `consultar_politica` | Bajo · solo lectura | Consulta las condiciones de pago, cancelación o agendamiento. Una respuesta equivocada puede confundir al cliente, pero la herramienta no cobra, cancela ni modifica una reserva. |

## Aprobación humana

Ninguna herramienta actual requiere aprobación humana para ejecutarse:
las dos consultan información existente y no realizan gestiones externas.

Si alguien pide crear, cambiar o cancelar una reserva, el agente debe
explicar que la gestión corresponde al profesional. La aplicación no consulta
disponibilidad real ni tiene una herramienta que ejecute esas acciones.

Si en una versión futura se incorpora una herramienta que modifica una
reserva, se evaluará su riesgo antes de habilitarla. Una cancelación con
penalización o un cobro deberán quedar detenidos hasta que el profesional
apruebe la acción concreta. Ese control aún no está implementado.

## Revisión de trazas

Revisaré la traza antes de cada entrega y después de cambiar las
herramientas, sus descripciones, el mensaje de sistema o la memoria.
También la revisaré si una respuesta contradice el catálogo o afirma haber
realizado una gestión.

En cada revisión comprobaré:

- **Elección:** una pregunta por el precio usa `consultar_servicio`;
  una pregunta por las condiciones usa `consultar_politica`.
  Un saludo puede resolverse sin herramientas.
- **Argumentos:** el nombre corresponde al servicio consultado e
  `incluir_duracion` es verdadero cuando se pregunta cuánto dura.
- **Resultado:** la respuesta final coincide con el dato devuelto por la
  herramienta. Una política de cancelación no equivale a una cancelación
  ejecutada.
- **Patrones anómalos:** llamadas repetidas sin aportar información,
  consultas a la herramienta equivocada, afirmaciones sin respaldo o
  referencias a información de otra sesión.

La versión actual muestra las llamadas en consola mediante
`intermediate_steps`. La evidencia que se comparta se obtendrá con
consultas de prueba, sin nombres, teléfonos, correos ni otros datos
personales.

## Respuesta ante un comportamiento inesperado

1. Identificar la consulta de prueba, la herramienta elegida y su resultado.
   Comparar la respuesta con el catálogo y reproducir el caso.
2. Si eligió la herramienta equivocada, revisar su descripción y el mensaje
   de sistema. Si la herramienta devolvió un dato incorrecto, revisar sus
   argumentos, la función y el catálogo.
3. Si el fallo se repite o el agente afirma haber confirmado, cambiado o
   cancelado una reserva, detener la demostración. Deshabilitar la herramienta
   afectada si se identifica como causa; si el fallo ocurre sin herramientas,
   mantener el agente fuera de uso hasta corregirlo.
4. Repetir el caso que falló y una consulta normal de cada herramienta antes
   de volver a habilitar el flujo. Registrar qué falló, qué se corrigió y
   qué prueba confirmó la corrección.

   ## Evidencia de verificación

El 10 de noviembre de 2026 se verificó una consulta por cada herramienta
disponible. La [evidencia de las dos consultas](evaluaciones/trazas_agente.jsonl)
registra la herramienta elegida, sus argumentos, su resultado y la respuesta final.
Ambos casos cubren el único nivel de riesgo presente en el agente actual:
bajo, de solo lectura.