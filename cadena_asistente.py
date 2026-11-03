import json
import os
from pathlib import Path
from time import perf_counter

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from src.consumir_gemini import (
    cargar_datos_profesional,
    crear_instrucciones_sistema,
    parsear_respuesta_json,
)


MODELO = "gemini-3.5-flash-lite"


def construir_cadena():
    """Construye la secuencia plantilla, modelo y extracción de texto."""
    raiz = Path(__file__).resolve().parent
    load_dotenv(raiz / ".env")

    clave = os.getenv("GEMINI_API_KEY")
    if not clave:
        raise ValueError("Falta configurar GEMINI_API_KEY en .env.")

    instrucciones = crear_instrucciones_sistema(
        cargar_datos_profesional()
    )

    # Separar las instrucciones del sistema de la consulta del usuario.
    # Pasarlas como valores evita interpretar las llaves del catálogo
    # como variables adicionales de la plantilla.
    plantilla = ChatPromptTemplate.from_messages([
        ("system", "{instrucciones}"),
        ("human", "{consulta}"),
    ]).partial(instrucciones=instrucciones)

    modelo = ChatGoogleGenerativeAI(
        model=MODELO,
        api_key=clave,
        vertexai=False,
        timeout=90,
        max_retries=0,
    )

    # Solicitar JSON; la validación de sus reglas se realiza después.
    modelo_json = modelo.bind(
        response_mime_type="application/json"
    )

    return plantilla | modelo_json | StrOutputParser()


def main():
    """Ejecuta una consulta y valida el JSON recibido."""
    print("Asistente de fotografía — LangChain")
    print("Esta versión no confirma ni registra reservas.\n")

    consulta = input("Escribe tu consulta: ").strip()
    if not consulta:
        raise ValueError("La consulta no puede estar vacía.")

    cadena = construir_cadena()

    inicio = perf_counter()
    texto = cadena.invoke({"consulta": consulta})
    tiempo = perf_counter() - inicio

    # StrOutputParser extrae texto; nuestro validador comprueba el JSON.
    respuesta = parsear_respuesta_json(texto)

    print(f"\nModelo solicitado: {MODELO}")
    print(f"Tiempo total de consulta: {tiempo:.2f} segundos")
    print("\nJSON validado:")
    print(json.dumps(respuesta, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        # Captura final de la CLI. Ocultar la clave si aparece en el error.
        detalle = str(error)
        clave = os.getenv("GEMINI_API_KEY")
        if clave:
            detalle = detalle.replace(clave, "[CLAVE OCULTA]")

        print(f"No se pudo completar la consulta: {detalle}")
        raise SystemExit(1)