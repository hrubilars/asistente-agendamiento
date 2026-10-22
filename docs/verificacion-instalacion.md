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

## Verificación funcional final

Fecha: 22 de octubre de 2026.

Se actualizó el clon independiente desde el repositorio remoto.
La instalación desde `requirements.txt` confirmó que las versiones
requeridas estaban disponibles en el entorno de verificación.

Se ejecutó:

`python src/consumir_gemini.py`

Consulta:

> Quiero una sesión familiar. ¿Cuánto cuesta y puedes confirmar
> una reserva para mañana?

Resultados:

- Modelo solicitado: `gemini-3.5-flash-lite`.
- Latencia: 33,58 segundos.
- Costo estimado: USD 0,000327.
- Respuesta JSON validada.
- Precio correcto: $55.000 CLP.
- Duración correcta: 60 minutos.
- Requiere contacto con el profesional: `true`.
- Reserva confirmada: `false`.
- Sin traceback.

## Conclusión

La instalación en un entorno independiente y la ejecución funcional
contra la API real quedaron verificadas.

El error HTTP 503 del ensayo anterior se conserva como antecedente.
La prueba del 22 de octubre permitió completar la comprobación
funcional que había quedado pendiente.