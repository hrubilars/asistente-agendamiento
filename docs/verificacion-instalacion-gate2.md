# Ensayo de instalación limpia — Gate 2

Fecha: 25 de noviembre de 2026.
Commit verificado: 3d24f7b.
Entorno: macOS, Python 3.14.8 y entorno virtual nuevo.

## Instalación y pruebas

Se clonó el repositorio en una carpeta nueva y se instalaron
las dependencias desde requirements.txt.

python -m pip check no encontró incompatibilidades.

Las 18 pruebas de seguridad, integración del filtro, supervisión
y selección del prompt pasaron sin llamadas a Gemini.

Se observaron avisos de obsolescencia de dependencias,
sin impedir la ejecución.

## Índice persistente

- Corpus: cinco documentos.
- Indexación inicial: cinco fragmentos guardados.
- Reapertura: cinco fragmentos verificados sin recalcular embeddings.
- Actualización sin cambios: cinco conservados, cero embeddings nuevos
  y cero fragmentos retirados.

Este ensayo no modifica el corpus; la actualización con cambios
se comprobó durante el desarrollo.

## Supervisión

El grafo se pausó y solicitó aprobación.
Se aprobó manualmente la versión 2 y se guardó su selección local.

Las pruebas automatizadas también comprobaron el rechazo
y la conservación de la versión anterior.

## Consulta real integrada

Pregunta: ¿Cuánto cuesta la sesión familiar y cuánto dura?

Respuesta: La sesión familiar dura 60 minutos y cuesta $55.000 CLP [1].

Fuente: docs/corpus/sesion-familiar.md.

- Modelo solicitado: gemini-3.5-flash-lite.
- Fragmentos recuperados y aceptados: dos.
- Fragmentos descartados: cero.
- Fuentes citadas: una.
- Tiempo total: 6180,78 ms.
- Tokens de entrada: 295.
- Tokens de salida: 21.
- Tokens totales: 316.
- Costo estimado de generación: USD 0,000141.
- Costo del embedding: desconocido, no incluido.

Se registraron nueve eventos operativos con el mismo trace_id.
Los eventos mostrados no contienen el texto completo de la pregunta,
la respuesta ni los documentos.

La evidencia JSON conserva una consulta ficticia de demostración
y sus eventos. No contiene credenciales.

## Evidencia

[Consulta y eventos del ensayo](evaluaciones/gate2-instalacion-limpia.json)

El resultado confirma esta ejecución y complementa las pruebas
simuladas del filtro. No demuestra inmunidad frente a toda inyección
ni garantiza la corrección de cualquier respuesta futura.