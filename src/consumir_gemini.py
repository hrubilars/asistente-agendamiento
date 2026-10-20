import os
import requests
from dotenv import load_dotenv

load_dotenv()


def armar_peticion(pregunta):
    if not pregunta:
        raise ValueError("La pregunta no puede estar vacía")

    api_key = os.getenv("GEMINI_API_KEY")
    modelo = "gemini-3.6-flash"

    url = (
        "https://generativelanguage.googleapis.com/"
        f"v1beta/models/{modelo}:generateContent?key={api_key}"
    )

    body = {
        "contents": [
            {
                "parts": [
                    {"text": pregunta}
                ]
            }
        ]
    }

    return url, body


def enviar_peticion(url, body):
    try:
        respuesta = requests.post(url, json=body)
    except requests.exceptions.ConnectionError:
        raise RuntimeError(
            "No se pudo conectar con el servicio. "
            "Intenta de nuevo en unos segundos."
        )

    try:
        return respuesta.json()
    except requests.exceptions.JSONDecodeError:
        raise RuntimeError(
            "La respuesta del servicio no llegó en el formato esperado."
        )


def extraer_texto(datos):
    try:
        return datos["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        raise RuntimeError(
            "La respuesta no trae el texto generado en el lugar esperado."
        )

def calcular_costo(datos, precio_entrada, precio_salida):
    try:
        uso = datos["usageMetadata"]

        tokens_entrada = uso["promptTokenCount"]
        tokens_salida = uso["candidatesTokenCount"]
        tokens_razonamiento = uso.get("thoughtsTokenCount", 0)

        costo = (
            tokens_entrada * precio_entrada
            + (tokens_salida + tokens_razonamiento) * precio_salida
        )

        return costo

    except KeyError:
        raise RuntimeError(
            "La respuesta no incluye los datos de uso necesarios "
            "para calcular el costo."
        )

def obtener_dato_de_prueba(pregunta):
    url, body = armar_peticion(pregunta)
    datos = enviar_peticion(url, body)

    # ▼ NUEVO: calcular y mostrar el costo
    costo = calcular_costo(
        datos,
        precio_entrada=0.00000075,
        precio_salida=0.00000375,
    )

    print(f"Costo estimado de la operación: ${costo:.6f} USD")
    # ▲ FIN DE LO NUEVO

    return extraer_texto(datos)

try:
    resultado = obtener_dato_de_prueba(
       "Confirma en una frase corta que esta conexión funciona."
    )
    print(resultado)
except (ValueError, RuntimeError) as error:
    print("No se pudo completar la operación:", error)