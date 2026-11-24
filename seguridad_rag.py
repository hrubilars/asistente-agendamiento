"""Detección básica de intentos de inyección en textos del RAG."""

import re
import unicodedata


# Son señales de instrucciones sospechosas, no una lista de palabras
# prohibidas. Mencionar "reserva" o "cancelación" no implica un ataque.
PATRONES_SOSPECHOSOS = (
    r"\bignora(?:r)?\b.{0,60}\binstrucciones\b",
    r"\bolvida\b.{0,60}\binstrucciones\b",
    r"\bignore\b.{0,60}\binstructions\b",
    r"\brevela\b.{0,40}\bprompt\b",
    r"\breveal\b.{0,40}\b(?:prompt|instructions)\b",
    r"\bnuevo\s+(?:mensaje\s+de\s+)?sistema\s*:",
    r"\bsystem\s+override\b",
)


def normalizar_para_revision(texto):
    """Unifica mayúsculas, tildes y espacios para revisar patrones."""
    if not isinstance(texto, str):
        raise TypeError("El contenido que se revisa debe ser texto.")

    # Descompone letras acentuadas: "ó" se separa en letra y acento.
    descompuesto = unicodedata.normalize("NFD", texto.casefold())

    # Quitamos los acentos únicamente para detectar patrones.
    # El documento original se conserva intacto.
    sin_tildes = "".join(
        caracter
        for caracter in descompuesto
        if not unicodedata.combining(caracter)
    )

    # Así, los saltos de línea no impiden reconocer una misma frase.
    return " ".join(sin_tildes.split())


def detectar_inyeccion(texto):
    """Devuelve los patrones encontrados; una lista vacía indica sin señales."""
    normalizado = normalizar_para_revision(texto)

    return [
        patron
        for patron in PATRONES_SOSPECHOSOS
        if re.search(patron, normalizado)
    ]


def filtrar_documentos_sospechosos(documentos):
    """Separa documentos utilizables y documentos con señales de inyección."""
    limpios = []
    descartados = []

    for documento in documentos:
        # Nuestros fragmentos son objetos Document de LangChain:
        # page_content contiene el texto y metadata conserva la fuente.
        patrones = detectar_inyeccion(documento.page_content)

        if patrones:
            descartados.append(documento)
        else:
            limpios.append(documento)

    # Conservamos los objetos originales, incluidos sus IDs y metadatos.
    # Esta función no imprime ni registra el contenido de los documentos.
    return limpios, descartados