# Práctica 29 — Preparación del dataset de personalización

## Objetivo

Preparar ejemplos para clasificar la intención de las consultas
del asistente de atención y agendamiento para profesionales independientes.

Clasificar una solicitud no implica registrarla ni ejecutarla.
La fotografía se utiliza como caso de ejemplo.

## Dataset

Se construyeron 12 ejemplos simulados, sin datos personales:

- consultar_servicio: 3.
- consultar_politica: 3.
- solicitar_reserva: 3.
- gestionar_reserva: 3.

Cada salida contiene intencion y requiere_contacto_profesional.

## Verificación realizada

Comando:

python dataset_tuning.py

Resultado: 12 ejemplos construidos y cero problemas encontrados.

Se comprobó que el validador detecta:

- Una entrada duplicada.
- Una clave faltante.
- Un JSON malformado.

Las comprobaciones se realizaron sobre copias del dataset.

## Alcance y límites

La ejecución fue local, sin llamadas a la API ni entrenamiento.

Los ejemplos están preparados en estructuras de Python.
Todavía no se exportaron al formato de entrenamiento de Vertex AI.

La validación comprueba estructura y duplicados; no garantiza
calidad semántica ni demuestra que un modelo haya aprendido.

Los 12 ejemplos cumplen el mínimo de esta práctica, pero no
constituyen por sí solos evidencia de suficiencia para entrenamiento.