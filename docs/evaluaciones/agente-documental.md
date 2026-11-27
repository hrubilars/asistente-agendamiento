# Verificación del agente documental con memoria

Fecha: 26 de noviembre de 2026.
Modelo solicitado: gemini-3.5-flash-lite.
Entrada de ejecución: python agente_documental.py.

## Pruebas automatizadas

Comando:

python -m pytest test_agente_documental.py test_herramienta_documental.py -v

Resultado: 9 pruebas aprobadas.

Se verificaron:
- Conservación de respuesta, fuentes, abstención y trace_id.
- Uso de la herramienta documental desde el ejecutor.
- Conservación de referencias dentro de una sesión.
- Aislamiento entre sesiones.
- Rechazo de entradas inválidas antes de ejecutar el agente.
- Propagación de errores sin inventar respuestas.

Las pruebas utilizan un planificador simulado y no llaman a Gemini.

## Conversación real

Se realizaron tres consultas consecutivas en la misma sesión.

| Consulta | Resultado observado |
|---|---|
| ¿Cuánto cuesta la sesión familiar? | $55.000 CLP, con cita a docs/corpus/sesion-familiar.md. |
| ¿Y cuánto dura esa sesión? | 60 minutos, identificando el servicio mediante el historial y citando su documento. |
| ¿Cuál es la dirección exacta del estudio? | Abstención explícita por información insuficiente, sin citas inventadas. |

Identificadores de las consultas RAG:

- Precio: trace-33ce8a14804b4b77b96875413beb4f7d
- Duración: trace-ddee891ec64e45e2844c92b8384601d6
- Dirección: trace-4b3ec8ff55684c4ab56706e7bbcd4c4d

## Alcance y limitaciones

- La memoria reside en el proceso y se pierde al cerrar el programa.
- El aislamiento entre sesiones se verificó mediante pruebas automatizadas.
- Los tiempos, tokens y costos registrados corresponden al RAG:
  no incluyen las llamadas adicionales del planificador del agente.
- En esta conversación, la abstención requirió generación del modelo.
- La aplicación no consulta disponibilidad ni gestiona reservas.
- Fotografía es el caso de demostración del asistente para profesionales
  independientes.
- Se observaron advertencias de deprecación en dependencias y en las
  clases de memoria utilizadas; no impidieron estas verificaciones.