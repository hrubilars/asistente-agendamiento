# Límites de la métrica de evaluación

## Qué mide

El pipeline compara palabras de una respuesta y una referencia,
después de limpiar y tokenizar ambos textos, contando repeticiones.
Calcula precisión, cobertura y F1 mediante coincidencia léxica.

No verifica por sí solo exactitud factual, significado, utilidad
ni cumplimiento de los límites del asistente.

## Modos de falla conocidos

- Contenido adicional correcto puede reducir el F1.
  En el caso 04, la referencia solo contiene el precio de la sesión
  familiar. La respuesta informa correctamente $55.000 CLP y agrega
  duración y orientación sobre reservas. Obtiene F1 = 0,303030,
  pese a ser factual y completa.
  El caso 01 presenta un patrón similar: enumera ambos servicios
  y agrega información del catálogo, con F1 = 0,325581.

- Una redacción equivalente puede obtener poca coincidencia.
  En el caso 13, la respuesta explica que no consulta disponibilidad
  y que la reserva requiere contacto directo con el profesional.
  Conserva la orientación esperada, pero obtiene F1 = 0,342857.

- El puntaje no identifica qué omisión importa para el usuario.
  En el caso 11 falta preguntar qué servicio desea, por lo que
  la orientación de la solicitud incompleta es parcial.
  Su F1 es 0,263158.
  En el caso 10 se identifica correctamente el retrato de $35.000
  dentro del presupuesto de $40.000, pero se omite la comparación
  explícita con la sesión familiar que incluye la referencia.
  Su F1 es 0,290909. La cobertura de la referencia es parcial,
  aunque la pregunta principal queda resuelta.

No se observaron errores factuales ni contradicciones en los diez
casos revisados. Esto no demuestra que la métrica pueda detectarlos
ni que estén ausentes en todas las respuestas del sistema.

## Muestra revisada

Se seleccionaron diez casos distintos de veinte respuestas reales
generadas mediante consultar_modelo, con el catálogo y las
instrucciones de sistema del asistente de fotografía.

La selección utiliza el F1 sin redondear y desempata por ID:

- Cinco F1 más bajos: 11, 10, 04, 01 y 13.
- Cinco F1 más altos: 07, 03, 05, 12 y 20.

Se valoraron corrección factual, completitud respecto de la referencia
y contradicción, con una justificación por caso.
Héctor Rubilar leyó y aceptó la propuesta de valoración preparada
con apoyo de IA. La fecha de registro consta en el JSON de revisión.

Los casos 05, 12 y 20 obtuvieron F1 = 1 y la lectura confirmó
su correspondencia con las referencias. El caso 20 resistió
ese intento concreto de ignorar instrucciones; no acredita
protección frente a cualquier inyección de prompt.

Evidencias:

- [Respuestas y métricas](evaluaciones/core17-resultados.json).
- [Revisión de diez casos](evaluaciones/core17-revision-manual.json).

Los fallos técnicos se conservan separados y no cuentan como
respuestas evaluadas. El ensayo se completó mediante una
reanudación después de un límite de solicitudes del proveedor.

## Recomendación de uso

Usar F1 como indicador de coincidencia léxica y apoyo para comparar
ejecuciones con referencias y condiciones equivalentes.

Revisar casos de puntuación baja y alta. No rechazar una respuesta
solo por un F1 bajo ni aprobarla solo por un F1 alto.

En este asistente, comprobar manualmente precios, duraciones,
disponibilidad y afirmaciones de registrar, enviar o confirmar
reservas. Revisar también si una solicitud incompleta recibe
la orientación necesaria.

La muestra es pequeña y seleccionada por extremos; no representa
una estimación de la tasa de calidad de todas las consultas.