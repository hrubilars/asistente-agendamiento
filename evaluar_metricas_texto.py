import json
from datetime import datetime, timezone
from pathlib import Path

from metricas_texto import calcular_metricas, resumir_metricas


CARPETA_EVALUACIONES = (
    Path(__file__).resolve().parent / "docs" / "evaluaciones"
)

ARCHIVO_ORIGEN = (
    CARPETA_EVALUACIONES / "pipeline-20261029T092711328679Z.json"
)


def main():
    """Calcula métricas sobre respuestas reales previamente registradas."""

    with ARCHIVO_ORIGEN.open("r", encoding="utf-8") as archivo:
        registro_original = json.load(archivo)

    resultados = []

    for caso in registro_original["resultados"]:
        # No incluir fallos técnicos en los promedios de respuestas.
        if caso["estado"] != "correcto":
            print(f"Caso omitido por fallo previo: {caso['nombre']}")
            continue

        respuesta = caso["respuesta_json"]["respuesta"]

        metricas = calcular_metricas(
            caso["referencia"],
            respuesta,
        )

        resultados.append({
            "nombre": caso["nombre"],
            "consulta": caso["consulta"],
            "referencia": caso["referencia"],
            "respuesta": respuesta,
            **metricas,
        })

    if not resultados:
        raise ValueError("El registro no contiene respuestas para evaluar.")

    # Ordenar de menor a mayor F1 para priorizar la revisión manual.
    resultados.sort(key=lambda caso: caso["f1"])
    resumen = resumir_metricas(resultados)

    for caso in resultados:
        print(f"\n--- {caso['nombre']} ---")
        print(f"Respuesta: {caso['respuesta']}")
        print(f"Precisión: {caso['precision']:.3f}")
        print(f"Cobertura: {caso['cobertura']:.3f}")
        print(f"F1: {caso['f1']:.3f}")

    print("\n--- Promedios por caso ---")
    for nombre, valor in resumen.items():
        print(f"{nombre}: {valor:.3f}")

    # Guardar un archivo nuevo y conservar la evidencia original.
    fecha = datetime.now(timezone.utc)
    ruta = CARPETA_EVALUACIONES / (
        f"metricas-{fecha.strftime('%Y%m%dT%H%M%S%fZ')}.json"
    )

    registro = {
        "fecha_calculo_utc": fecha.isoformat(),
        "archivo_origen": ARCHIVO_ORIGEN.name,
        "fecha_respuestas_utc": registro_original["fecha_utc"],
        "modelo_solicitado": registro_original["modelo_solicitado"],
        "nuevas_llamadas_api": False,
        "descripcion": (
            "Coincidencia léxica con repeticiones. "
            "Los promedios se calculan por caso y no garantizan "
            "exactitud factual ni equivalencia de significado."
        ),
        "casos_evaluados": len(resultados),
        "resumen": resumen,
        "resultados_ordenados_por_f1": resultados,
    }

    ruta.write_text(
        json.dumps(registro, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"\nCasos evaluados: {len(resultados)}")
    print(f"Registro guardado en: {ruta}")
    print("Cálculo terminado sin nuevas llamadas a la API.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"No se pudo completar la evaluación: {error}")
        raise SystemExit(1)