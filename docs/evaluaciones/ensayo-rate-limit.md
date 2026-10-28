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
se verificaron mediante pruebas automatizadas con mocks. La evidencia
de un 429 real solicitada por la lección sigue pendiente.