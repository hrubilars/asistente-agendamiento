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
- Mostrar latencia y costo estimado.
- Informar errores de conexión, tiempo de espera y errores HTTP.
- Comparar modelos y ejecutar pruebas de consistencia.

## Límites

La aplicación no consulta disponibilidad real, no confirma reservas
y no registra ni envía solicitudes al profesional.

La reserva requiere contacto directo y confirmación del profesional.

## Requisitos

- Python 3.9 o superior.
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

Desde la raíz del proyecto, con el entorno virtual activo:

```bash
python src/consumir_gemini.py
```

Ejemplo de consulta:

```text
¿Cuánto cuesta el retrato profesional y cuánto dura?
```

Si la petición funciona y la respuesta supera la validación,
la consola muestra el modelo solicitado, la latencia, el costo
estimado y el JSON validado.

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

## Estado de las pruebas

Se han obtenido respuestas JSON válidas del asistente.

Las corridas de comparación y consistencia del 21 de octubre de 2026
presentaron errores HTTP 503 y 429. Los registros se conservan
como evidencia.

La comparación con un segundo modelo y la validación completa del
banco de prompts siguen pendientes. No se presentan los fallos
del servicio como pruebas exitosas.

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

## Seguridad

- `.env` está excluido mediante `.gitignore`.
- `.env.example` contiene únicamente la referencia de configuración.
- No deben publicarse claves en código, registros ni commits.