import pytest

from metricas_texto import (
    calcular_metricas,
    calcular_precision_cobertura_f1,
    contar_coincidencias,
    resumir_metricas,
)


def test_contar_coincidencias_respeta_repeticiones():
    """Una repetición adicional no crea una coincidencia inexistente."""
    referencia = ["sesión", "sesión", "familiar"]
    respuesta = ["sesión", "familiar", "familiar"]

    assert contar_coincidencias(referencia, respuesta) == 2


def test_metricas_de_respuestas_identicas():
    resultado = calcular_metricas(
        "La sesión dura 60 minutos.",
        "La sesión dura 60 minutos.",
    )

    assert resultado == {
        "precision": 1.0,
        "cobertura": 1.0,
        "f1": 1.0,
    }


def test_metricas_de_coincidencia_parcial():
    """Comprueba las fórmulas con un resultado calculado a mano."""
    resultado = calcular_precision_cobertura_f1(
        ["sesión", "familiar"],
        ["sesión", "de", "fotos"],
    )

    assert resultado["precision"] == pytest.approx(1 / 3)
    assert resultado["cobertura"] == pytest.approx(1 / 2)
    assert resultado["f1"] == pytest.approx(0.4)


def test_metricas_sin_coincidencias():
    resultado = calcular_metricas("retrato profesional", "sesión familiar")

    assert resultado == {
        "precision": 0.0,
        "cobertura": 0.0,
        "f1": 0.0,
    }


@pytest.mark.parametrize(
    "referencia,respuesta",
    [
        ("", "Sesión familiar"),
        ("Sesión familiar", ""),
        ("¡¡¡...!!!", "???"),
    ],
)
def test_metricas_con_textos_vacios(referencia, respuesta):
    """Evita divisiones por cero, incluso después de limpiar el texto."""
    assert calcular_metricas(referencia, respuesta) == {
        "precision": 0.0,
        "cobertura": 0.0,
        "f1": 0.0,
    }


def test_calcular_metricas_normaliza_ambos_textos():
    resultado = calcular_metricas(
        "¡SESIÓN familiar!",
        "sesión familiar",
    )

    assert resultado["f1"] == 1.0


def test_resumir_metricas_calcula_promedios():
    resultados = [
        {"precision": 1.0, "cobertura": 1.0, "f1": 1.0},
        {"precision": 0.0, "cobertura": 0.0, "f1": 0.0},
    ]

    assert resumir_metricas(resultados) == {
        "precision_promedio": 0.5,
        "cobertura_promedio": 0.5,
        "f1_promedio": 0.5,
    }


def test_resumir_metricas_sin_resultados():
    assert resumir_metricas([]) == {
        "precision_promedio": 0.0,
        "cobertura_promedio": 0.0,
        "f1_promedio": 0.0,
    }