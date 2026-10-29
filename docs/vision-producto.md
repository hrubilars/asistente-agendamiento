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

El asistente funciona desde una terminal y permite:

- Consultar un catálogo de ejemplo.
- Orientar consultas mediante Gemini.
- Separar instrucciones de sistema y mensajes del usuario.
- Solicitar y validar respuestas JSON.
- Manejar errores y reintentar fallos temporales.
- Estimar costos por operación y acumularlos durante la sesión.
- Ejecutar pruebas automatizadas del cliente y del validador.

Actualmente no consulta disponibilidad real ni registra, envía
o confirma reservas.

## Evolución prevista

### Gate 1 — Base técnica entregada

Miniaplicación Python con consumo de API, instrucciones de sistema,
catálogo, procesamiento de respuestas y manejo de errores.

### Gate 2 — Componentes de IA e integración

Progresión prevista hacia recuperación de documentos con RAG,
herramientas y flujos de atención y agendamiento.

El alcance obligatorio se determinará con la rúbrica vigente y la
ficha de alineación técnica.

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
- Documentos que formarán el corpus de consulta.
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