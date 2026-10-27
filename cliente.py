import random
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
    espera_base: float = 2,
    espera_maxima: float = 30,
) -> Any:
    """Ejecuta una operación con reintentos ante errores temporales."""

    # Evitar configuraciones que impidan ejecutar la operación.
    if intentos < 1:
        raise ValueError("La cantidad de intentos debe ser al menos 1.")

    if espera_base < 0 or espera_maxima < 0:
        raise ValueError("Los tiempos de espera no pueden ser negativos.")

    for intento in range(1, intentos + 1):
        try:
            # Si la operación funciona, devolver el resultado de inmediato.
            return funcion()

        except TimeoutError:
            # En el último intento se propaga el error sin esperar otra vez.
            if intento == intentos:
                raise

            # La espera crece exponencialmente: 2, 4, 8... segundos.
            espera = min(
                espera_base * (2 ** (intento - 1)),
                espera_maxima,
            )

            # Agregar una variación aleatoria y respetar la espera máxima.
            jitter = random.uniform(0, espera * 0.1)
            espera_con_jitter = min(espera + jitter, espera_maxima)

            print(
                f"Intento {intento} de {intentos} falló por un "
                f"problema temporal. Reintentando en "
                f"{espera_con_jitter:.2f} segundos..."
            )

            time.sleep(espera_con_jitter)


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