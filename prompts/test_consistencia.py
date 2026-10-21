import json
from datetime import datetime, timezone
from pathlib import Path
from time import sleep

from prompts.banco import BANCO_DE_PROMPTS
from src.consumir_gemini import (
    armar_peticion,
    enviar_peticion,
    extraer_texto,
    parsear_respuesta_json,
)


MODELO = "gemini-3.6-flash"
REPETICIONES = 3
CARPETA = Path(__file__).resolve().parent


def probar_consistencia():
    fecha = datetime.now(timezone.utc)
    nombre = f"registro-{fecha:%Y%m%dT%H%M%S%fZ}.json"
    ruta = CARPETA / nombre

    registro = {
        "fecha_utc": fecha.isoformat(),
        "modelo": MODELO,
        "repeticiones_por_prompt": REPETICIONES,
        "alcance": (
            "Validación automática de JSON, claves, tipos y "
            "valores booleanos esperados. La calidad del texto "
            "requiere revisión manual."
        ),
        "prompts": [],
    }

    for prompt in BANCO_DE_PROMPTS:
        resultado_prompt = {
            "nombre": prompt["nombre"],
            "system_instruction": prompt["system_instruction"],
            "entrada_usuario": prompt["ejemplo_usuario"],
            "estructura_esperada": prompt["estructura_esperada"],
            "contacto_esperado": prompt["contacto_esperado"],
            "criterio_calidad": prompt["criterio_calidad"],
            "revision_manual": "pendiente",
            "exitos": 0,
            "fallos": 0,
            "intentos": [],
        }
        registro["prompts"].append(resultado_prompt)

        for numero in range(1, REPETICIONES + 1):
            print(
                f"\n{prompt['nombre']} "
                f"— intento {numero}/{REPETICIONES}",
                flush=True,
            )

            intento = {
                "numero": numero,
                "valido": False,
            }

            try:
                url, body = armar_peticion(
                    prompt["ejemplo_usuario"],
                    modelo=MODELO,
                    system_instruction=prompt["system_instruction"],
                )

                respuesta_api = enviar_peticion(url, body)
                texto = extraer_texto(respuesta_api)

                # Conservar el texto incluso si luego falla su validación.
                intento["texto_generado"] = texto
                intento["modelo_respuesta"] = respuesta_api.get(
                    "modelVersion"
                )

                datos = parsear_respuesta_json(texto)

                if (
                    datos["requiere_contacto_profesional"]
                    != prompt["contacto_esperado"]
                ):
                    raise ValueError(
                        "El indicador de contacto profesional "
                        "no coincide con lo esperado para este caso."
                    )

                intento["valido"] = True
                intento["respuesta_validada"] = datos
                resultado_prompt["exitos"] += 1

                print("Validación automática: correcta")
                print(json.dumps(
                    datos,
                    indent=2,
                    ensure_ascii=False,
                ))

            except (RuntimeError, ValueError, KeyError, TypeError) as error:
                intento["error"] = str(error)
                resultado_prompt["fallos"] += 1
                print(f"Falló: {error}")

            resultado_prompt["intentos"].append(intento)

            # Guardar cada intento para conservar el avance.
            ruta.write_text(
                json.dumps(registro, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )

            sleep(3)

    print("\nResultados de validación automática:")

    for resultado in registro["prompts"]:
        print(
            f"{resultado['nombre']}: "
            f"{resultado['exitos']}/{REPETICIONES} válidos; "
            f"{resultado['fallos']} fallos"
        )

    print(f"\nRegistro guardado en: {ruta}")
    print("Pendiente: revisar la calidad del texto de las respuestas.")


if __name__ == "__main__":
    probar_consistencia()