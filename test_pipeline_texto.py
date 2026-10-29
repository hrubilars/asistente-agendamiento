import pytest

from pipeline_texto import procesar_texto, vectorizar


def test_procesar_texto_normaliza_mayusculas_y_puntuacion():
    """Normaliza una frase relacionada con nuestro proyecto."""
    resultado = procesar_texto("  ¡La SESIÓN familiar, dura 60 minutos!  ")

    assert resultado == [
        "la", "sesión", "familiar", "dura", "60", "minutos"
    ]


def test_procesar_texto_solo_puntuacion_devuelve_lista_vacia():
    """La puntuación por sí sola no produce palabras."""
    assert procesar_texto("¡¡¡...!!!") == []


def test_procesar_texto_conserva_tildes_y_enie():
    """Evita perder caracteres propios del español."""
    assert procesar_texto("¡Sesión para NIÑOS!") == [
        "sesión", "para", "niños"
    ]


def test_procesar_texto_rechaza_entrada_no_textual():
    """Un objeto de otro tipo produce un error comprensible."""
    with pytest.raises(TypeError):
        procesar_texto(None)


def test_vectorizar_cuenta_repeticiones():
    """Comprueba que el conteo conserva las palabras repetidas."""
    resultado = vectorizar(["sesión", "familiar", "sesión"])

    assert resultado == {"sesión": 2, "familiar": 1}