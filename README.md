# Asistente de atención y agendamiento

Proyecto en Python de un asistente para profesionales independientes.

La versión RAG consulta documentos propios sobre servicios y políticas,
recupera fragmentos relevantes y genera respuestas con fuentes citadas.
Incluye medición de tiempos y consumo, logging estructurado, filtrado
de documentos sospechosos y aprobación humana de versiones del prompt.

La fotografía es el caso de demostración. Los servicios, precios
y condiciones utilizados son datos de ejemplo.

La aplicación no consulta disponibilidad real ni registra, envía,
modifica, cancela o confirma reservas.

## Ejecutar el RAG — Gate 2

Todos los comandos se ejecutan desde la raíz del repositorio,
con el entorno virtual activo.

Primero completa la sección
[Instalación en macOS o Linux](#instalación-en-macos-o-linux):
clonar, crear el entorno, instalar requirements.txt y configurar
GEMINI_API_KEY en el archivo local .env.

Comprueba las dependencias:

```bash
python -m pip check
```

### 1. Crear el índice por primera vez

El corpus está en docs/corpus/. Contiene cinco documentos Markdown
con servicios y políticas del profesional de ejemplo.

```bash
python indexar_corpus.py indexar
```

Este comando calcula embeddings mediante Gemini y guarda el índice
en vectorstore/. Requiere conexión, clave válida y cuota disponible.

Se utiliza el modelo de embeddings models/gemini-embedding-001.
La colección de Chroma se llama fotografia.

Si vectorstore/ ya existe, el comando se detiene para evitar
reconstruir el índice accidentalmente.

### 2. Verificar la persistencia

Ejecuta una segunda operación independiente:

```bash
python indexar_corpus.py verificar
```

Este modo reabre Chroma y compara los textos y fuentes guardados
con el corpus actual. No recalcula embeddings ni llama a Gemini.

Comprueba persistencia y correspondencia con los archivos;
no mide la calidad de la recuperación.

### 3. Aplicar cambios al corpus

Después de modificar un documento:

```bash
python indexar_corpus.py actualizar
python indexar_corpus.py verificar
```

La actualización conserva los fragmentos vigentes, genera embeddings
para los nuevos o modificados y retira los obsoletos.

Si no hay cambios, no genera embeddings nuevos.
No es necesario borrar vectorstore/ para actualizar el contenido.

### 4. Aprobar una versión del prompt

Las dos versiones iniciales están publicadas en
docs/prompts/versiones.json, con autor, fecha, nota y huella SHA-256.

Para revisar la propuesta de versión 2:

```bash
python grafo_supervision.py
```

El grafo se pausa y muestra la propuesta:

- Responder s aprueba y activa la versión propuesta.
- Responder n conserva la selección anterior.

La selección se guarda en .local/prompt_activo.json.
Esta carpeta está excluida de Git.

Para consultar la selección actual:

```bash
python -c "from prompt_activo import cargar_version_activa; v = cargar_version_activa(); print('Versión activa:', v['version'] if v else 'prompt base')"
```

En una instalación nueva, mientras no exista una selección aprobada,
se utiliza el prompt base.

El checkpoint del grafo vive en RAM y no sobrevive al cierre
del programa. La selección aprobada sí queda guardada localmente.
La aprobación no implementa autenticación ni gestión de roles.

registro_prompts.py creó el registro inicial y se niega
a sobrescribirlo. No es necesario ejecutarlo nuevamente para instalar.

### 5. Ejecutar una consulta completa con instrumentación

```bash
python registro_rag.py "¿Cuánto cuesta la sesión familiar y cuánto dura?" --k 2
```

Esta ejecución:

1. Convierte la pregunta en un embedding y recupera fragmentos.
2. Filtra documentos con patrones sospechosos.
3. Construye el contexto y las citas solo con los documentos aceptados.
4. Genera la respuesta usando el prompt seleccionado.
5. Valida que las citas correspondan al contexto.
6. Registra tiempos, tokens y costo estimado de generación.

El comando realiza llamadas reales a Gemini.
Si no queda contexto utilizable, se abstiene sin llamar
al modelo generativo; la búsqueda ya pudo consumir un embedding.

La respuesta del RAG es texto con citas, no el contrato JSON
de la versión inicial con catálogo.

La consola muestra un objeto JSON con la respuesta, fuentes,
trace_id, tiempos, consumo y conteos de documentos.

### 6. Revisar registros y evidencias

Los eventos operativos se guardan en:

```text
logs/rag.jsonl
```

Los eventos de una misma consulta comparten trace_id.
Se registran longitudes, huellas, conteos, tiempos y consumo,
sin copiar el texto de preguntas o documentos a esos eventos.

Para revisar los últimos eventos en macOS o Linux:

```bash
tail -n 12 logs/rag.jsonl
```

La carpeta logs/ está excluida de Git.

El comando también agrega una evidencia de evaluación en:

```text
docs/evaluaciones/registros_latencia_costo.jsonl
```

Ese archivo sí conserva la pregunta y la respuesta.
Para las evidencias publicadas se utilizan exclusivamente consultas
y datos de ejemplo.

El costo de generación es una estimación con las tarifas configuradas,
no necesariamente el importe facturado. El costo del embedding
se informa como desconocido; no está incluido en esa estimación.

### 7. Evaluar la recuperación

```bash
python evaluacion_recuperacion.py --k 2
```

Evalúa diez preguntas del corpus mediante búsqueda real.
Calcula precisión, exhaustividad y F1, y guarda un reporte nuevo
en docs/evaluaciones/.

Este comando genera embeddings de las preguntas, pero no llama
al modelo de chat para redactar respuestas.

El caso sin fuente esperada no tiene exhaustividad ni F1 definidos.
La evaluación actual requiere un fragmento por archivo;
si el corpus crece, deben revisarse las etiquetas del banco.

### 8. Ejecutar pruebas de seguridad y supervisión

```bash
python -m pytest test_seguridad_rag.py test_integracion_seguridad_rag.py test_grafo_supervision.py test_prompt_activo.py -v
```

Resultado observado durante el desarrollo: 18 pruebas aprobadas.

Estas pruebas utilizan documentos y modelos simulados, sin llamadas
a Gemini. Comprueban filtrado, citas, abstención, pausa,
aprobación, rechazo y selección del prompt utilizado por el RAG.

### Documentación y límites

- [Decisión de personalización](decision_personalizacion.md)
- [Matriz de riesgos](docs/matriz-riesgos.md)
- [Evidencia del Core 28](docs/evaluaciones/revision-core28.md)
- [Verificación del logging](docs/evaluaciones/revision-logging-rag.md)
- [Evidencia del Core 32](docs/evaluaciones/revision-core32.md)

El filtro por patrones es una defensa parcial.
La validación de citas comprueba que las referencias existan;
no garantiza que respalden todas las afirmaciones.

Los reintentos del cliente HTTP de la versión inicial no se aplican
automáticamente al RAG: sus modelos de chat están configurados
con max_retries=0.

El ensayo final de instalación limpia del Gate 2 está pendiente
de ejecutar y documentar.

## Funcionalidades del asistente con catálogo JSON

- Consultar servicios, precios y duración.
- Orientar solicitudes incompletas.
- Separar las instrucciones del sistema del mensaje del usuario.
- Solicitar respuestas JSON y validar claves, tipos y restricciones.
- Mostrar el tiempo total de consulta mediante el cliente modular.
- Estimar el costo de cada operación y acumularlo durante la sesión.
- Mostrar latencia y costo estimado mediante el módulo del Gate 1.
- Reintentar fallos temporales con backoff exponencial y jitter.
- Informar errores de conexión, tiempo de espera y errores HTTP.
- Comparar modelos y ejecutar pruebas de consistencia.

## Límites

La aplicación no consulta disponibilidad real, no confirma reservas
y no registra ni envía solicitudes al profesional.

La reserva requiere contacto directo y confirmación del profesional.

## Requisitos

- Python 3.14.8, utilizado durante el desarrollo y en el ensayo
  de instalación del Gate 1. El ensayo limpio del Gate 2
  está pendiente de completar.
- Git.
- Conexión a internet.
- Una clave de Gemini con acceso y cuota para el modelo utilizado.

## Instalación en macOS o Linux

Clonar el repositorio:

```bash
git clone https://github.com/hrubilars/asistente-agendamiento.git
cd asistente-agendamiento
```

Crear y activar el entorno virtual:

```bash
python3 -m venv venv
source venv/bin/activate
```

Instalar las dependencias:

```bash
python -m pip install -r requirements.txt
```

Crear la configuración local:

```bash
cp .env.example .env
```

Editar `.env` y completar:

```dotenv
GEMINI_API_KEY=tu_clave_real
```

La clave se guarda únicamente en el archivo local `.env`.
No debe agregarse al repositorio.

## Ejecutar el asistente con catálogo JSON

Modelo predeterminado: `gemini-3.5-flash-lite`.

La elección y sus resultados están documentados en
[Decisión de arquitectura](docs/decision-arquitectura.md).

Desde la raíz del proyecto, con el entorno virtual activo:

```bash
python main.py
```

Ejemplo de consulta:

```text
¿Cuánto cuesta el retrato profesional y cuánto dura?
```

Cuando se recibe una respuesta de la API, el cliente muestra el costo
estimado de la operación y el costo acumulado de la sesión, siempre que
existan tarifas configuradas y datos de uso suficientes.

Si además la respuesta supera la validación, la consola muestra el
tiempo total de consulta y el JSON validado. El tiempo total incluye
las peticiones y las esperas entre reintentos.

El acumulado se mantiene mientras el programa está en ejecución y se
reinicia al iniciarlo nuevamente. En la ejecución actual de `main.py`
se realiza una consulta por sesión.

Si no se puede calcular el costo de una operación, se informa en
pantalla y esa operación no se suma al acumulado. Por ello, el total
solo incluye los costos que se pudieron estimar.

El módulo original del Gate 1 conserva la ejecución directa con
modelo solicitado, latencia y costo estimado:

```bash
python src/consumir_gemini.py
```

La respuesta contiene:

| Clave | Tipo | Significado |
|---|---|---|
| `respuesta` | Texto no vacío | Orientación para el usuario. |
| `requiere_contacto_profesional` | Booleano | Indica si se necesita gestión directa del profesional. |
| `reserva_confirmada` | Booleano | Siempre debe ser `false`. |

La validación automática de estructura no garantiza por sí sola
que todo el contenido del texto sea correcto.

## Catálogo

Los datos de ejemplo están en:

```text
src/datos_profesional.json
```

Incluyen servicios, precios, duración y condiciones del profesional.

## Comparación de modelos

Ejecutar:

```bash
python src/evaluar_modelos.py
```

El script realiza cuatro intentos por modelo y guarda un archivo
nuevo en `docs/evaluaciones/`.

Los registros contienen las condiciones de prueba, respuestas,
latencias, tokens, costos estimados y fallos observados.

Los costos son estimaciones calculadas con las tarifas configuradas.
No representan necesariamente el importe facturado, especialmente
si se utiliza cuota gratuita.

Consultar las tarifas vigentes:
https://ai.google.dev/gemini-api/docs/pricing

## Banco de prompts

Ejecutar desde la raíz del proyecto:

```bash
python -m prompts.test_consistencia
```

El banco contiene tres casos:

1. Consulta de servicios.
2. Solicitud incompleta.
3. Límites de agendamiento.

Se realizan tres intentos por caso contra la API real.

Cada ejecución genera un archivo `registro-*.json` en `prompts/`,
con resultados de validación y errores.

La revisión manual del texto complementa la validación automática.

## Pruebas locales del validador

Ejecutar desde la raíz del proyecto:

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

Comprueban la aceptación de una respuesta válida y el rechazo de
JSON malformado, estructura incorrecta, claves faltantes, tipos
incorrectos, texto vacío y confirmaciones de reserva.

No realizan llamadas al proveedor ni sustituyen las pruebas de
consistencia con la API real.

## Pruebas automatizadas del cliente — Bloque 14

Ejecutar desde la raíz del proyecto:

```bash
python -m pytest test_cliente.py -v
```

La suite ejecuta 12 casos y cubre:

- Clasificación de errores HTTP y respuesta exitosa.
- Recuperación tras fallos temporales.
- Propagación de errores no reintentables.
- Agotamiento de intentos.
- Cálculo y acumulación del costo estimado.
- Conversión y propagación de errores en `consultar_modelo`.

Utiliza mocks para sustituir las llamadas HTTP y las esperas.
No necesita una API key ni consume tokens.

Para ejecutar también las pruebas del validador JSON:

```bash
python -m pytest test_cliente.py tests/test_validacion_json.py -v
```

## Estado de las pruebas

El 22 de octubre de 2026 se completó la comparación de
`gemini-3.6-flash` y `gemini-3.5-flash-lite`. Se eligió Flash Lite
por costo y cumplimiento de los requisitos evaluados.

El banco ejecutó tres intentos por cada uno de sus tres prompts:
siete respuestas superaron la validación automática y la revisión
manual; dos intentos fallaron por HTTP 503 del proveedor.

Las siete pruebas locales del validador JSON también pasaron.

Evidencias:

- [Comparación y decisión](docs/decision-arquitectura.md)
- [Revisión del banco de prompts](prompts/revision-resultados.md)
- [Ensayo de instalación limpia](docs/verificacion-instalacion.md)
- [Revisión de seguridad](docs/verificacion-seguridad.md)

El 22 de octubre de 2026 se completó correctamente la ejecución
funcional desde el clon de verificación, utilizando Flash Lite
y obteniendo una respuesta JSON validada.

## Errores frecuentes

| Error | Acción |
|---|---|
| Falta `GEMINI_API_KEY` | Revisar el archivo `.env`. |
| HTTP 400 | Revisar los parámetros enviados. |
| HTTP 401 o 403 | Revisar la clave y los permisos. |
| HTTP 404 | Comprobar disponibilidad y acceso al modelo. |
| HTTP 429 | Revisar cuota y límites antes de repetir llamadas. |
| HTTP 503 | Esperar la recuperación del servicio y probar de forma controlada. |
| Tiempo de espera | Revisar conexión y disponibilidad del proveedor. |
| JSON inválido | Revisar la respuesta, las instrucciones y su validación. |

## Documentación

- [Arquitectura del asistente](docs/arquitectura.md)
- [Decisión de modelo y resultados](docs/decision-arquitectura.md)
- [Visión del producto](docs/vision-producto.md)

## Seguridad

- `.env` está excluido mediante `.gitignore`.
- `.env.example` contiene únicamente la referencia de configuración.
- No deben publicarse claves en código, registros ni commits.

## Alcance entregado en Gate 1

La versión entregada en Gate 1 implementó la base comprometida
en la ficha de alineación técnica: una miniaplicación en Python
que interpreta consultas mediante una API de IA, procesa respuestas
y maneja errores.

Se utiliza un profesional de fotografía como caso de ejemplo.

Gate 2 incorpora consulta documental con RAG, fuentes citadas,
evaluación de recuperación, medición, trazabilidad y controles
de seguridad.

La consulta de disponibilidad y la gestión de reservas siguen fuera
del alcance implementado. Su incorporación se definirá en el diseño
funcional del producto final.

FastAPI y Docker corresponden a la siguiente etapa del curso.

## Cliente modular — Bloques 12 y 13

El asistente se ejecuta desde la raíz del proyecto:

```bash
python main.py
```

`main.py` carga el catálogo del profesional, construye las instrucciones
de sistema, consulta el modelo mediante el cliente modular y valida
el JSON antes de mostrarlo.

### Organización

- `main.py`: interacción con el usuario y validación de la respuesta.
- `cliente.py`: consulta del modelo, reintentos y registro de costos.
- `src/consumir_gemini.py`: construcción de peticiones, comunicación
  HTTP y extracción del texto generado.

### Manejo de errores y reintentos

- HTTP 401/403: produce `ValueError`, sin reintentar.
- HTTP 429, HTTP 5xx, errores de conexión y timeout:
  producen `TimeoutError` y permiten reintentos.
- Otros errores HTTP o respuestas inválidas:
  producen `RuntimeError`, sin reintentar automáticamente.

El cliente realiza hasta tres intentos en total. Entre fallos
temporales utiliza backoff exponencial: con la configuración
predeterminada, la espera comienza en dos segundos y aumenta en el
siguiente reintento. Se agrega una variación aleatoria o jitter y se
respeta una espera máxima de 30 segundos.

El cliente se detiene inmediatamente cuando obtiene una respuesta
exitosa y no espera después del último intento.

Si agota los intentos, informa:
“El servicio no respondió tras varios intentos. Intenta más tarde.”

Los reintentos no garantizan resolver una cuota agotada. El encabezado
`Retry-After`, cuando existe, se conserva en el detalle del error;
todavía no modifica automáticamente la espera.

### Verificación realizada

Se verificaron mediante simulaciones, sin llamadas a la API:

- Recuperación después de dos fallos temporales.
- Propagación de credenciales inválidas sin reintentos.
- Detención al agotar los intentos.
- Integración de estos comportamientos en `consultar_modelo`.

También se realizó una consulta real mediante `python main.py`,
con respuesta JSON válida sobre la sesión familiar:
55.000 CLP, 60 minutos y reserva no confirmada.

El 27 de octubre de 2026 se realizó un ensayo de diez consultas reales.
Todas respondieron correctamente y el costo estimado acumulado fue de
USD $0,000265. No se observó un error 429 durante ese ensayo.

También se verificaron mediante simulaciones las esperas exponenciales
y el registro de costos, sin realizar llamadas a la API.

El detalle está en el [registro del ensayo](docs/evaluaciones/ensayo-rate-limit.md).

## Procesamiento de texto — Bloque 15

`pipeline_texto.py` contiene las funciones de limpieza, tokenización
y conteo de palabras.

Pruebas locales, sin llamadas a la API:

```bash
python -m pytest test_pipeline_texto.py -v
```

Evaluación de tres respuestas reales del asistente contra referencias:

```bash
python evaluar_pipeline_texto.py
```

Esta evaluación consume tokens y guarda un registro nuevo en
`docs/evaluaciones/`. Compara el texto antes y después de procesarlo;
la coincidencia de palabras no garantiza que la respuesta sea correcta.

Consultar la [revisión de resultados](docs/evaluaciones/revision-pipeline.md).

## Métricas de texto — Bloque 16

`metricas_texto.py` calcula coincidencias con repeticiones,
precisión, cobertura y F1.

Pruebas locales:

```bash
python -m pytest test_metricas_texto.py -v
```

Calcular métricas sobre las tres respuestas reales guardadas:

```bash
python evaluar_metricas_texto.py
```

Este comando no realiza nuevas llamadas a la API. Guarda las métricas,
sus promedios y los casos ordenados por F1 en un registro nuevo.

Consultar la [revisión de métricas](docs/evaluaciones/revision-metricas.md).

## Revisión cualitativa — Bloque 17

Se generaron veinte respuestas reales con métricas de texto.
Se revisaron diez casos: cinco con menor F1 y cinco con mayor F1,
aplicando corrección factual, completitud y contradicción.

La revisión fue realizada con apoyo de IA y validada por el autor.

- [Resultados](docs/evaluaciones/core17-resultados.json)
- [Revisión manual](docs/evaluaciones/core17-revision-manual.json)
- [Límites de la métrica](docs/limites_metrica.md)

`revision_manual.py` registra las valoraciones acordadas y no
realiza llamadas a la API ni sustituye la lectura de los casos.