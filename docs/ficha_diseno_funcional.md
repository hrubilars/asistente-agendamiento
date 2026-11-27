# Ficha de Diseño Funcional

## 1. Problema de negocio

Los profesionales independientes que atienden directamente a sus clientes reciben consultas repetidas sobre servicios, precios, duración y condiciones, y deben coordinar manualmente las solicitudes de hora. Estas tareas interrumpen su actividad principal y pueden generar información inconsistente, intercambios innecesarios y confusión entre una solicitud recibida y una reserva confirmada.

Para un profesional ficticio se estima un volumen de 30 consultas semanales de tres minutos cada una: 90 minutos semanales dedicados solo a responder consultas frecuentes. Es una estimación de trabajo para el ejercicio, no una medición de un negocio real; no incluye el tiempo adicional de coordinación de horas.

Se espera que el cliente obtenga información verificable en menos de un minuto, identifique horarios disponibles y pueda solicitar una hora sin confundirla con una reserva confirmada. El profesional debe conservar la decisión de aceptar o rechazar cada solicitud.

## 2. Requerimientos y alcance (MVP)

### Requerimientos funcionales

- RF-01: El cliente obtiene respuestas sobre servicios, precios, duración y políticas, con identificación de las fuentes que las respaldan.
- RF-02: El cliente consulta los horarios disponibles para un servicio en una fecha indicada.
- RF-03: El cliente registra una solicitud de hora con servicio, horario y contacto, identificada como pendiente de aprobación y con un número de seguimiento.
- RF-04: El profesional aprueba o rechaza una solicitud pendiente; la aprobación produce una reserva confirmada y el rechazo deja constancia de que no fue confirmada.
- RF-05: El cliente realiza preguntas de seguimiento conservando el servicio mencionado durante su conversación, sin mezclar el historial entre sesiones.
- RF-06: El cliente solicita cambiar el horario de una reserva, sujeto a aprobación del profesional.
- RF-07: El cliente solicita cancelar una reserva de acuerdo con las políticas del profesional.
- RF-08: El servicio sincroniza las reservas con calendarios externos reales.
- RF-09: El cliente paga los servicios desde la plataforma.
- RF-10: El cliente y el profesional utilizan una interfaz web completa con cuentas, historial y panel de administración.

### Requerimientos no funcionales

Los siguientes requisitos expresan objetivos verificables del producto final. Los resultados actuales de Gate 2 son antecedentes, pero no acreditan por sí solos estos objetivos de Gate 3.

- RNF-01: En al menos 9 de 10 consultas informativas del conjunto de prueba, el cliente recibe una respuesta válida en menos de 60 segundos; se cronometra desde el envío de la consulta hasta la recepción de la respuesta, con el servicio ya iniciado.
- RNF-02: En al menos 8 de las 9 preguntas con fuente esperada del banco documental, la respuesta coincide con la información de los documentos y cita una fuente que respalda la afirmación; se comprueba mediante revisión manual registrada. En la pregunta del banco cuya información no existe, se declara explícitamente que no hay información suficiente.
- RNF-03: En los registros operativos de 10 consultas y 5 solicitudes de prueba aparecen cero claves de acceso, cero datos de contacto completos y cero textos completos de preguntas o documentos; se comprueba mediante revisión de los registros.
- RNF-04: Una persona distinta del autor inicia el servicio siguiendo el README en un equipo de prueba con Docker instalado, conexión disponible y credenciales configuradas en menos de 15 minutos, medidos desde el inicio de la construcción de la imagen hasta la comprobación de salud del servicio.
- RNF-05: En 10 escenarios de solicitudes de prueba, incluidos intentos repetidos y dos solicitudes para el mismo horario, se producen cero reservas confirmadas incompatibles para ese horario y cero reservas confirmadas sin aprobación explícita del profesional; se comprueba revisando las respuestas y el estado almacenado. Los horarios de la demostración no se superponen y admiten una sola reserva.
- RNF-06: El 100 % de las 10 consultas y las 5 solicitudes de prueba tiene un identificador que permite relacionar su inicio con su finalización o fallo. Para cada generación se registran los tokens informados por el proveedor y su costo estimado, o se declara expresamente que esa información no está disponible.

