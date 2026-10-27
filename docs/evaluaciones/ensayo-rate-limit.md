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