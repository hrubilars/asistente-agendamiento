# Verificación de instalación limpia

Fecha: 21 de octubre de 2026.

## Procedimiento

Se clonó el repositorio en una carpeta independiente:
`asistente-agendamiento-verificacion`.

Se creó un entorno virtual nuevo, se instalaron las dependencias
desde `requirements.txt` y se configuró la clave en un archivo
`.env` local.

## Resultados locales

| Comprobación | Resultado |
|---|---|
| Versión de Python | 3.14.8 |
| `python -m pip check` | Sin dependencias incompatibles |
| `git check-ignore .env` | `.env` está ignorado |
| `git ls-files -- .env` | Sin resultados |
| `git log --all --oneline -- .env` | Sin resultados |
| `git status --short` | Copia de trabajo limpia |
| Inicio del programa | Correcto; mostró la interfaz y recibió la consulta |

Estas comprobaciones confirman que `.env` no está versionado
ni aparece en el historial consultado bajo ese nombre.
No constituyen una búsqueda completa de credenciales en otros archivos.

## Prueba contra la API

Comando:

`python src/consumir_gemini.py`

Consulta:

> ¿Cuánto cuesta el retrato profesional y cuánto dura?

El servicio devolvió HTTP 503 (`UNAVAILABLE`) e informó alta demanda.

La aplicación capturó el error y mostró un mensaje sin un traceback
sin controlar.

## Conclusión

La instalación y el inicio del programa quedaron verificados
en un entorno nuevo.

La ejecución funcional completa desde este clon sigue pendiente:
se debe repetir una prueba cuando el proveedor esté disponible
y comprobar la respuesta JSON validada.