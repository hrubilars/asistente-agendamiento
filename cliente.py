import time
from typing import Any, Callable


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