### Alcance

Imprescindible: RF-01, RF-02, RF-03, RF-04, RF-05
Deseable: RF-06, RF-07
Fuera de alcance: RF-08 (requiere cuentas e integraciones externas reales), RF-09 (incorpora transacciones y obligaciones adicionales al ejercicio), RF-10 (se posterga la interfaz completa para priorizar el flujo funcional, su exposición y su ejecución reproducible)

#### Límites del MVP académico

- El MVP opera con un perfil profesional configurado por instancia. El nombre, la especialidad, los servicios, las tarifas, las duraciones, los horarios, los documentos y las políticas se mantienen fuera de la lógica general de atención y agendamiento. Cambiar de especialidad debe requerir preparar su configuración y corpus, no reescribir el flujo de negocio.
- La demostración principal utiliza un profesional ficticio. Se realizará además una comprobación de adaptación con un segundo perfil de otra especialidad, por ejemplo un profesor particular o un consultor, para revisar que las respuestas y los servicios correspondan al perfil configurado. No se exige operar varias cuentas de profesionales simultáneamente.
- Los servicios, horarios, clientes y datos de contacto son simulados. No se utilizan datos personales reales ni agendas de negocios reales.
- La agenda de demostración contiene horarios predefinidos, sin superposición, con capacidad para una reserva por horario.
- Consultar disponibilidad, registrar solicitudes y aprobar o rechazar serán operaciones reales sobre datos simulados almacenados. No serán únicamente afirmaciones generadas por el modelo.
- Una solicitud pendiente no constituye una reserva ni bloquea definitivamente el horario. Al aprobar, el sistema comprueba nuevamente su disponibilidad; solo una solicitud puede convertirse en reserva para ese horario.
- Las solicitudes y las decisiones se conservan tras reiniciar el servicio. El historial de conversación puede limitarse a la sesión activa y debe mantenerse separado entre sesiones.
- Cuando falta información documental, se declara esa limitación. No se inventan servicios, precios, horarios ni acciones realizadas.
- El rol de profesional se representa mediante un mecanismo de acceso de demostración, separado del acceso del cliente y con su secreto fuera del repositorio. No se implementa una plataforma completa de usuarios y recuperación de contraseñas.
- La aprobación de una reserva y la aprobación de un cambio de prompt son decisiones diferentes. El control de prompts existente no sustituye la aprobación de solicitudes de hora.
- El flujo se prueba mediante la documentación interactiva de la API y un cliente HTTP. Una interfaz comercial completa queda para una evolución posterior.
- El empaquetado, los endpoints y las pruebas son parte de la entrega académica, aunque no sean funciones de negocio que el cliente describiría como tales.

## 3. Arquitectura de la solución

Esta sección describe el diseño objetivo de Gate 3. Reutiliza componentes de Gate 2 y añade la gestión de solicitudes y la exposición del servicio.

- Modelo: Gemini mediante API, inicialmente con el modelo configurado `gemini-3.5-flash-lite`; orienta las consultas y utiliza herramientas, sin decidir por sí mismo que una reserva quedó confirmada.
- Vector store: Chroma conserva el índice documental en `vectorstore/`, con persistencia y actualización incremental.
- Orquestación: LangChain coordina la conversación, el RAG y las herramientas de agenda y solicitudes; LangGraph conserva el flujo existente de supervisión de cambios del prompt.
- Exposición: FastAPI ofrece las operaciones de consulta, disponibilidad, solicitud y decisión del profesional, además de una comprobación de salud; valida entradas y devuelve resultados estructurados.
- Empaquetado: Docker ejecuta el servicio con configuración externa y volúmenes para conservar el índice y los datos de solicitudes después de reiniciarlo.

### Persistencia y reglas de agendamiento

Como decisión de diseño propuesta, SQLite almacenará los horarios simulados, las solicitudes y las decisiones del profesional. La aprobación comprobará disponibilidad y guardará la reserva en una operación atómica para impedir confirmaciones incompatibles.

Las herramientas ejecutarán las reglas de negocio y devolverán el resultado efectivo al asistente. El texto generado no sustituirá el estado almacenado.

### Seguridad y trazabilidad

