# Decisión de personalización — Core 30

## 1. El problema

El asistente para profesionales independientes necesita responder sobre
servicios y políticas usando información verificable y actualizable.
Debe mantener sus límites: actualmente no consulta disponibilidad,
registra solicitudes ni confirma reservas.

La fotografía es el caso de demostración, no el límite del producto.

Evidencia disponible:

- Cinco documentos Markdown en docs/corpus/.
- El historial consultado muestra la incorporación inicial del corpus
  el 12 de noviembre de 2026. No demuestra cambios mensuales.
- Veinte respuestas históricas del Core 17 cumplen el contrato JSON.
- Existe un fallo de ejecución registrado por separado, que no se
  considera respuesta válida ni incumplimiento de formato demostrado.
- Hay doce ejemplos simulados de clasificación, tres por intención.
  La validación estructural del dataset no encontró problemas.

La revisión de las veinte respuestas solo acredita estructura histórica.
No evalúa el tono, toda la calidad semántica ni el comportamiento del
RAG actual.

## 2. Resultado del método de decisión

Se aplicó el método de cinco preguntas publicado en el curso.

| Criterio | Respuesta | Fundamento |
|---|---|---|
| Información que cambia seguido | False | No hay historial suficiente para acreditar cambios mensuales. |
| Problema de formato o tono | False | No está demostrado con una muestra actual; el antecedente histórico tiene 20 respuestas con estructura válida. |
| Dataset grande y de calidad | False | Hay 12 ejemplos; no se cumple el umbral orientativo de 200. |
| Presupuesto limitado o iteración rápida | True | Se adopta como objetivo de diseño comprobar cambios documentales en menos de un día, sin entrenamiento. |
| Múltiples variantes | False | No se ha identificado una necesidad de modelos entrenados distintos; catálogos diferentes no bastan para acreditarla. |

La respuesta sobre iteración rápida es un requisito adoptado para esta
etapa, no una medición de tiempo ni una declaración de presupuesto.

| Técnica | Puntaje |
|---|---:|
| RAG | 2 |
| Fine-tuning completo | 0 |
| PEFT | 1 |

Candidatas con mayor puntaje: RAG.

Los valores False por falta de evidencia son decisiones conservadoras
para este análisis; no demuestran ausencia definitiva del problema.
Los puntajes orientan la elección y no comparan calidad empírica
entre modelos entrenados.

## 3. Técnica elegida y por qué

Se elige mantener RAG como estrategia principal para consultar
servicios y políticas con fuentes citadas.

La información del profesional está fuera del modelo, en documentos
que ya se indexan, recuperan y citan. El proyecto ya cuenta con
evaluación de recuperación y cinco corridas reales de latencia
y consumo. Mantener esta solución aprovecha evidencia existente
y permite comprobar cambios sin lanzar un entrenamiento.

El método asigna el mayor puntaje a RAG bajo las condiciones declaradas.
Además, el problema principal requiere acceso a información propia,
aunque todavía no se haya demostrado una frecuencia mensual de cambios.

No se justifica por ahora un entrenamiento: los doce ejemplos son
un ejercicio de preparación y no demuestran suficiencia, generalización
ni una mejora frente a instrucciones y validación.

PEFT queda como alternativa a evaluar si aparece un problema persistente
de comportamiento o clasificación, medido con ejemplos independientes.
La consulta documental y la clasificación podrían combinarse en el futuro.

La decisión se revisará cuando exista una muestra actual del RAG
o cambien los requisitos. No se afirma que RAG resuelva por sí solo
la consistencia del formato ni la seguridad del sistema.

## 4. Qué necesitaríamos para ejecutarla

RAG ya está implementado para el corpus de demostración:

- Documentos actuales: 5.
- Documentos de ese corpus pendientes de indexación: 0, según la
  verificación previa del índice.
- Preguntas del banco de recuperación: 10, de las cuales 9 tienen
  fuentes esperadas y 1 consulta información ausente.
- Corridas reales documentadas de latencia y consumo: 5.

Para sostener la decisión falta evaluar 20 respuestas del RAG actual
con criterios explícitos de formato y tono. Las respuestas históricas
no sustituyen esa comprobación.

Si se reconsidera entrenamiento, existen 12 ejemplos de clasificación.
Faltan 188 para alcanzar el umbral orientativo de 200 del curso.
Alcanzar ese número no garantiza calidad ni cumple automáticamente
los requisitos de un proveedor.

También habría que revisar etiquetas, ampliar situaciones y reservar
casos independientes para evaluación. No se ha realizado entrenamiento
ni una comparación empírica con PEFT o fine-tuning completo.

La información de otro profesional requerirá preparar y verificar su
corpus. Esa ampliación aún no tiene un número de documentos definido.

Evidencias del repositorio:

- [Respuestas históricas](docs/evaluaciones/core17-resultados.json)
- [Dataset y validación](docs/evaluaciones/revision-dataset-tuning.md)
- [Medición del RAG](docs/evaluaciones/revision-core28.md)

Para cerrar el Gate 2 también se deben completar e integrar logging,
seguridad, versionado, riesgos y supervisión humana. Elegir RAG
no reemplaza esos requisitos.
