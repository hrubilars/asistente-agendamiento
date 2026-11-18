"""Funciones para instrumentar el flujo RAG del asistente."""

from contextlib import contextmanager
from time import perf_counter


@contextmanager
def medir(tiempos, etapa):
    """Guarda en segundos cuánto demora el bloque dentro de with."""
    # Antes de ejecutar el bloque, tomamos una lectura del reloj.
    inicio = perf_counter()

    try:
        # Cede el control al código que queremos medir.
        # No crea hilos ni ejecuta operaciones en paralelo.
        yield
    finally:
        # También registramos el tiempo si el bloque termina con error.
        # Ese error sigue propagándose: medir() no lo oculta.
        tiempos[etapa] = perf_counter() - inicio


def calcular_costo_consulta(uso, tarifas):
    """Estima el costo de generación con tokens reportados por LangChain.

    Las tarifas deben estar expresadas en USD por token,
    igual que en TARIFAS_MODELOS de cliente.py.
    """
    # Si falta el consumo o la tarifa, desconocemos el costo.
    # Devolver None evita confundir "sin información" con "gratis".
    if not uso or not tarifas:
        return None

    entrada = uso.get("input_tokens")
    salida = uso.get("output_tokens")

    # No sustituimos un consumo desconocido por cero.
    # type(...) is int también rechaza booleanos como True.
    if any(type(valor) is not int or valor < 0 for valor in (entrada, salida)):
        return None

    # Usamos los contadores normalizados de LangChain.
    # No sumamos nuevamente detalles de razonamiento a output_tokens.
    return (
        entrada * tarifas["entrada"]
        + salida * tarifas["salida"]
    )
