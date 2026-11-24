# Verificación del Core 32

## Proyecto

Asistente de atención para profesionales independientes.
La fotografía es el caso de demostración.

## Versionado de prompts

Se registraron dos versiones propias en docs/prompts/versiones.json:

- Versión 1: instrucciones base del RAG.
- Versión 2: propuesta que refuerza la seguridad del contexto
  y los límites de autonomía.

Cada versión incluye texto, autor, fecha, nota y huella SHA-256.
registro_prompts.py permite mostrar las diferencias entre versiones.

Registrar una versión no la activa automáticamente.

## Supervisión humana

grafo_supervision.py implementa una pausa real con interrupt(),
un checkpointer en memoria y reanudación mediante Command.

- La aprobación selecciona la versión propuesta.
- El rechazo conserva la versión anterior.
- La decisión debe ser un booleano.
- La pausa y la reanudación utilizan el mismo thread_id.

Se realizó una aprobación manual desde la terminal.
Las pruebas automatizadas verificaron aprobación y rechazo.

## Activación en el RAG

prompt_activo.py comprueba las huellas antes de guardar o cargar
la selección activa.

responder_corpus.py utiliza la versión activa al construir
el mensaje de sistema. registro_rag.py reutiliza esa función.

Las pruebas verifican que aprobar cambia el prompt utilizado
y que rechazar mantiene el anterior.

La selección local está excluida de Git mediante /.local/.
En una instalación nueva debe ejecutarse la aprobación;
mientras no exista una selección, se utiliza el prompt base.

## Matriz de riesgos

docs/matriz-riesgos.md contiene seis riesgos propios, con:

- Probabilidad e impacto de 1 a 5.
- Puntaje y categoría.
- Identificación de casos al límite.
- Justificación, mitigación y supervisión.
- Referencias al código y a las evidencias.

El riesgo alto R2 se vincula con la aprobación humana del prompt.
Las revisiones manuales se distinguen de los controles automatizados.

## Verificación automatizada

Ejecutar desde la raíz:

    python -m pytest test_seguridad_rag.py test_integracion_seguridad_rag.py test_grafo_supervision.py test_prompt_activo.py -v

Resultado observado: 18 pruebas aprobadas.

Estas pruebas no llaman a Gemini. Incluyen filtrado de documentos,
reconstrucción de citas, abstención sin generación, pausa del grafo,
aprobación, rechazo y selección del prompt utilizado por el RAG.

La matriz se generó mediante:

    python matriz_riesgos.py

## Límites

- El filtro por patrones no detecta todos los ataques.
- La existencia de citas no garantiza la veracidad del contenido.
- Una huella no autentica al autor.
- La aprobación local no implementa usuarios ni roles.
- El checkpoint vive en RAM y se pierde al cerrar el programa.
- La selección aprobada persiste localmente.
- Las puntuaciones de riesgo son estimaciones iniciales.