Se reutilizarán el filtro de preguntas y documentos, la validación de citas, el versionado de prompts y el registro estructurado con `trace_id`. Las claves y los secretos de demostración se proporcionarán mediante configuración externa, excluida de Git y de la imagen.

### Diagrama

Diagrama objetivo: `docs/diagrama_arquitectura_gate3.png`.

Estado: pendiente de crear. Debe mostrar FastAPI, LangChain, LangGraph, Gemini, Chroma y SQLite; la frontera Docker, los volúmenes persistentes y la configuración externa. Los nombres deben coincidir con esta sección. El diagrama de Gate 1 no representa el diseño final.

### Qué existe y qué falta construir

| Estado | Componentes |
|---|---|
| Implementados como base | RAG persistente, recuperación, respuestas con citas, seguridad de entrada y contexto, logs y consumo, versiones de prompt y supervisión con LangGraph. |
| Implementados y verificados | Agente con herramientas del catálogo y agente documental que integra memoria por sesión con RAG, fuentes citadas, abstención y trazabilidad de las consultas documentales. |
| Pendientes de generalización | Retirar referencias exclusivas a fotografía de prompts y herramientas, parametrizar el perfil profesional y comprobar un segundo escenario de otra especialidad. |
| Pendientes de construcción | Agenda simulada, registro persistente de solicitudes, decisión del profesional, protección del acceso de demostración, FastAPI y Docker. |
| Pendientes de validación final | Pruebas del flujo completo, verificación de los RNF, instalación reproducible y diagrama del diseño final. |

## 4. Criterios de aceptación

Estos criterios definen la aceptación del producto final de Gate 3.
Su cumplimiento se registrará durante las pruebas; incluirlos en esta
ficha no significa que ya estén implementados.

Los casos de agenda utilizarán un perfil ficticio de profesor particular:
servicio "Clase individual", duración de 60 minutos y un horario de
prueba el 10 de diciembre de 2026 a las 10:00, inicialmente disponible.
Los contactos serán ficticios.

- CA-01 (RF-01): Con el perfil de fotografía de prueba activo, ante "¿Cuánto cuesta el retrato profesional?", la respuesta indica $35.000 CLP y cita docs/corpus/retrato-profesional.md como fuente.
- CA-02 (RF-01): Ante una consulta por una dirección ausente del corpus, la respuesta declara información insuficiente y devuelve la lista de fuentes citadas vacía.
- CA-03 (RF-02): Al consultar los horarios de "Clase individual" para el 10 de diciembre de 2026, el resultado incluye las 10:00 si ese horario está disponible; después de confirmar una reserva para ese horario, la misma consulta deja de ofrecerlo.
- CA-04 (RF-03): Al solicitar "Clase individual" para el horario disponible con un contacto ficticio válido, el sistema devuelve un identificador y estado pendiente; la solicitud sigue disponible mediante ese identificador después de reiniciar el servicio.
- CA-05 (RF-03): Una solicitud sin el servicio, horario o contacto obligatorio es rechazada con identificación del dato faltante y no crea una solicitud almacenada.
- CA-06 (RF-04): Una aprobación autorizada de una solicitud pendiente cambia su estado a confirmada y conserva la decisión después de reiniciar; un rechazo autorizado cambia otra solicitud pendiente a rechazada sin crear una reserva.
- CA-07 (RF-04): Un intento de aprobar una solicitud sin la credencial de demostración del profesional es rechazado y no modifica su estado.
- CA-08 (RF-05): En una misma sesión, después de consultar un servicio, la pregunta "¿Y cuánto dura ese servicio?" devuelve su duración con fuente; en una sesión nueva sin referente, solicita identificar el servicio.
- CA-09 (RNF-01): En diez consultas informativas de prueba, al menos nueve entregan una respuesta válida en menos de 60 segundos desde el envío hasta su recepción, con el servicio ya iniciado; se conserva el tiempo de cada consulta.
- CA-10 (RNF-02): En el banco documental de diez preguntas, al menos ocho de las nueve preguntas con fuente esperada obtienen una respuesta factual correcta y una fuente que respalda la afirmación; la pregunta sin información obtiene una abstención. Cada valoración queda registrada en una revisión manual.
- CA-11 (RNF-03): Al revisar los registros operativos de diez consultas y cinco solicitudes ficticias, se encuentran cero claves de acceso, cero contactos completos y cero textos completos de preguntas o documentos.
- CA-12 (RNF-04): Una persona distinta del autor, siguiendo el README en un equipo con Docker y los prerrequisitos indicados, construye e inicia el servicio y obtiene una comprobación de salud exitosa en menos de 15 minutos; se registra el tiempo observado.
- CA-13 (RNF-05): En diez escenarios de solicitudes, incluidos una aprobación repetida y dos aprobaciones concurrentes para el mismo horario, se observa como máximo una reserva confirmada por horario y ninguna confirmación sin aprobación autorizada del profesional.
- CA-14 (RNF-06): Las diez consultas y cinco solicitudes de prueba tienen un identificador que relaciona su inicio y finalización o fallo; cada generación del modelo registra los tokens y el costo estimado, o declara expresamente su indisponibilidad.

