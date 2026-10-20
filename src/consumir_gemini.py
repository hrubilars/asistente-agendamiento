import os
import requests
from dotenv import load_dotenv

# IMPORTACIONES ESPECIFICAS
import json
from pathlib import Path
# IMPORTACIONES ESPECIFICAS

load_dotenv()

# FUNCIONES NUEVAS PARA TRABAJAR CON PROFESIONAL Y CONSULTA
def cargar_datos_profesional():
    ruta = Path(__file__).resolve().parent / "datos_profesional.json"

    try:
        with ruta.open("r", encoding="utf-8") as archivo:
            return json.load(archivo)
    except FileNotFoundError:
        raise RuntimeError(
            "No se encontró el archivo de datos del profesional."
        )
    except json.JSONDecodeError:
        raise RuntimeError(
            "El archivo de datos del profesional no contiene JSON válido."
        )


def preparar_consulta(consulta, profesional):
    if not consulta.strip():
        raise ValueError("La consulta no puede estar vacía")

    informacion = json.dumps(profesional, ensure_ascii=False, indent=2)

    return (
        "Actúa como asistente de atención de un profesional independiente.\n"
        "Responde en español, de forma breve y clara.\n"
        "Usa exclusivamente los datos del profesional que se entregan abajo.\n"
        "Si falta información, indícalo y pregunta lo necesario.\n"
        "No inventes servicios, precios ni horarios disponibles.\n"
        "No confirmes reservas: solo orienta sobre la solicitud.\n\n"
        f"DATOS DEL PROFESIONAL:\n{informacion}\n\n"
        f"CONSULTA DEL USUARIO:\n{consulta}"
    )
# FIN FUNCIONES NUEVAS PARA TRABAJAR CON PROFESIONAL Y CONSULTA

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

#try:
#    resultado = obtener_dato_de_prueba(
#       "Confirma en una frase corta que esta conexión funciona."
#    )
#    print(resultado)
#except (ValueError, RuntimeError) as error:
#    print("No se pudo completar la operación:", error)

if __name__ == "__main__":
    try:
        profesional = cargar_datos_profesional()

        print("Asistente de atención y solicitudes de hora")
        print("Esta versión no confirma reservas.\n")

        consulta = input("Escribe tu consulta: ")
        pregunta = preparar_consulta(consulta, profesional)

        resultado = obtener_dato_de_prueba(pregunta)

        print("\nRespuesta:")
        print(resultado)

    except (ValueError, RuntimeError) as error:
        print("No se pudo completar la operación:", error)