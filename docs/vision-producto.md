# Visión del producto

## Propósito

Construir un asistente inteligente de atención y agendamiento para
profesionales independientes, que facilite responder consultas y
gestionar solicitudes de hora con información confiable y supervisión
del profesional.

El caso inicial utiliza un catálogo de servicios de fotografía.
La solución se inspira en plataformas como Encuadrado, pero no busca
replicar todas sus funcionalidades durante el curso.

## Experiencia objetivo

1. El cliente consulta servicios, precios, duración y condiciones.
2. El asistente responde utilizando información del profesional.
3. Cuando corresponda, consulta documentos y cita sus fuentes.
4. Ante una solicitud de hora, identifica la información necesaria.
5. Utiliza herramientas para consultar disponibilidad y gestionar
   solicitudes, según las integraciones y reglas que se implementen.
6. El profesional conserva la supervisión de las reservas y sus reglas
   de confirmación.

Esta experiencia representa la visión objetivo. No implica que todas
estas capacidades ya estén implementadas.

## Estado actual

El proyecto funciona desde terminal e incluye:

- Cliente de Gemini con manejo de errores, reintentos y costos estimados.
- Consultas al catálogo y validación de respuestas JSON.
- Agente con herramientas del catálogo y memoria durante la sesión.
- RAG sobre cinco documentos de demostración.
- Índice Chroma persistente con verificación y actualización incremental.
- Respuestas documentales con citas y abstención cuando falta información.
- Revisión de preguntas y filtrado de documentos sospechosos.
- Evaluación de recuperación mediante precisión, recall y F1.
- Logs JSON correlacionados mediante trace_id.
- Medición de tiempos, tokens y costo estimado de generación.
- Versionado de prompts y aprobación humana mediante LangGraph.
- Pruebas automatizadas y un ensayo desde un clon limpio.

Estas capacidades tienen diferentes entradas de ejecución, documentadas
en el README. Todavía no forman una única interfaz de producto.

El agente con memoria consulta el catálogo JSON. Su integración con
el RAG documental sigue pendiente como mejora opcional.

Actualmente no consulta disponibilidad real ni registra, envía,
modifica, cancela o confirma reservas.

## Evolución prevista

### Gate 1 — Base técnica entregada

Miniaplicación Python con consumo de API, instrucciones de sistema,
catálogo, procesamiento de respuestas y manejo de errores.

### Gate 2 — Componentes implementados, entrega en preparación

RAG persistente, recuperación evaluada, respuestas con fuentes,
seguridad, decisión de personalización, observabilidad y mediciones.

También se implementó supervisión del prompt mediante LangGraph.
El agente con memoria existe por separado; integrarlo con el RAG
es una mejora opcional pendiente.

El cierre de la entrega incluye actualizar la documentación
y comprobar que las evidencias correspondan a la versión entregada.

### Gate 3 — Integración del producto

Progresión prevista hacia API, persistencia, interfaz y despliegue.

Las tecnologías y funcionalidades concretas se confirmarán con los
requisitos del curso y las decisiones del proyecto.

## Decisiones pendientes

- Tipo y alcance de la interfaz.
- Fuente de disponibilidad: agenda propia o calendario externo.
- Datos necesarios para gestionar una solicitud.
- Reglas de confirmación, modificación y cancelación.
- Acciones que requieren aprobación del profesional.
- Ampliación del corpus de demostración a otros profesionales y servicios.
- Almacenamiento, acceso y conservación de datos personales.
- Entorno de despliegue y presupuesto de operación.

## Criterios de éxito del producto

- Entregar información coherente con el catálogo y los documentos.
- Distinguir orientación, solicitud y reserva confirmada.
- No afirmar que realizó acciones que no puede ejecutar.
- Respetar las reglas y autorizaciones del profesional.
- Manejar fallos con mensajes comprensibles y reintentos acotados.
- Permitir verificar el funcionamiento mediante pruebas.
- Documentar instalación, límites y consumo estimado.

Estos criterios orientan el producto y no sustituyen las rúbricas
oficiales del curso.

## Regla para priorizar avances

Cada cambio debe cumplir un requisito del curso o aportar a la
experiencia objetivo.

Los ejercicios aislados sirven para verificar componentes y no se
convierten automáticamente en funcionalidades del producto.

Ante una diferencia entre esta visión, la ficha de alineación y una
rúbrica, revisar y documentar la decisión antes de ampliar el alcance.