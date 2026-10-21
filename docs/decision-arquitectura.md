# Decisión de arquitectura: elección de modelo

Fecha de evaluación: 21 de octubre de 2026.

Proyecto: Asistente inteligente de atención y agendamiento para
profesionales independientes.

## 1. Modelo elegido

Se mantiene provisionalmente `gemini-3.6-flash`.

La aplicación orienta consultas sobre servicios, precios y condiciones
de un profesional independiente. Actualmente utiliza un catálogo de
ejemplo de servicios de fotografía.

Los requisitos principales son:

- Responder en español de forma clara y breve.
- Usar los servicios, precios y condiciones del catálogo.
- Solicitar aclaraciones cuando falte información.
- No inventar disponibilidad ni confirmar reservas.
- No afirmar que registra o envía solicitudes, porque esas funciones
  todavía no están implementadas.

## 2. Diagrama de arquitectura

El flujo y sus componentes están documentados en
[Arquitectura del asistente](arquitectura.md).

## 3. Comparación de candidatos

### Condiciones de prueba

Se realizaron cuatro intentos por modelo, alternando los candidatos.

Ambos recibieron la misma consulta, las mismas instrucciones y el mismo
catálogo. No se configuraron parámetros de generación adicionales:
se utilizaron los valores predeterminados de cada modelo.

Consulta:

> Quiero una sesión familiar. ¿Cuánto cuesta y cuánto dura?
> ¿Puedes confirmar una reserva para mañana a las 10?

La latencia mide la duración de la petición al servicio.
El promedio incluye únicamente las peticiones que devolvieron texto.

Un éxito técnico significa que se obtuvo una respuesta con texto;
no implica automáticamente que esa respuesta cumpla todos los
requisitos de calidad.

### Tarifas de referencia

Tarifas estándar para texto, en USD por millón de tokens:

| Criterio | gemini-3.6-flash | gemini-3.8-flash |
|---|---:|---:|
| Entrada | 0,75 | 0,75 |
| Salida, incluido razonamiento | 3,75 | 3,75 |

Fuente: https://ai.google.dev/gemini-api/docs/pricing

Fecha de consulta: 21 de octubre de 2026.

Las tarifas indicadas son promocionales hasta el 31 de diciembre
de 2026. El costo calculado es una estimación equivalente a tarifa
pagada, no una comprobación del importe efectivamente facturado.

### Resultados de la corrida comparativa

Registro:
[evidencia de la comparación](evaluaciones/comparacion-20261021T150733182382Z.json).

| Criterio | gemini-3.6-flash | gemini-3.8-flash |
|---|---|---|
| Intentos | 4 | 4 |
| Respuestas con texto | 3 | 0 |
| Fallos observados | 1 error HTTP 503 | 4 errores HTTP 503 |
| Latencias exitosas | 22,55; 10,26; 24,01 segundos | Sin datos |
| Latencia promedio exitosa | 18,94 segundos | No calculable |
| Costo promedio estimado por respuesta exitosa | Aproximadamente USD 0,003304 | No calculable |
| Precio y duración correctos | Sí, en las tres respuestas recibidas | No evaluable |
| Evita confirmar reservas | Sí, en las tres respuestas recibidas | No evaluable |
| Respeta el límite de no registrar ni enviar solicitudes | Presenta desviaciones que requieren ajustar las instrucciones | No evaluable |

El promedio de costo mostrado se calculó a partir de los importes
redondeados impresos en consola. El registro JSON conserva mayor
precisión.

Los errores HTTP 503 informaron alta demanda temporal del servicio.
Los intentos fallidos no se contabilizan como respuestas rápidas ni
como respuestas gratuitas: su costo no pudo determinarse.

### Observaciones de calidad

Las tres respuestas de `gemini-3.6-flash` indicaron correctamente:

- Sesión familiar: $55.000 CLP.
- Duración: 60 minutos.
- La reserva requiere confirmación del profesional.

Sin embargo, algunas respuestas ofrecieron enviar o registrar la
solicitud. La aplicación todavía no realiza esas acciones.

Se debe ajustar el prompt para evitar esa afirmación y comprobar
el cambio con nuevas pruebas.

## 4. Justificación

Se mantiene provisionalmente `gemini-3.6-flash` porque ya está integrado
y produjo respuestas útiles para el caso de uso en tres de los cuatro
intentos de esta corrida.

La precisión sobre el catálogo y la claridad sobre la confirmación
de reservas son criterios prioritarios para esta aplicación.

La decisión tiene limitaciones:

- La muestra es pequeña.
- Se probó una sola consulta.
- Hubo fallos del proveedor.
- No se pudo evaluar la calidad ni el costo por respuesta de 3.8.
- Se detectaron afirmaciones sobre acciones que el programa no realiza.

Por ello, esta prueba no demuestra superioridad general de 3.6.
La elección se revisará cuando el segundo candidato pueda responder
y se amplíen las pruebas del asistente.

## 5. Alternativas no elegidas y motivos

### gemini-3.8-flash

No se adopta por ahora porque los cuatro intentos devolvieron HTTP 503
por alta demanda y no permitieron verificar su funcionamiento para
esta aplicación.

Es un descarte provisional por disponibilidad observada en la prueba,
no por mala calidad demostrada.

### gemini-2.5-flash

Fue el segundo candidato inicial. Una prueba de diagnóstico devolvió
HTTP 404 e informó que el modelo ya no está disponible para usuarios
nuevos.

Registro:
[diagnóstico de disponibilidad](evaluaciones/comparacion-20261021T150329112265Z.json).

Se descartó por falta de acceso desde esta cuenta. Su presencia en el
listado de modelos no garantizó que pudiera utilizarse para generar
contenido.

## Pendiente para cerrar la comparación

- Obtener respuestas de un segundo modelo disponible.
- Comparar la calidad de las respuestas bajo las mismas condiciones.
- Actualizar la decisión con los nuevos resultados.