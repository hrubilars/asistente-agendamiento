"""Verifica que la aprobación gobierna el prompt utilizado por el RAG."""

import hashlib
import json

import pytest

import responder_corpus

from grafo_supervision import construir_grafo
from langgraph.types import Command
from prompt_activo import aplicar_decision, cargar_version_activa


@pytest.mark.parametrize(
    "decision, esperada",
    [(True, 2), (False, 1)],
)
def test_decision_controla_prompt_del_rag(
    tmp_path,
    monkeypatch,
    decision,
    esperada,
):
    registro = tmp_path / "versiones.json"
    activo = tmp_path / "prompt_activo.json"

    # Construimos versiones ficticias para probar el mecanismo
    # sin depender de los textos reales de nuestro proyecto.
    versiones = []
    for numero in (1, 2):
        texto = f"Instrucciones de prueba, versión {numero}."
        versiones.append({
            "version": numero,
            "texto": texto,
            "huella": hashlib.sha256(texto.encode("utf-8")).hexdigest(),
        })

    registro.write_text(
        json.dumps(versiones),
        encoding="utf-8",
    )

    # Dejamos la versión 1 como selección inicial de esta prueba.
    aplicar_decision(
        {
            "aprobado": True,
            "version_propuesta": 1,
            "huella_propuesta": versiones[0]["huella"],
        },
        archivo_registro=registro,
        archivo_activo=activo,
    )

    grafo = construir_grafo()
    config = {
        "configurable": {
            "thread_id": f"activacion-{decision}"
        }
    }

    pausado = grafo.invoke(
        {
            "version_actual": 1,
            "version_propuesta": 2,
            "huella_propuesta": versiones[1]["huella"],
            "aprobado": False,
            "version_seleccionada": 1,
        },
        config=config,
    )

    assert "__interrupt__" in pausado

    # Mientras espera aprobación, la versión activa sigue siendo la 1.
    assert cargar_version_activa(registro, activo)["version"] == 1

    resultado = grafo.invoke(
        Command(resume=decision),
        config=config,
    )
    aplicar_decision(resultado, registro, activo)

    assert cargar_version_activa(registro, activo)["version"] == esperada

    # Conectamos el lector del asistente al archivo temporal.
    # Comprobamos el mensaje de sistema que realmente construye el RAG.
    monkeypatch.setattr(
        responder_corpus,
        "cargar_version_activa",
        lambda: cargar_version_activa(registro, activo),
    )

    mensajes = responder_corpus.construir_prompt().invoke({
        "pregunta": "Consulta de prueba.",
        "contexto": "Documento de prueba.",
    }).to_messages()

    assert mensajes[0].content == versiones[esperada - 1]["texto"]