"""Construye la matriz de riesgos del asistente para profesionales."""

from pathlib import Path


RAIZ = Path(__file__).resolve().parent
ARCHIVO = RAIZ / "docs" / "matriz-riesgos.md"


# Probabilidad e impacto utilizan una escala de 1 a 5.
# Las puntuaciones consideran el prototipo actual:
# corpus pequeño y controlado, datos de ejemplo y ejecución local.
RIESGOS = [
    {
        "id": "R1",
        "riesgo": (
            "Un documento recuperado contiene instrucciones que intentan "
            "cambiar el comportamiento del asistente."
        ),
        "probabilidad": 2,
        "impacto": 4,
        "justificacion": (
            "El corpus se administra localmente, pero un documento incorporado "
            "podría contener instrucciones maliciosas. El filtro tiene límites."
        ),
        "mitigacion": (
            "Filtrar antes de construir el contexto; conservar solo fuentes "
            "aceptadas; abstenerse si no queda contexto utilizable. "
            "Mantener instrucciones de sistema separadas de los documentos."
        ),
        "supervision": (
            "El responsable del corpus revisa documentos nuevos y los descartes "
            "antes de corregir o volver a incorporar contenido. "
            "Esta revisión es manual, no una pausa automática del grafo."
        ),
        "evidencia": (
            "seguridad_rag.py: filtrar_documentos_sospechosos; "
            "registro_rag.py: _registrar_consulta; "
            "test_integracion_seguridad_rag.py."
        ),
    },
    {
        "id": "R2",
        "riesgo": (
            "Activar una modificación del prompt que elimine límites "
            "o permita afirmar acciones que el asistente no realiza."
        ),
        "probabilidad": 3,
        "impacto": 4,
        "justificacion": (
            "Los prompts cambian durante el desarrollo y afectan todas "
            "las respuestas. Una modificación incorrecta puede alterar "
            "los límites de autonomía."
        ),
        "mitigacion": (
            "Registrar versiones y diferencias; comprobar huellas; "
            "activar la propuesta únicamente después de aprobarla."
        ),
        "supervision": (
            "El mantenedor revisa el texto y sus diferencias antes de aprobar. "
            "grafo_supervision.py se pausa en solicitar_aprobacion mediante "
            "interrupt(); Command reanuda con aprobación o rechazo. "
            "aplicar_decision conserva la selección anterior si se rechaza."
        ),
        "evidencia": (
            "registro_prompts.py: comparar_versiones; "
            "grafo_supervision.py: solicitar_aprobacion; "
            "prompt_activo.py: aplicar_decision; "
            "test_prompt_activo.py."
        ),
    },
    {
        "id": "R3",
        "riesgo": (
            "Responder con un precio, duración o condición incorrectos "
            "aunque la respuesta incluya una cita válida."
        ),
        "probabilidad": 2,
        "impacto": 4,
        "justificacion": (
            "El catálogo es pequeño, pero una cita existente no demuestra "
            "que el documento respalde cada afirmación generada."
        ),
        "mitigacion": (
            "Usar el contexto recuperado, exigir citas existentes y permitir "
            "abstención. Complementar con evaluación manual del contenido."
        ),
        "supervision": (
            "El responsable revisa respuestas de prueba al cambiar documentos, "
            "modelo o prompt. Si detecta información falsa, suspende la entrega "
            "de esa versión hasta corregirla y repetir la evaluación."
        ),
        "evidencia": (
            "responder_corpus.py: construir_prompt y validar_citas; "
            "evaluacion_recuperacion.py; "
            "docs/evaluaciones/."
        ),
    },
    {
        "id": "R4",
        "riesgo": (
            "Exponer preguntas, documentos sensibles o credenciales "
            "en registros operativos o archivos publicados."
        ),
        "probabilidad": 2,
        "impacto": 4,
        "justificacion": (
            "Actualmente usamos datos de ejemplo, pero cambios de código "
            "podrían incorporar contenido crudo a los registros."
        ),
        "mitigacion": (
            "Registrar longitudes, huellas, conteos y consumo; registrar "
            "errores por tipo; excluir .env, credenciales.json, logs/ "
            "y .local/ de Git."
        ),
        "supervision": (
            "El mantenedor revisa los campos registrados y los archivos "
            "preparados para cada entrega. Los registros de evaluación "
            "publicados deben contener exclusivamente datos de ejemplo."
        ),
        "evidencia": (
            "logging_rag.py: registrar_evento; "
            "registro_rag.py: registrar_consulta; "
            ".gitignore; docs/evaluaciones/revision-logging-rag.md."
        ),
    },
    {
        "id": "R5",
        "riesgo": (
            "Responder con una política antigua porque el corpus cambió "
            "pero el índice persistido no se actualizó."
        ),
        "probabilidad": 2,
        "impacto": 3,
        "justificacion": (
            "Modificar un Markdown no actualiza automáticamente "
            "los fragmentos que ya están guardados en Chroma."
        ),
        "mitigacion": (
            "Ejecutar la actualización incremental y verificar que el índice "
            "coincida con el corpus antes de utilizar cambios de contenido."
        ),
        "supervision": (
            "El responsable del corpus comprueba los fragmentos modificados "
            "y una consulta sobre la política actualizada antes de dar "
            "el cambio por terminado."
        ),
        "evidencia": (
            "indexar_corpus.py: actualización incremental y modo verificar; "
            "docs/corpus/."
        ),
    },
    {
        "id": "R6",
        "riesgo": (
            "Interrumpir una consulta por falta de cuota, alta demanda "
            "o indisponibilidad del proveedor."
        ),
        "probabilidad": 3,
        "impacto": 2,
        "justificacion": (
            "Ya se observaron errores HTTP 429 y 503. En el alcance actual "
            "interrumpen la orientación, pero no modifican reservas."
        ),
        "mitigacion": (
            "Mantener tiempos de espera y registrar el tipo de fallo. "
            "No presentar una consulta fallida como una respuesta exitosa. "
            "El cliente HTTP tiene reintentos acotados, pero no debemos "
            "suponer que se aplican también al flujo LangChain del RAG."
        ),
        "supervision": (
            "El operador revisa cuota y disponibilidad antes de repetir "
            "consultas. No ejecuta reintentos masivos para intentar "
            "resolver una cuota agotada."
        ),
        "evidencia": (
            "registro_rag.py: configuración timeout y max_retries, "
            "registro de consulta_fallida; "
            "cliente.py: cliente HTTP con reintentos."
        ),
    },
]

