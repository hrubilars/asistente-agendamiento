import random
import time
from typing import Any, Callable

from src.consumir_gemini import (
    armar_peticion,
    calcular_costo,
    enviar_peticion,
    extraer_texto,
)

# Tarifas por millón configuradas actualmente en el proyecto.
# Son referenciales y deben revisarse si cambian los precios del proveedor.
TARIFAS_MODELOS = {
    "gemini-3.5-flash-lite": {
        "entrada": 0.30 / 1_000_000,
        "salida": 2.50 / 1_000_000,
    },
}

# Se reinicia cada vez que se inicia nuevamente el programa.
costo_total_sesion = 0.0

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

        except TimeoutError as error:
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

            # Mostrar el motivo permite identificar el código HTTP observado.
            print(
                f"Intento {intento} de {intentos} falló: {error}. "
                f"Reintentando en {espera_con_jitter:.2f} segundos..."
            )

            time.sleep(espera_con_jitter)


def registrar_costo(datos: dict, modelo: str) -> float | None:
    """Calcula y acumula el costo estimado de una consulta."""

    global costo_total_sesion

    # Evitar aplicar la tarifa de un modelo a otro distinto.
    tarifas = TARIFAS_MODELOS.get(modelo)

    if tarifas is None:
        print(
            f"Costo estimado no disponible: "
            f"no hay tarifas configuradas para {modelo}."
        )
        return None

    try:
        # Reutilizar el cálculo de entrada, salida y razonamiento.
        costo = calcular_costo(
            datos,
            precio_entrada=tarifas["entrada"],
            precio_salida=tarifas["salida"],
        )
    except (RuntimeError, TypeError):
        # La consulta puede responder aunque falten datos de uso.
        print(
            "Costo estimado no disponible: "
            "la respuesta no contiene datos de uso suficientes."
        )
        return None

    costo_total_sesion += costo

    print(f"Costo estimado de la operación: ${costo:.6f} USD")
    print(f"Costo acumulado de la sesión: ${costo_total_sesion:.6f} USD")

    return costo

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

    # Registrar el uso después de recibir la respuesta de la API.
    registrar_costo(datos, modelo)

    # Extraer el texto después de recibir una respuesta exitosa.
    return extraer_texto(datos)