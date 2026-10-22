# Decisión de arquitectura: elección de modelo

Fecha de evaluación: 22 de octubre de 2026.

Proyecto: Asistente inteligente de atención y agendamiento para
profesionales independientes.

## 1. Modelo elegido

Se elige `gemini-3.5-flash-lite`.

La aplicación orienta consultas sobre servicios, precios y condiciones
de un profesional independiente. Actualmente utiliza un catálogo de
ejemplo de servicios de fotografía.

Los requisitos principales son:

- Responder en español de forma breve y clara.
- Usar correctamente el catálogo.
- Preguntar cuando falta información.
- No inventar disponibilidad ni confirmar reservas.
- No afirmar que registra o envía solicitudes.
- Producir una respuesta JSON que la aplicación pueda validar.

## 2. Diagrama de arquitectura

Consultar el [diagrama y sus componentes](arquitectura.md).

## 3. Comparación de candidatos

### Condiciones

Se realizaron cuatro intentos por modelo, alternando los candidatos.
Ambos recibieron la misma consulta, catálogo e instrucciones.

Consulta:

> Quiero una sesión familiar. ¿Cuánto cuesta y cuánto dura?
> ¿Puedes confirmar una reserva para mañana a las 10?

Esta comparación utilizó `preparar_consulta`, que combina instrucciones,
catálogo y consulta en un texto. No utilizó el prompt de sistema
separado ni la salida JSON de la versión actual del asistente.

La validación de la versión actual se realizó por separado con
el banco de prompts.

Se utilizaron los parámetros de generación predeterminados de
cada modelo.

Registro:
[Resultados de comparación](evaluaciones/comparacion-20261022T130450723449Z.json).

### Tarifas

Tarifas estándar para texto en USD por millón de tokens:

| Criterio | gemini-3.6-flash | gemini-3.5-flash-lite |
|---|---:|---:|
| Entrada | 0,75 | 0,30 |
| Salida, incluido razonamiento | 3,75 | 2,50 |

Fuente: https://ai.google.dev/gemini-api/docs/pricing

Fecha de consulta: 22 de octubre de 2026.

Las tarifas de 3.6 indicadas son promocionales hasta el
31 de diciembre de 2026.

Los costos calculados son estimaciones equivalentes a tarifa pagada.
No necesariamente representan el importe facturado si se utiliza
cuota gratuita. No se utilizó caché explícita ni herramientas externas.

### Resultados

| Criterio | gemini-3.6-flash | gemini-3.5-flash-lite |
|---|---|---|
| Intentos | 4 | 4 |
| Respuestas exitosas | 2 | 3 |
| Errores HTTP 503 | 2 | 1 |
| Latencias exitosas, segundos | 8,60; 6,03 | 20,89; 21,39; 20,62 |
| Latencia promedio exitosa | 7,32 s | 20,97 s |
| Costo promedio estimado por respuesta exitosa | Aproximadamente USD 0,003744 | Aproximadamente USD 0,000290 |
| Precio y duración del servicio | Correctos en ambas respuestas | Correctos en las tres respuestas |
| Confirma una reserva | No | No |

Los promedios de latencia excluyen los intentos fallidos.
Los promedios de costo de esta tabla se calcularon a partir de
los importes redondeados impresos en consola; el registro JSON
conserva mayor precisión.

No se asigna costo cero a los intentos fallidos: su costo no pudo
determinarse.

### Calidad y limitaciones observadas

Ambos modelos indicaron correctamente que la Sesión familiar cuesta
$55.000 CLP y dura 60 minutos. Ninguno confirmó la reserva.

Con las instrucciones antiguas:

- 3.6 ofreció enviar la solicitud o insinuó que quedaría pendiente
  para contacto posterior, acciones que la aplicación no realiza.
- Lite pidió nuevamente fecha y hora aunque ya estaban en la consulta.

Estas observaciones muestran limitaciones de las respuestas bajo
esas instrucciones. No permiten afirmar que un modelo esté libre
de errores.

### Prueba del prompt actual

Se probó `gemini-3.5-flash-lite` con tres prompts y tres intentos
por prompt, usando instrucciones de sistema separadas y salida JSON.

Se obtuvieron siete respuestas válidas y dos errores HTTP 503.
Las siete respuestas recibidas superaron la validación automática
y la revisión manual de sus criterios.

Consultar la
[revisión del banco de prompts](../prompts/revision-resultados.md)
y su
[registro real](../prompts/registro-20261022T125255578570Z.json).

No se observaron ofertas de registrar o enviar solicitudes en
esas siete respuestas.

## 4. Justificación

Se elige `gemini-3.5-flash-lite` porque ofrece calidad suficiente
para las consultas acotadas del catálogo, tuvo menor costo
estimado por respuesta y produjo tres respuestas exitosas frente
a dos de 3.6 en la corrida comparativa.

El criterio de mayor peso es el costo, manteniendo el cumplimiento
de los requisitos del asistente.

Se acepta una mayor latencia observada: aproximadamente
20,97 segundos frente a 7,32 segundos de 3.6.

La elección también cuenta con evidencia del banco de prompts
de la versión actual.

La muestra es pequeña y hubo alta demanda del proveedor.
Los resultados no demuestran que Lite sea siempre más disponible
ni que estas latencias se mantengan en otras condiciones.

## 5. Alternativas descartadas y motivos

### gemini-3.6-flash

No se elige como modelo principal porque su mayor costo observado
no se justifica para las consultas simples evaluadas.

Fue más rápido cuando respondió, por lo que podría reconsiderarse
si la latencia adquiere mayor prioridad.

### gemini-3.8-flash

En la corrida del 21 de octubre, los cuatro intentos devolvieron
HTTP 503. No se obtuvieron respuestas para evaluar su calidad.

Se descartó de esta selección por indisponibilidad durante
las pruebas, sin concluir que su calidad sea inferior.

### gemini-2.5-flash

Una prueba de diagnóstico devolvió HTTP 404 e informó que
el modelo no está disponible para usuarios nuevos.

Se descartó por falta de acceso desde la cuenta utilizada.