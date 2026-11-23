# Bloque 31 — Verificación del logging del RAG

## Implementación

Se instrumentó el flujo existente de recuperación y generación,
conservando su validación de citas y su respuesta de abstención.

Los eventos operativos se escriben en logs/rag.jsonl.
La carpeta logs/ está excluida de Git.

Cada consulta tiene un trace_id que relaciona sus eventos.

## Pruebas locales

Se verificaron sin llamadas a la API:

- Correlación de eventos, citas y consumo.
- Abstención sin generación cuando no hay documentos.
- Identificación de un fallo durante la generación.
- Restauración del contexto después de un error.
- Registro del tipo de error sin exponer su mensaje completo.

## Consulta real

Consulta:
¿Cuánto cuesta la sesión familiar y cuánto dura?

Modelo solicitado: gemini-3.5-flash-lite.

Resultados:

- Eventos correlacionados: 8.
- Fragmentos recuperados: 2.
- Fuentes citadas: 1.
- Tokens de entrada: 218.
- Tokens de salida: 21.
- Tokens totales: 239.
- Recuperación: 1107,17 ms.
- Armado del prompt: 9,77 ms.
- Generación: 25717,19 ms.
- Tiempo total: 26841,34 ms.
- Costo estimado de generación: USD 0,0001179.

La generación fue la etapa más lenta de esta corrida.
Una sola observación no establece la latencia típica del sistema.

## Límites

El costo usa las tarifas configuradas en el proyecto.
No incluye el embedding ni constituye una verificación de facturación.

Los eventos mostrados contienen métricas y huellas, sin los textos
completos de pregunta, contexto o respuesta.

La validación de citas comprueba que las referencias existan;
no garantiza por sí sola el respaldo factual de cada afirmación.

La evidencia detallada de consultas de ejemplo permanece en
docs/evaluaciones/registros_latencia_costo.jsonl.

La mitigación de inyección de prompts sigue pendiente.