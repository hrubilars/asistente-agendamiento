# Ensayo de límite de uso y registro de costos

## Datos del ensayo

- Fecha: 27 de octubre de 2026.
- Modelo solicitado: `gemini-3.5-flash-lite`.
- Consultas realizadas: 10.
- Consultas exitosas: 10.
- Consultas fallidas: 0.
- Costo estimado acumulado: USD $0,000265.

## Resultado observado

Las diez consultas recibieron una respuesta. La aplicación mostró el
costo estimado de cada operación y el acumulado de la sesión.

Durante este ensayo no apareció un error HTTP 429 ni se mostraron
mensajes de reintento. Por lo tanto, esta ejecución no permite afirmar
que el backoff se haya comprobado frente a un límite de uso real.

El costo indicado es una estimación basada en las tarifas configuradas
en el proyecto; no necesariamente corresponde a un cobro efectivo.

## Pruebas simuladas complementarias

Se verificó el mecanismo de reintentos sin llamadas a la API:

- Una operación se recuperó después de dos fallos temporales.
- Se comprobaron esperas simuladas de 2 y 4 segundos, con el jitter
  fijado en cero para que el resultado fuera reproducible.
- Un error de credenciales no provocó reintentos.
- Al agotarse los intentos, se propagó el error sin una espera adicional.

Estas pruebas simuladas complementan el ensayo real, pero no lo
sustituyen como evidencia de un error 429 real.

## Segundo ensayo — 28 de octubre de 2026

Se realizaron consultas cortas con el cliente modular y un envoltorio
que contabilizó las solicitudes HTTP y los errores 429 sin sustituir
la comunicación real con Gemini.

- Modelo solicitado: `gemini-3.5-flash-lite`.
- Consultas iniciadas: 10.
- Consultas exitosas: 10.
- Consultas fallidas: 0.
- Solicitudes HTTP, incluidos reintentos: 10.
- Errores HTTP 429 observados: 0.
- Costo estimado registrado: USD $0,000064.

No se activaron reintentos. Este ensayo confirma el funcionamiento
de las consultas y del registro de costos, pero no demuestra una
recuperación frente a un límite de uso real.

La clasificación de un HTTP 429 y el comportamiento de los reintentos
se verificaron inicialmente mediante pruebas automatizadas con mocks.
Posteriormente se observó un HTTP 429 real durante el ensayo del core 17,
como se documenta a continuación.

## HTTP 429 real durante el core 17 — 31 de octubre de 2026

Durante la generación de veinte respuestas con el modelo
`gemini-3.5-flash-lite`, se completaron y guardaron dieciséis casos.
Al consultar el caso 17, el proveedor respondió HTTP 429
con estado RESOURCE_EXHAUSTED.

El detalle del error informó un límite de quince solicitudes
por minuto para el proyecto y modelo en el nivel gratuito.
Este límite corresponde a lo informado en esa ejecución;
no se considera una cuota universal ni permanente.

### Reintentos observados

- Después del primer fallo, el cliente esperó 2,17 segundos.
- Después del segundo fallo, esperó 4,32 segundos.
- Al agotarse los tres intentos, informó un error controlado.
- El evaluador conservó las dieciséis respuestas y registró el fallo.

El proveedor sugería inicialmente una espera aproximada de
24 segundos. Las esperas aplicadas por nuestro backoff fueron
insuficientes para superar el límite en esa consulta.

El cliente conserva Retry-After cuando existe, pero todavía no
ajusta automáticamente la espera a ese encabezado ni al campo
retryDelay del cuerpo de la respuesta.

### Reanudación

En una ejecución posterior, el evaluador omitió los casos 01–16,
consultó los casos 17–20 y completó veinte respuestas con JSON
validado, conservando el registro del fallo anterior.

Esto demuestra persistencia del avance y reanudación manual
exitosa. No demuestra recuperación automática exitosa dentro
de los tres intentos de la consulta fallida.

El costo acumulado de sesión se reinicia al ejecutar nuevamente
el programa; el acumulado de la segunda ejecución no representa
por sí solo el costo total de ambas ejecuciones.

### Evidencia y alcance

- [Registro del core 17](core17-resultados.json):
  contiene veinte resultados y un fallo del caso 17.
- Los códigos HTTP, las esperas y el detalle de cuota se observaron
  en la salida de terminal compartida durante el trabajo.
- El JSON conserva el mensaje final resumido del fallo, no el detalle
  completo del HTTP 429 ni los mensajes de cada reintento.

No se realizaron nuevas llamadas a la API para escribir este informe.