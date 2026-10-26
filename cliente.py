import time
from typing import Any, Callable

from src.consumir_gemini import (
    armar_peticion,
    enviar_peticion,
    extraer_texto,
)

def con_reintento(
    funcion: Callable[[], Any],
    intentos: int = 3,
    espera_segundos: float = 2,
) -> Any:
    """Ejecuta una operación y reintenta únicamente ante TimeoutError."""

    # Evitar configuraciones que impidan ejecutar o esperar correctamente.
    if intentos < 1:
        raise ValueError("La cantidad de intentos debe ser al menos 1.")

    if espera_segundos < 0:
        raise ValueError("La espera no puede ser negativa.")

    for intento in range(1, intentos + 1):
        try:
            # Si funciona, devolver el resultado y terminar inmediatamente.
            return funcion()

        except TimeoutError:
            # Propagar el error final sin realizar otra espera.
            if intento == intentos:
                raise

            print(
                f"Intento {intento} de {intentos} falló por un "
                "problema temporal. Reintentando..."
            )
            time.sleep(espera_segundos)


def consultar_modelo(
    pregunta: str,
    system_instruction: str = "",
    modelo: str = "gemini-3.5-flash-lite",
) -> str:
    """Consulta el modelo con reintentos y devuelve el texto generado."""

    # Reutilizar el módulo existente para construir la petición.
    url, body = armar_peticion(
        pregunta,
        modelo=modelo,
        system_instruction=system_instruction,
    )

    try:
        # Reintentar solo el envío, conservando la misma petición.
        datos = con_reintento(
            lambda: enviar_peticion(url, body)
        )
    except TimeoutError:
        # Entregar un mensaje claro cuando se agotan los intentos.
        raise RuntimeError(
            "El servicio no respondió tras varios intentos. "
            "Intenta más tarde."
        ) from None

    # Extraer el texto después de recibir una respuesta exitosa.
    return extraer_texto(datos)