RF-06 y RF-07 son deseables y no forman parte de estos criterios
obligatorios. Su incorporación requiere revisar previamente el
presupuesto de horas.

## 5. Plan de construcción por hitos

## 5. Plan de construcción por hitos

Fecha de entrega: viernes 18 de diciembre de 2026.

Disponibilidad declarada: 5 horas semanales.
Presupuesto conservador: 15 horas durante tres semanas de trabajo.

Se reservan 3 horas para imprevistos. Los hitos planificados suman
12 horas: 7,5 de construcción e integración y 4,5 de pruebas,
documentación y preparación de defensa.

Las duraciones son estimaciones iniciales, pendientes de contrastar
con el tiempo real. No representan trabajo ya completado.

### Hitos

- H1 1h: Perfil profesional configurable y conversación documental adaptada. Entrega: configuración y corpus de un segundo profesional ficticio, con respuestas correspondientes al perfil activo y seguimiento del servicio dentro de la sesión. Reutiliza el RAG y la memoria existentes. Cubre RF-01, RF-05 y CA-01, CA-02, CA-08.
- H2 2.5h: Agenda y solicitudes persistentes sobre datos simulados. Entrega: horarios consultables, creación de solicitudes pendientes con identificador, validación de campos y recuperación de solicitudes después de reiniciar. Depende de H1. Cubre RF-02, RF-03 y CA-03, CA-04, CA-05.
- H3 2h: Decisión autorizada del profesional. Entrega: aprobación y rechazo persistentes, comprobación atómica de disponibilidad y protección frente a aprobaciones repetidas o concurrentes. Depende de H2. Cubre RF-04, RNF-05 y CA-06, CA-07, CA-13.
- H4 2h: Servicio FastAPI y ejecución con Docker. Entrega: endpoints validados de consulta, disponibilidad, solicitud, decisión y salud; configuración externa, persistencia mediante volúmenes y trazabilidad del flujo, incluidas las generaciones del planificador. Depende de H1, H2 y H3. Cubre RF-01 a RF-05, RNF-03, RNF-04, RNF-06 y prepara CA-11, CA-12, CA-14.
- H5 4.5h: Validación integral y preparación de entrega. Entrega: ejecución registrada de CA-01 a CA-14, revisión manual del banco documental, medición de latencia, revisión de registros, ensayo de instalación con otra persona, diagrama final, README y guion de defensa con ensayo en vivo. Depende de H1 a H4. Cubre RF-01 a RF-05, RNF-01 a RNF-06 y CA-01 a CA-14.

### Dependencias y control del presupuesto

Los hitos se ejecutan en orden. Cada uno debe producir una entrega
comprobable antes de comenzar el siguiente.

Al terminar cada hito se registran las horas consumidas, el resultado
y el trabajo restante. Si la proyección supera las 12 horas
planificadas, se revisan las estimaciones y el alcance antes de seguir.

Las 3 horas de margen no se asignan anticipadamente a nuevas funciones.

RF-06 y RF-07 permanecen deseables y sin horas asignadas.
RF-08, RF-09 y RF-10 permanecen fuera del MVP.

La entrega del Gate 2 y las actividades administrativas pendientes
se gestionan por separado; si consumen parte de estas 15 horas,
se recalculará el presupuesto disponible para Gate 3.
