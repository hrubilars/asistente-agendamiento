"""Verifica el registro de consumo sin llamadas a Gemini."""

from unittest.mock import Mock

import pytest
from langchain_core.documents import Document
from langchain_core.messages import AIMessage

import registro_rag as rag


@pytest.mark.parametrize(
    "respuesta, mensaje_error",
    [
        ("La sesión familiar cuesta $55.000 CLP [99].", "no se recuperó"),
        ("", "respuesta vacía"),
        ("La sesión familiar cuesta $55.000 CLP.", "sin citas"),
        ("La sesión familiar cuesta $55.000 CLP [1].", None),
    ],
)
def test_registra_consumo_antes_de_validar(
    monkeypatch, respuesta, mensaje_error
):
    """Cada generación registra consumo, incluso si se rechaza el texto."""
    documento = Document(
        page_content="La sesión familiar cuesta $55.000 CLP.",
        metadata={"fuente": "docs/corpus/sesion-familiar.md"},
    )

    # Simulamos recuperación y construcción del prompt.
    # No abrimos Chroma ni solicitamos embeddings.
    monkeypatch.setattr(
        rag,
        "recuperar_fragmentos",
        Mock(return_value=[documento]),
    )
    monkeypatch.setattr(
        rag,
        "formatear_contexto",
        Mock(
            return_value=(
                "[1] La sesión familiar cuesta $55.000 CLP.",
                {1: "docs/corpus/sesion-familiar.md"},
            )
        ),
    )
    plantilla = Mock()
    plantilla.invoke.return_value = "Prompt simulado"
    monkeypatch.setattr(rag, "construir_prompt", Mock(return_value=plantilla))

    # El modelo simulado devuelve contenido y consumo como lo haría
    # una respuesta real, pero sin conectarse al proveedor.
    modelo = Mock()
    modelo.invoke.return_value = AIMessage(
        content=respuesta,
        usage_metadata={
            "input_tokens": 100,
            "output_tokens": 20,
            "total_tokens": 120,
        },
    )

    # Usamos tarifas de prueba conocidas para comprobar el cálculo.
    monkeypatch.setattr(
        rag,
        "TARIFAS_MODELOS",
        {
            "modelo-prueba": {
                "entrada": 0.000001,
                "salida": 0.000002,
            }
        },
    )

    # Capturamos los eventos en memoria: no escribimos archivos de logs.
    eventos = []

    def capturar_evento(evento, **datos):
        eventos.append((evento, datos))

    monkeypatch.setattr(rag, "registrar_evento", capturar_evento)

    if mensaje_error:
        with pytest.raises(ValueError, match=mensaje_error):
            rag.registrar_consulta(
                object(),
                modelo,
                "¿Cuánto cuesta la sesión familiar?",
                nombre_modelo="modelo-prueba",
            )
    else:
        registro = rag.registrar_consulta(
            object(),
            modelo,
            "¿Cuánto cuesta la sesión familiar?",
            nombre_modelo="modelo-prueba",
        )
        assert registro["tokens"]["total_tokens"] == 120

    # Cada generación debe producir exactamente un evento de consumo.
    consumos = [
        datos for evento, datos in eventos if evento == "consumo_llm"
    ]
    assert len(consumos) == 1
    assert consumos[0]["input_tokens"] == 100
    assert consumos[0]["output_tokens"] == 20
    assert consumos[0]["total_tokens"] == 120
    assert consumos[0]["costo_generacion_estimado_usd"] == pytest.approx(
        0.000140
    )
    modelo.invoke.assert_called_once()

    nombres = [evento for evento, _ in eventos]

    if mensaje_error:
        # El consumo debe aparecer antes del error de validación.
        assert nombres.index("consumo_llm") < nombres.index("consulta_fallida")
        assert "consulta_finalizada" not in nombres
    else:
        assert nombres.index("consumo_llm") < nombres.index("consulta_finalizada")
        assert "consulta_fallida" not in nombres