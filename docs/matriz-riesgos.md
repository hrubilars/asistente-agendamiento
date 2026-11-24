# Matriz de riesgos del asistente

Producto: asistente para profesionales independientes.
La fotografía es el caso de demostración.

## Método

Probabilidad e impacto se estiman de 1 a 5.
Puntaje = probabilidad × impacto.
BAJO: 1–3; MEDIO: 4–8; ALTO: 9–14; CRITICO: 15–25.

Las puntuaciones son estimaciones iniciales para el prototipo,
no probabilidades medidas ni puntuaciones residuales tras mitigación.
Deben revisarse si cambia el alcance, los datos o la exposición.

Al límite indica que variar un punto en probabilidad o impacto
puede cambiar la categoría.

## Resumen

| ID | Probabilidad | Impacto | Puntaje | Nivel | Al límite |
|---|---:|---:|---:|---|---|
| R1 | 2 | 4 | 8 | MEDIO | Sí |
| R2 | 3 | 4 | 12 | ALTO | Sí |
| R3 | 2 | 4 | 8 | MEDIO | Sí |
| R4 | 2 | 4 | 8 | MEDIO | Sí |
| R5 | 2 | 3 | 6 | MEDIO | Sí |
| R6 | 3 | 2 | 6 | MEDIO | Sí |

## R1 — Riesgo

Un documento recuperado contiene instrucciones que intentan cambiar el comportamiento del asistente.

**Justificación de la estimación:**
El corpus se administra localmente, pero un documento incorporado podría contener instrucciones maliciosas. El filtro tiene límites.

**Mitigación:**
Filtrar antes de construir el contexto; conservar solo fuentes aceptadas; abstenerse si no queda contexto utilizable. Mantener instrucciones de sistema separadas de los documentos.

**Supervisión y responsable:**
El responsable del corpus revisa documentos nuevos y los descartes antes de corregir o volver a incorporar contenido. Esta revisión es manual, no una pausa automática del grafo.

**Referencias de implementación y evidencia:**
seguridad_rag.py: filtrar_documentos_sospechosos; registro_rag.py: _registrar_consulta; test_integracion_seguridad_rag.py.

## R2 — Riesgo

Activar una modificación del prompt que elimine límites o permita afirmar acciones que el asistente no realiza.

**Justificación de la estimación:**
Los prompts cambian durante el desarrollo y afectan todas las respuestas. Una modificación incorrecta puede alterar los límites de autonomía.

**Mitigación:**
Registrar versiones y diferencias; comprobar huellas; activar la propuesta únicamente después de aprobarla.

**Supervisión y responsable:**
El mantenedor revisa el texto y sus diferencias antes de aprobar. grafo_supervision.py se pausa en solicitar_aprobacion mediante interrupt(); Command reanuda con aprobación o rechazo. aplicar_decision conserva la selección anterior si se rechaza.

**Referencias de implementación y evidencia:**
registro_prompts.py: comparar_versiones; grafo_supervision.py: solicitar_aprobacion; prompt_activo.py: aplicar_decision; test_prompt_activo.py.

## R3 — Riesgo

Responder con un precio, duración o condición incorrectos aunque la respuesta incluya una cita válida.

**Justificación de la estimación:**
El catálogo es pequeño, pero una cita existente no demuestra que el documento respalde cada afirmación generada.

**Mitigación:**
Usar el contexto recuperado, exigir citas existentes y permitir abstención. Complementar con evaluación manual del contenido.

**Supervisión y responsable:**
El responsable revisa respuestas de prueba al cambiar documentos, modelo o prompt. Si detecta información falsa, suspende la entrega de esa versión hasta corregirla y repetir la evaluación.

**Referencias de implementación y evidencia:**
responder_corpus.py: construir_prompt y validar_citas; evaluacion_recuperacion.py; docs/evaluaciones/.

## R4 — Riesgo

Exponer preguntas, documentos sensibles o credenciales en registros operativos o archivos publicados.

**Justificación de la estimación:**
Actualmente usamos datos de ejemplo, pero cambios de código podrían incorporar contenido crudo a los registros.

**Mitigación:**
Registrar longitudes, huellas, conteos y consumo; registrar errores por tipo; excluir .env, credenciales.json, logs/ y .local/ de Git.

**Supervisión y responsable:**
El mantenedor revisa los campos registrados y los archivos preparados para cada entrega. Los registros de evaluación publicados deben contener exclusivamente datos de ejemplo.

**Referencias de implementación y evidencia:**
logging_rag.py: registrar_evento; registro_rag.py: registrar_consulta; .gitignore; docs/evaluaciones/revision-logging-rag.md.

## R5 — Riesgo

Responder con una política antigua porque el corpus cambió pero el índice persistido no se actualizó.

**Justificación de la estimación:**
Modificar un Markdown no actualiza automáticamente los fragmentos que ya están guardados en Chroma.

**Mitigación:**
Ejecutar la actualización incremental y verificar que el índice coincida con el corpus antes de utilizar cambios de contenido.

**Supervisión y responsable:**
El responsable del corpus comprueba los fragmentos modificados y una consulta sobre la política actualizada antes de dar el cambio por terminado.

**Referencias de implementación y evidencia:**
indexar_corpus.py: actualización incremental y modo verificar; docs/corpus/.

## R6 — Riesgo

Interrumpir una consulta por falta de cuota, alta demanda o indisponibilidad del proveedor.

**Justificación de la estimación:**
Ya se observaron errores HTTP 429 y 503. En el alcance actual interrumpen la orientación, pero no modifican reservas.

**Mitigación:**
Mantener tiempos de espera y registrar el tipo de fallo. No presentar una consulta fallida como una respuesta exitosa. El cliente HTTP tiene reintentos acotados, pero no debemos suponer que se aplican también al flujo LangChain del RAG.

**Supervisión y responsable:**
El operador revisa cuota y disponibilidad antes de repetir consultas. No ejecuta reintentos masivos para intentar resolver una cuota agotada.

**Referencias de implementación y evidencia:**
registro_rag.py: configuración timeout y max_retries, registro de consulta_fallida; cliente.py: cliente HTTP con reintentos.

## Límites de los controles

- El filtro por patrones es parcial y puede tener falsos positivos
  y falsos negativos.
- Validar números de cita no verifica por sí solo la veracidad
  de todas las afirmaciones.
- Las huellas detectan cambios; no autentican al autor.
- La aprobación funciona en la terminal local, sin gestión
  de usuarios ni autorización de roles.
- El checkpoint del grafo vive en RAM; la selección aprobada
  se conserva en .local/prompt_activo.json.
- Las revisiones manuales descritas son procedimientos definidos;
  no se presentan como automatizaciones ni como ejecuciones ya realizadas.
