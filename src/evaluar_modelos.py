import json
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter, sleep

from consumir_gemini import (
    armar_peticion,
    enviar_peticion,
    extraer_texto,
    calcular_costo,
    cargar_datos_profesional,
    preparar_consulta,
)


# Tarifas estándar de texto en USD por millón de tokens.
MODELOS = {
    "gemini-3.6-flash": {
        "entrada": 0.75,
        "salida": 3.75,
    },
    "gemini-3.8-flash": {
        "entrada": 0.75,
        "salida": 3.75,
    },
}

CONSULTA = (
    "Quiero una sesión familiar. ¿Cuánto cuesta y cuánto dura? "
    "¿Puedes confirmar una reserva para mañana a las 10?"
)

REPETICIONES = 4
FUENTE_TARIFAS = "https://ai.google.dev/gemini-api/docs/pricing"

RAIZ = Path(__file__).resolve().parent.parent
CARPETA = RAIZ / "docs" / "evaluaciones"


def evaluar_modelos():
    profesional = cargar_datos_profesional()
    pregunta = preparar_consulta(CONSULTA, profesional)

    fecha = datetime.now(timezone.utc)
    CARPETA.mkdir(parents=True, exist_ok=True)
    ruta = CARPETA / f"comparacion-{fecha:%Y%m%dT%H%M%S%fZ}.json"

    registro = {
        "fecha_utc": fecha.isoformat(),
        "consulta": CONSULTA,
        "pregunta_completa": pregunta,
        "repeticiones_por_modelo": REPETICIONES,
        "fuente_tarifas": FUENTE_TARIFAS,
        "tarifas_usd_por_millon": MODELOS,
        "criterios_revision_manual": [
            "Indica precio de sesión familiar: 55000 CLP.",
            "Indica duración de sesión familiar: 60 minutos.",
            "No confirma reserva ni inventa disponibilidad.",
        ],
        "intentos": [],
        "resumen": {},
    }

    # Alternar modelos reduce el efecto del orden de ejecución.
    for repeticion in range(1, REPETICIONES + 1):
        for modelo, tarifas in MODELOS.items():
            print(f"\n{modelo} — intento {repeticion}/{REPETICIONES}")

            intento = {
                "modelo_solicitado": modelo,
                "repeticion": repeticion,
                "exito_tecnico": False,
                "calidad_revision_manual": "pendiente",
            }

            inicio = perf_counter()

            try:
                url, body = armar_peticion(pregunta, modelo=modelo)

                inicio = perf_counter()
                datos = enviar_peticion(url, body)
                latencia = perf_counter() - inicio

                if "error" in datos:
                    error_api = datos["error"]
                    codigo = error_api.get("code", "desconocido")
                    estado = error_api.get("status", "sin estado")
                    mensaje = error_api.get("message", "Sin descripción")

                    # Evitar guardar accidentalmente la clave.
                    import os
                    clave = os.getenv("GEMINI_API_KEY")
                    if clave:
                        mensaje = mensaje.replace(clave, "[CLAVE OCULTA]")

                    raise RuntimeError(
                        f"Error API {codigo} ({estado}): {mensaje}"
                    )

                texto = extraer_texto(datos)

                if not isinstance(texto, str) or not texto.strip():
                    raise RuntimeError("La respuesta no contiene texto útil.")

                intento.update({
                    "exito_tecnico": True,
                    "latencia_segundos": round(latencia, 4),
                    "modelo_respuesta": datos.get("modelVersion"),
                    "respuesta": texto,
                    "uso_tokens": datos.get("usageMetadata", {}),
                })

                # Una respuesta puede funcionar aunque falten datos de uso.
                try:
                    costo = calcular_costo(
                        datos,
                        precio_entrada=tarifas["entrada"] / 1_000_000,
                        precio_salida=tarifas["salida"] / 1_000_000,
                    )
                    intento["costo_estimado_usd"] = costo
                    print(f"Costo estimado: ${costo:.6f} USD")
                except RuntimeError as error:
                    intento["costo_estimado_usd"] = None
                    intento["observacion_costo"] = str(error)

                print(f"Latencia: {latencia:.2f} segundos")
                print(texto)

            except (RuntimeError, ValueError, KeyError, TypeError) as error:
                intento.update({
                    "duracion_intento_fallido_segundos": round(
                        perf_counter() - inicio, 4
                    ),
                    "error": str(error),
                })
                print(f"Falló: {error}")

            registro["intentos"].append(intento)

            # Guardar después de cada intento para conservar el avance.
            ruta.write_text(
                json.dumps(registro, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )

            sleep(3)

    for modelo in MODELOS:
        intentos = [
            item for item in registro["intentos"]
            if item["modelo_solicitado"] == modelo
        ]
        exitos = [item for item in intentos if item["exito_tecnico"]]

        promedio = (
            sum(item["latencia_segundos"] for item in exitos) / len(exitos)
            if exitos else None
        )

        registro["resumen"][modelo] = {
            "intentos": len(intentos),
            "exitos_tecnicos": len(exitos),
            "fallos": len(intentos) - len(exitos),
            "latencia_promedio_exitos_segundos": promedio,
        }

        promedio_texto = (
            f"{promedio:.2f} s" if promedio is not None else "sin datos"
        )
        print(
            f"\n{modelo}: {len(exitos)}/{len(intentos)} éxitos técnicos"
            f" | Latencia promedio: {promedio_texto}"
        )

    ruta.write_text(
        json.dumps(registro, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"\nResultados guardados en: {ruta}")


if __name__ == "__main__":
    evaluar_modelos()