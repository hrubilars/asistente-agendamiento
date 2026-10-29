import re
from collections import Counter


def limpiar_texto(texto: str) -> str:
    """Normaliza un texto para compararlo con otro."""

    if not isinstance(texto, str):
        raise TypeError("El texto debe ser una cadena de caracteres.")

    # Unificar mayúsculas y eliminar puntuación.
    # Se conservan números, letras acentuadas, ñ y guiones bajos.
    texto = texto.lower()
    texto = re.sub(r"[^\w\s]", "", texto)

    # Reducir espacios repetidos y quitar los de los extremos.
    return re.sub(r"\s+", " ", texto).strip()


def tokenizar(texto_limpio: str) -> list[str]:
    """Separa el texto limpio en palabras."""
    return texto_limpio.split()


def procesar_texto(texto: str) -> list[str]:
    """Combina limpieza y tokenización en una sola operación."""
    return tokenizar(limpiar_texto(texto))


def vectorizar(tokens: list[str]) -> Counter:
    """Cuenta las apariciones de cada palabra."""
    return Counter(tokens)