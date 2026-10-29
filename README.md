# Asistente de atención y agendamiento

Miniaplicación de terminal en Python que utiliza Gemini para orientar
consultas sobre servicios, precios y condiciones de un profesional
independiente.

El catálogo actual contiene datos de ejemplo de servicios de fotografía.

## Funcionalidades

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

- Python 3.14.8, versión utilizada en el ensayo de instalación.
  Otras versiones no han sido verificadas.
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

## Ejecutar el asistente

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

La consulta de documentos con RAG y las herramientas de disponibilidad
y reserva corresponden a la progresión prevista para Gate 2.
FastAPI, persistencia, interfaz y Docker se contemplan para Gate 3.

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