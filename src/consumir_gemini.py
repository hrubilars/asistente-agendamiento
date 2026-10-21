import os
from time import perf_counter
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


def crear_instrucciones_sistema(profesional):
    informacion = json.dumps(profesional, ensure_ascii=False, indent=2)

    return (
        "Actúa como asistente de atención de un profesional independiente.\n"
        "Responde en español, de forma breve y clara.\n"
        "Usa exclusivamente los datos del catálogo proporcionado.\n"
        "Si falta información, indícalo y pregunta lo necesario.\n"
        "No inventes servicios, precios ni horarios disponibles.\n"
        "No puedes consultar disponibilidad ni confirmar reservas.\n"
        "No puedes registrar, guardar, tramitar ni enviar solicitudes.\n"
        "No ofrezcas realizar esas acciones ni afirmes haberlas realizado.\n"
        "Para concretar una reserva, indica que requiere contacto "
        "directo y confirmación del profesional.\n"
        "No inventes datos de contacto que no estén en el catálogo.\n"
        "No solicites datos personales para simular una gestión.\n\n"
        "Devuelve exclusivamente un objeto JSON, sin Markdown.\n"
        "El objeto debe contener exactamente estas claves:\n"
        '- "respuesta": texto de orientación para el usuario.\n'
        '- "requiere_contacto_profesional": booleano; true cuando '
        "la consulta necesita una gestión o confirmación del profesional.\n"
        '- "reserva_confirmada": booleano; siempre false, porque '
        "esta aplicación no confirma reservas.\n\n"
        f"CATÁLOGO DEL PROFESIONAL:\n{informacion}"
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

def armar_peticion(
    pregunta,
    modelo="gemini-3.6-flash",
    system_instruction=None,
):
    if not isinstance(pregunta, str) or not pregunta.strip():
        raise ValueError("La pregunta no puede estar vacía")

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("Falta configurar GEMINI_API_KEY en .env")

    url = (
        "https://generativelanguage.googleapis.com/"
        f"v1beta/models/{modelo}:generateContent?key={api_key}"
    )

    body = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": pregunta.strip()}],
            }
        ]
    }

    if system_instruction:
        body["systemInstruction"] = {
            "parts": [{"text": system_instruction}]
        }
        body["generationConfig"] = {
            "responseMimeType": "application/json"
        }

    return url, body


def enviar_peticion(url, body):
    try:
        respuesta = requests.post(
            url,
            json=body,
            timeout=(10, 90),
        )
    except requests.exceptions.Timeout:
        raise RuntimeError(
            "Se agotó el tiempo de espera del servicio."
        ) from None
    except requests.exceptions.ConnectionError:
        raise RuntimeError(
            "No se pudo conectar con el servicio."
        ) from None
    except requests.exceptions.RequestException:
        raise RuntimeError(
            "No se pudo completar la petición al servicio."
        ) from None

    # Revisar el código HTTP antes de procesar la respuesta.
    if respuesta.status_code != 200:
        mensajes = {
            400: "La petición contiene parámetros no válidos.",
            401: "El servicio rechazó la autenticación.",
            403: "La clave no tiene permiso para esta operación.",
            404: "El modelo o recurso solicitado no está disponible.",
            429: "Se alcanzó un límite de cuota o de solicitudes.",
            500: "El proveedor presentó un error interno.",
            503: "El servicio no está disponible temporalmente.",
        }

        detalle = mensajes.get(
            respuesta.status_code,
            "El servicio rechazó la petición.",
        )

        raise RuntimeError(
            f"HTTP {respuesta.status_code}: {detalle}"
        )

    try:
        datos = respuesta.json()
    except ValueError:
        raise RuntimeError(
            "La respuesta del servicio no contiene JSON válido."
        ) from None

    if not isinstance(datos, dict):
        raise RuntimeError(
            "La respuesta del servicio debe ser un objeto JSON."
        )

    return datos


def extraer_texto(datos):
    try:
        return datos["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        raise RuntimeError(
            "La respuesta no trae el texto generado en el lugar esperado."
        )

def parsear_respuesta_json(texto):
    try:
        datos = json.loads(texto)
    except json.JSONDecodeError as error:
        raise ValueError(
            "El modelo no devolvió un JSON válido."
        ) from error

    if not isinstance(datos, dict):
        raise ValueError("La respuesta debe ser un objeto JSON.")

    claves_esperadas = {
        "respuesta",
        "requiere_contacto_profesional",
        "reserva_confirmada",
    }

    if set(datos) != claves_esperadas:
        raise ValueError(
            "El JSON no contiene exactamente las claves esperadas."
        )

    if not isinstance(datos["respuesta"], str):
        raise ValueError("'respuesta' debe ser un texto.")

    if not datos["respuesta"].strip():
        raise ValueError("'respuesta' no puede estar vacía.")

    for clave in (
        "requiere_contacto_profesional",
        "reserva_confirmada",
    ):
        if not isinstance(datos[clave], bool):
            raise ValueError(f"'{clave}' debe ser un booleano.")

    if datos["reserva_confirmada"]:
        raise ValueError(
            "El modelo afirmó una reserva que la aplicación no puede confirmar."
        )

    return datos

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

def obtener_dato_de_prueba(
    pregunta,
    modelo="gemini-3.6-flash",
    system_instruction=None,
):
    url, body = armar_peticion(
        pregunta,
        modelo=modelo,
        system_instruction=system_instruction,
    )

    # Medir la duración de la petición al servicio.
    inicio = perf_counter()
    datos = enviar_peticion(url, body)
    latencia = perf_counter() - inicio

    # Confirmar que la respuesta contiene texto.
    texto = extraer_texto(datos)

    costo = calcular_costo(
        datos,
        precio_entrada=0.00000075,
        precio_salida=0.00000375,
    )

    print(f"Modelo solicitado: {modelo}")
    print(f"Latencia de la petición: {latencia:.2f} segundos")
    print(f"Costo estimado de la operación: ${costo:.6f} USD")

    return texto

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
        instrucciones = crear_instrucciones_sistema(profesional)

        print("Asistente de atención y solicitudes de hora")
        print("Esta versión no confirma ni registra reservas.\n")

        consulta = input("Escribe tu consulta: ")

        resultado = obtener_dato_de_prueba(
            consulta,
            system_instruction=instrucciones,
        )

        datos_respuesta = parsear_respuesta_json(resultado)

        print("\nJSON validado:")
        print(json.dumps(
            datos_respuesta,
            indent=2,
            ensure_ascii=False,
        ))

    except (ValueError, RuntimeError) as error:
        print("No se pudo completar la operación:", error)