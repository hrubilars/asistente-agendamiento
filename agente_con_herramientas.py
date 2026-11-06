import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI

from cadena_asistente import MODELO
from unicodedata import normalize

from src.consumir_gemini import cargar_datos_profesional


def normalizar(texto: str) -> str:
    """Permite comparar nombres aunque tengan mayúsculas o tildes."""
    descompuesto = normalize("NFD", texto.casefold())
    sin_tildes = "".join(
        letra for letra in descompuesto if not "\u0300" <= letra <= "\u036f"
    )
    return " ".join(sin_tildes.split())


def consultar_servicio(nombre: str) -> str:
    """Consulta el precio y la duración de un servicio de fotografía por nombre."""
    catalogo = cargar_datos_profesional()

    for servicio in catalogo["servicios"]:
        if normalizar(servicio["nombre"]) == normalizar(nombre):
            precio = f"{servicio['precio_clp']:,}".replace(",", ".")
            return (
                f"{servicio['nombre']}: ${precio} CLP, "
                f"{servicio['duracion_minutos']} minutos."
            )

    disponibles = ", ".join(servicio["nombre"] for servicio in catalogo["servicios"])
    return f"No encontré ese servicio. Servicios del catálogo: {disponibles}."


def consultar_politica(tema: str) -> str:
    """Consulta las condiciones de pago, cancelación o agendamiento."""
    catalogo = cargar_datos_profesional()

    # Si el tema no existe, devolvemos una orientación en vez de inventar una regla.
    for nombre, condicion in catalogo["politicas"].items():
        if normalizar(nombre) == normalizar(tema):
            return condicion

    return "No encontré esa política. Puedes consultar por pago, cancelación o agendamiento."

def construir_agente():
    """Conecta Gemini con las dos herramientas de solo lectura."""
    load_dotenv(Path(__file__).resolve().parent / ".env")
    clave = os.getenv("GEMINI_API_KEY")
    if not clave:
        raise ValueError("Falta configurar GEMINI_API_KEY en el archivo .env.")

    # Expone las funciones al agente sin cambiar cómo se prueban por separado.
    herramientas = [tool(consultar_servicio), tool(consultar_politica)]
    modelo = ChatGoogleGenerativeAI(
        model=MODELO,
        api_key=clave,
        vertexai=False,
        timeout=90,
        max_retries=0,
    )

    plantilla = ChatPromptTemplate.from_messages([
        (
            "system",
            "Eres un asistente de fotografía. Responde brevemente en español. "
            "Usa consultar_servicio para obtener precios o duración; pasa el "
            "nombre del servicio, por ejemplo 'Sesión familiar'. Usa "
            "consultar_politica para condiciones; pasa 'pago', 'cancelación' "
            "o 'agendamiento'. Si preguntan por ambas cosas, usa ambas herramientas. "
            "Para un saludo simple, responde sin usar herramientas. "
            "Si falta un dato, pregunta o indica que no lo tienes. "
            "No inventes precios, políticas ni disponibilidad. "
            "No puedes consultar la agenda ni crear, confirmar, cambiar o "
            "cancelar reservas. Si solicitan una gestión, indica que deben "
            "contactar directamente al profesional.",
        ),
        ("human", "{entrada}"),
        # Aquí el agente recibe los resultados de sus llamadas anteriores.
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    agente = create_tool_calling_agent(modelo, herramientas, plantilla)
    return AgentExecutor(
        agent=agente,
        tools=herramientas,
        return_intermediate_steps=True,
        max_iterations=4,
        verbose=False,
    )

def extraer_texto_respuesta(salida: str | list) -> str:
    """Extrae el texto visible, venga como cadena o como bloques."""
    if isinstance(salida, str):
        return salida.strip()

    textos = [
        bloque["text"].strip()
        for bloque in salida
        if isinstance(bloque, dict)
        and bloque.get("type") == "text"
        and isinstance(bloque.get("text"), str)
        and bloque["text"].strip()
    ]
    return "\n".join(textos)

def main():
    consulta = input("Escribe tu consulta: ").strip()
    if not consulta:
        print("La consulta no puede estar vacía.")
        return

    resultado = construir_agente().invoke({"entrada": consulta})

    print("\nTraza de herramientas:")
    pasos = resultado["intermediate_steps"]
    if not pasos:
        print("No se usaron herramientas.")
    for numero, (accion, observacion) in enumerate(pasos, start=1):
        print(f"{numero}. {accion.tool}: {observacion}")

    print("\nRespuesta:")
    texto = extraer_texto_respuesta(resultado["output"])
    print(texto or "No se recibió una respuesta de texto.")


if __name__ == "__main__":
    try:
        main()
    except ValueError as error:
        if not os.getenv("GEMINI_API_KEY"):
            print("Falta configurar GEMINI_API_KEY en el archivo .env.")
        else:
            print(f"No se pudo completar la consulta ({type(error).__name__}).")
        raise SystemExit(1)
    except Exception as error:
        print(f"No se pudo completar la consulta ({type(error).__name__}).")
        raise SystemExit(1)