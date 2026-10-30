from collections import Counter

from pipeline_texto import procesar_texto


def contar_coincidencias(
    tokens_referencia: list[str],
    tokens_respuesta: list[str],
) -> int:
    """Cuenta palabras coincidentes, considerando sus repeticiones."""

    referencia = Counter(tokens_referencia)
    respuesta = Counter(tokens_respuesta)

    # La intersección conserva el mínimo de apariciones de cada palabra.
    coincidencias = referencia & respuesta
    return sum(coincidencias.values())


def calcular_precision_cobertura_f1(
    tokens_referencia: list[str],
    tokens_respuesta: list[str],
) -> dict[str, float]:
    """Calcula métricas de coincidencia léxica entre dos listas."""

    # Adoptamos cero como resultado cuando alguno de los textos está vacío.
    if not tokens_referencia or not tokens_respuesta:
        return {"precision": 0.0, "cobertura": 0.0, "f1": 0.0}

    coincidencias = contar_coincidencias(
        tokens_referencia,
        tokens_respuesta,
    )

    precision = coincidencias / len(tokens_respuesta)
    cobertura = coincidencias / len(tokens_referencia)

    # F1 es la media armónica de precisión y cobertura.
    f1 = (
        2 * precision * cobertura / (precision + cobertura)
        if precision + cobertura
        else 0.0
    )

    return {
        "precision": precision,
        "cobertura": cobertura,
        "f1": f1,
    }


def calcular_metricas(
    texto_referencia: str,
    texto_respuesta: str,
) -> dict[str, float]:
    """Procesa ambos textos antes de calcular sus métricas."""

    return calcular_precision_cobertura_f1(
        procesar_texto(texto_referencia),
        procesar_texto(texto_respuesta),
    )


def resumir_metricas(
    resultados: list[dict[str, float]],
) -> dict[str, float]:
    """Calcula el promedio de cada métrica entre los casos evaluados."""

    if not resultados:
        return {
            "precision_promedio": 0.0,
            "cobertura_promedio": 0.0,
            "f1_promedio": 0.0,
        }

    cantidad = len(resultados)

    return {
        f"{metrica}_promedio": sum(
            resultado[metrica] for resultado in resultados
        ) / cantidad
        for metrica in ("precision", "cobertura", "f1")
    }