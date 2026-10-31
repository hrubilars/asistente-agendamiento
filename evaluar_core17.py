import json
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter

from casos_evaluacion import CASOS_EVALUACION
from cliente import consultar_modelo
from metricas_texto import calcular_metricas
from src.consumir_gemini import (
    cargar_datos_profesional,
    crear_instrucciones_sistema,
    parsear_respuesta_json,
)


MODELO = "gemini-3.5-flash-lite"

RUTA = (
    Path(__file__).resolve().parent
    / "docs"
    / "evaluaciones"
    / "core17-resultados.json"
)


def fecha_actual():
    """Devuelve la fecha UTC para identificar cada ejecución."""
    return datetime.now(timezone.utc).isoformat()


def guardar_registro(registro):
    """Guarda el avance mediante un archivo temporal."""
    RUTA.parent.mkdir(parents=True, exist_ok=True)
    temporal = RUTA.with_suffix(".tmp")

    temporal.write_text(
        json.dumps(registro, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporal.replace(RUTA)


def cargar_registro(configuracion):
    """Recupera el avance sin mezclar condiciones diferentes."""
    if not RUTA.exists():
        return {
            "fecha_inicio_utc": fecha_actual(),
            "configuracion": configuracion,
            "resultados": [],
            "fallos": [],
        }

    registro = json.loads(RUTA.read_text(encoding="utf-8"))

    # Si cambiaron preguntas, modelo o instrucciones, no mezclar ensayos.
    if registro["configuracion"] != configuracion:
        raise ValueError(
            "La configuración cambió respecto del registro guardado. "
            "Conserva ese archivo con otro nombre antes de iniciar "
            "un ensayo diferente."
        )

    return registro


def main():
    """Consulta los casos pendientes y conserva resultados y fallos."""
    instrucciones = crear_instrucciones_sistema(
        cargar_datos_profesional()
    )

    configuracion = {
        "modelo": MODELO,
        "instrucciones_sistema": instrucciones,
        "casos": CASOS_EVALUACION,
    }

    registro = cargar_registro(configuracion)
    completados = {
        resultado["id"] for resultado in registro["resultados"]
    }

    for caso in CASOS_EVALUACION:
        if caso["id"] in completados:
            print(f"Caso {caso['id']}: ya guardado.")
            continue

        print(f"\n--- Caso {caso['id']} de 20 ---")
        print(f"Consulta: {caso['consulta']}")

        inicio = perf_counter()
        texto = None

        try:
            # Mantener las mismas instrucciones que utiliza el asistente.
            texto = consultar_modelo(
                caso["consulta"],
                system_instruction=instrucciones,
                modelo=MODELO,
            )

            respuesta_json = parsear_respuesta_json(texto)

            # Medir el texto de orientación, no todo el objeto JSON.
            metricas = calcular_metricas(
                caso["referencia"],
                respuesta_json["respuesta"],
            )

        except (RuntimeError, ValueError) as error:
            registro["fallos"].append({
                "id": caso["id"],
                "fecha_utc": fecha_actual(),
                "error": str(error),
                "texto_recibido": texto,
                "tiempo_total_segundos": perf_counter() - inicio,
            })
            guardar_registro(registro)

            print(f"Evaluación detenida: {error}")
            print("El avance quedó guardado.")
            print("Revisa el error antes de ejecutar nuevamente.")
            break

        registro["resultados"].append({
            **caso,
            "fecha_utc": fecha_actual(),
            "respuesta_original": texto,
            "respuesta_json": respuesta_json,
            "respuesta": respuesta_json["respuesta"],
            "tiempo_total_segundos": perf_counter() - inicio,
            **metricas,
        })

        # Guardar inmediatamente para no perder consultas ya realizadas.
        guardar_registro(registro)
        completados.add(caso["id"])

        print(f"Respuesta: {respuesta_json['respuesta']}")
        print(f"Precisión: {metricas['precision']:.3f}")
        print(f"Cobertura: {metricas['cobertura']:.3f}")
        print(f"F1: {metricas['f1']:.3f}")

    print("\n--- Estado del ensayo ---")
    print(f"Respuestas con JSON validado: {len(completados)}/20")
    print(f"Fallos registrados: {len(registro['fallos'])}")
    print(f"Archivo: {RUTA}")

    if len(completados) == 20:
        print("Generación completa. Falta la revisión cualitativa.")
    else:
        print("Generación pendiente de completar.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"No se pudo completar la evaluación: {error}")
        raise SystemExit(1)