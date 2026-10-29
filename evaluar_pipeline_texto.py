import json
from datetime import datetime, timezone
from pathlib import Path

from cliente import consultar_modelo
from pipeline_texto import procesar_texto
from src.consumir_gemini import (
    cargar_datos_profesional,
    crear_instrucciones_sistema,
    parsear_respuesta_json,
)


CASOS = [
    {
        "nombre": "retrato_profesional",
        "consulta": "¿Cuánto cuesta el retrato profesional y cuánto dura?",
        "referencia": (
            "El retrato profesional cuesta $35.000 CLP "
            "y tiene una duración de 45 minutos."
        ),
    },
    {
        "nombre": "sesion_familiar",
        "consulta": "¿Cuánto cuesta la sesión familiar y cuánto dura?",
        "referencia": (
            "La sesión familiar cuesta $55.000 CLP "
            "y tiene una duración de 60 minutos."
        ),
    },
    {
        "nombre": "confirmacion_reserva",
        "consulta": "¿Puedes confirmar una reserva para mañana a las 10?",
        "referencia": (
            "No puedo consultar disponibilidad ni confirmar reservas. "
            "Para concretar una reserva, se requiere contacto directo "
            "y confirmación del profesional."
        ),
    },
]


def calcular_coincidencia(referencia: list[str], respuesta: list[str]) -> float:
    """Calcula qué proporción de palabras únicas de referencia aparece."""
    palabras_referencia = set(referencia)

    # Evitar una división por cero si la referencia queda vacía.
    if not palabras_referencia:
        return 0.0

    comunes = palabras_referencia & set(respuesta)
    return len(comunes) / len(palabras_referencia)


def main():
    """Evalúa tres respuestas reales y guarda sus resultados."""
    profesional = cargar_datos_profesional()
    instrucciones = crear_instrucciones_sistema(profesional)
    resultados = []

    for caso in CASOS:
        print(f"\n--- {caso['nombre']} ---")

        try:
            texto_json = consultar_modelo(
                pregunta=caso["consulta"],
                system_instruction=instrucciones,
            )

            # Validar el JSON y evaluar solo el texto de orientación.
            datos = parsear_respuesta_json(texto_json)
            respuesta = datos["respuesta"]
            referencia = caso["referencia"]

            crudo = calcular_coincidencia(
                referencia.split(),
                respuesta.split(),
            )
            procesado = calcular_coincidencia(
                procesar_texto(referencia),
                procesar_texto(respuesta),
            )

            resultados.append({
                **caso,
                "estado": "correcto",
                "respuesta_json": datos,
                "coincidencia_cruda": crudo,
                "coincidencia_procesada": procesado,
            })

            print(f"Respuesta: {respuesta}")
            print(f"Coincidencia cruda: {crudo:.1%}")
            print(f"Coincidencia procesada: {procesado:.1%}")

        except (RuntimeError, ValueError) as error:
            # Conservar el fallo como evidencia, sin contarlo como respuesta.
            resultados.append({
                **caso,
                "estado": "fallido",
                "error": str(error),
            })
            print(f"No se pudo evaluar este caso: {error}")

    # Crear un registro nuevo para no reemplazar ejecuciones anteriores.
    fecha = datetime.now(timezone.utc)
    carpeta = Path(__file__).resolve().parent / "docs" / "evaluaciones"
    carpeta.mkdir(parents=True, exist_ok=True)

    ruta = carpeta / (
        f"pipeline-{fecha.strftime('%Y%m%dT%H%M%S%fZ')}.json"
    )

    registro = {
        "fecha_utc": fecha.isoformat(),
        "modelo_solicitado": "gemini-3.5-flash-lite",
        "descripcion_metrica": (
            "Proporción de palabras únicas de la referencia "
            "presentes en la respuesta."
        ),
        "resultados": resultados,
    }

    ruta.write_text(
        json.dumps(registro, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    exitos = sum(caso["estado"] == "correcto" for caso in resultados)
    print(f"\nCasos evaluados correctamente: {exitos}/{len(CASOS)}")
    print(f"Registro guardado en: {ruta}")
    print("Pendiente: revisar manualmente la calidad de las respuestas.")


# Importar este archivo no debe ejecutar consultas a Gemini.
if __name__ == "__main__":
    main()