# Indica en qué bloques construimos los controles de cada riesgo.
BLOQUES_POR_RIESGO = {
    "R1": "31",
    "R2": "32",
    "R3": "26 y 27",
    "R4": "31",
    "R5": "24 y 25",
    "R6": "12, 13, 28 y 31",
}

def clasificar(puntaje):
    """Aplica los rangos de severidad utilizados en el curso."""
    if puntaje <= 3:
        return "BAJO"
    if puntaje <= 8:
        return "MEDIO"
    if puntaje <= 14:
        return "ALTO"
    return "CRITICO"


def esta_al_limite(probabilidad, impacto):
    """Detecta si variar un punto en P o I cambia la categoría."""
    categoria_actual = clasificar(probabilidad * impacto)

    # Solo revisamos vecinos válidos dentro de la escala 1–5.
    for cambio_p, cambio_i in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        nueva_p = probabilidad + cambio_p
        nueva_i = impacto + cambio_i

        if 1 <= nueva_p <= 5 and 1 <= nueva_i <= 5:
            if clasificar(nueva_p * nueva_i) != categoria_actual:
                return True

    return False


def validar_riesgos(riesgos):
    """Comprueba requisitos básicos antes de generar el documento."""
    if len(riesgos) < 5:
        raise ValueError("La matriz debe contener al menos cinco riesgos.")

    identificadores = set()

    for riesgo in riesgos:
        if riesgo["id"] in identificadores:
            raise ValueError("Hay identificadores de riesgo duplicados.")
        identificadores.add(riesgo["id"])

        for campo in ("probabilidad", "impacto"):
            valor = riesgo[campo]
            if type(valor) is not int or not 1 <= valor <= 5:
                raise ValueError(f"{campo} debe ser un entero entre 1 y 5.")

        categoria = clasificar(
            riesgo["probabilidad"] * riesgo["impacto"]
        )

        # Una puntuación alta no puede quedar sin supervisión definida.
        if categoria in {"ALTO", "CRITICO"}:
            if not riesgo["supervision"].strip():
                raise ValueError("Un riesgo alto o crítico necesita supervisión.")


