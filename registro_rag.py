"""Funciones para instrumentar el flujo RAG del asistente."""

from datetime import datetime, timezone

from langchain_core.output_parsers import StrOutputParser

from cadena_asistente import MODELO
from cliente import TARIFAS_MODELOS
from recuperar_corpus import formatear_contexto, recuperar_fragmentos
from responder_corpus import SIN_INFORMACION, construir_prompt, validar_citas

from contextlib import contextmanager
from time import perf_counter


@contextmanager
def medir(tiempos, etapa):
    """Guarda en segundos cuánto demora el bloque dentro de with."""
    # Antes de ejecutar el bloque, tomamos una lectura del reloj.
    inicio = perf_counter()

    try:
        # Cede el control al código que queremos medir.
        # No crea hilos ni ejecuta operaciones en paralelo.
        yield
    finally:
        # También registramos el tiempo si el bloque termina con error.
        # Ese error sigue propagándose: medir() no lo oculta.
        tiempos[etapa] = perf_counter() - inicio


def calcular_costo_consulta(uso, tarifas):
    """Estima el costo de generación con tokens reportados por LangChain.

    Las tarifas deben estar expresadas en USD por token,
    igual que en TARIFAS_MODELOS de cliente.py.
    """
    # Si falta el consumo o la tarifa, desconocemos el costo.
    # Devolver None evita confundir "sin información" con "gratis".
    if not uso or not tarifas:
        return None

    entrada = uso.get("input_tokens")
    salida = uso.get("output_tokens")

    # No sustituimos un consumo desconocido por cero.
    # type(...) is int también rechaza booleanos como True.
    if any(type(valor) is not int or valor < 0 for valor in (entrada, salida)):
        return None

    # Usamos los contadores normalizados de LangChain.
    # No sumamos nuevamente detalles de razonamiento a output_tokens.
    return (
        entrada * tarifas["entrada"]
        + salida * tarifas["salida"]
    )

def registrar_consulta(almacen, modelo, pregunta, k=2, nombre_modelo=MODELO):
    """Ejecuta el RAG y devuelve su respuesta junto con tiempos y consumo."""
    pregunta = pregunta.strip()
    if not pregunta:
        raise ValueError("La pregunta no puede estar vacía.")
    if type(k) is not int or k < 1:
        raise ValueError("k debe ser un entero mayor o igual a 1.")

    tiempos = {}
    inicio_total = perf_counter()
    timestamp = datetime.now(timezone.utc).isoformat()

    # Etapa 1: Gemini genera el embedding de la pregunta y Chroma
    # busca los fragmentos localmente. No recalculamos el corpus.
    with medir(tiempos, "embed_y_busqueda"):
        fragmentos = recuperar_fragmentos(almacen, pregunta, k=k)

    respuesta = SIN_INFORMACION
    fuentes = {}
    uso = None

    # Si no hay fragmentos, conservamos la abstención del asistente
    # y evitamos una llamada innecesaria al modelo generativo.
    tiempos["armado_prompt"] = 0.0
    tiempos["generacion"] = 0.0
    generacion_ejecutada = False
    costo_generacion = 0.0

    if fragmentos:
        # Etapa 2: reutilizamos el contexto numerado y el mismo prompt.
        # Las reglas del sistema siguen separadas de la consulta.
        with medir(tiempos, "armado_prompt"):
            contexto, mapa_citas = formatear_contexto(fragmentos)
            prompt = construir_prompt().invoke({
                "pregunta": pregunta,
                "contexto": contexto,
            })

        # Etapa 3: conservamos el mensaje completo, incluidos los tokens.
        # Si encadenáramos directamente StrOutputParser, solo quedaría texto.
        with medir(tiempos, "generacion"):
            mensaje = modelo.invoke(prompt)

        generacion_ejecutada = True
        metadata_uso = getattr(mensaje, "usage_metadata", None)
        uso = dict(metadata_uso) if metadata_uso else None

        # Extraemos texto sin asumir que content siempre es una cadena.
        respuesta = StrOutputParser().invoke(mensaje).strip()
        if not respuesta:
            raise ValueError("El modelo devolvió una respuesta vacía.")

        # Conservamos la validación existente:
        # las citas deben corresponder a los fragmentos recuperados.
        fuentes = validar_citas(respuesta, mapa_citas)

        costo_generacion = calcular_costo_consulta(
            uso,
            TARIFAS_MODELOS.get(nombre_modelo),
        )

    # Medimos el tiempo total por separado: también incluye extracción
    # del texto y validación. Puede superar la suma de las tres etapas.
    tiempo_total = perf_counter() - inicio_total

    return {
        "timestamp": timestamp,
        "pregunta": pregunta,
        "modelo_solicitado": nombre_modelo,
        "k": k,
        "fragmentos_recuperados": len(fragmentos),
        "ids_recuperados": [doc.id for doc in fragmentos],
        "respuesta": respuesta,
        "fuentes_citadas": fuentes,
        "abstencion": respuesta == SIN_INFORMACION,
        "generacion_ejecutada": generacion_ejecutada,
        "tiempos_ms": {
            etapa: round(segundos * 1000, 2)
            for etapa, segundos in tiempos.items()
        },
        "tiempo_total_ms": round(tiempo_total * 1000, 2),
        "tokens": uso,
        "costo_generacion_estimado_usd": costo_generacion,
        # Los tokens del mensaje corresponden a generación, no al
        # embedding de la pregunta. No inventamos ese consumo ni su costo.
        "costo_embedding_estimado_usd": None,
    }