def generar_documento(riesgos):
    """Genera un resumen comparable y el detalle de cada control."""
    validar_riesgos(riesgos)

    lineas = [
        "# Matriz de riesgos del asistente",
        "",
        "Producto: asistente para profesionales independientes.",
        "La fotografía es el caso de demostración.",
        "",
        "## Método",
        "",
        "Probabilidad e impacto se estiman de 1 a 5.",
        "Puntaje = probabilidad × impacto.",
        "BAJO: 1–3; MEDIO: 4–8; ALTO: 9–14; CRITICO: 15–25.",
        "",
        "Las puntuaciones son estimaciones iniciales para el prototipo,",
        "no probabilidades medidas ni puntuaciones residuales tras mitigación.",
        "Deben revisarse si cambia el alcance, los datos o la exposición.",
        "",
        "Al límite indica que variar un punto en probabilidad o impacto",
        "puede cambiar la categoría.",
        "",
        "## Resumen",
        "",
        "| ID | Probabilidad | Impacto | Puntaje | Nivel | Al límite |",
        "|---|---:|---:|---:|---|---|",
    ]

    for riesgo in riesgos:
        p = riesgo["probabilidad"]
        i = riesgo["impacto"]
        limite = "Sí" if esta_al_limite(p, i) else "No"

        lineas.append(
            f"| {riesgo['id']} | {p} | {i} | {p * i} | "
            f"{clasificar(p * i)} | {limite} |"
        )

    for riesgo in riesgos:
        lineas.extend([
            "",
            f"## {riesgo['id']} — Riesgo",
            "",
            riesgo["riesgo"],
            "",
            "**Justificación de la estimación:**",
            riesgo["justificacion"],
            "",
            "**Mitigación:**",
            (
                f"Bloques del curso: {BLOQUES_POR_RIESGO[riesgo['id']]}. "
                f"{riesgo['mitigacion']}"
            ),
            "",
            "**Supervisión y responsable:**",
            riesgo["supervision"],
            "",
            "**Referencias de implementación y evidencia:**",
            riesgo["evidencia"],
        ])

    lineas.extend([
        "",
        "## Límites de los controles",
        "",
        "- El filtro por patrones es parcial y puede tener falsos positivos",
        "  y falsos negativos.",
        "- Validar números de cita no verifica por sí solo la veracidad",
        "  de todas las afirmaciones.",
        "- Las huellas detectan cambios; no autentican al autor.",
        "- La aprobación funciona en la terminal local, sin gestión",
        "  de usuarios ni autorización de roles.",
        "- El checkpoint del grafo vive en RAM; la selección aprobada",
        "  se conserva en .local/prompt_activo.json.",
        "- Las revisiones manuales descritas son procedimientos definidos;",
        "  no se presentan como automatizaciones ni como ejecuciones ya realizadas.",
        "",
    ])

    return "\n".join(lineas)


def main():
    """Comprueba los rangos y escribe la matriz del proyecto."""
    # Verificamos especialmente los límites entre categorías.
    assert clasificar(3) == "BAJO"
    assert clasificar(4) == "MEDIO"
    assert clasificar(8) == "MEDIO"
    assert clasificar(9) == "ALTO"
    assert clasificar(14) == "ALTO"
    assert clasificar(15) == "CRITICO"

    documento = generar_documento(RIESGOS)

    ARCHIVO.parent.mkdir(parents=True, exist_ok=True)
    ARCHIVO.write_text(documento, encoding="utf-8")

    for riesgo in RIESGOS:
        puntaje = riesgo["probabilidad"] * riesgo["impacto"]
        print(
            f"{riesgo['id']}: {puntaje} puntos — "
            f"{clasificar(puntaje)}"
        )

    print(f"\nRiesgos documentados: {len(RIESGOS)}")
    print(f"Matriz guardada en: {ARCHIVO}")
    print("Generación terminada sin llamadas a la API.")


if __name__ == "__main__":
    main()