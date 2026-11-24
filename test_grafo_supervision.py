"""Pruebas de aprobación y rechazo mediante LangGraph."""

import pytest

from langgraph.types import Command

from grafo_supervision import construir_grafo


@pytest.mark.parametrize(
    "decision, version_esperada",
    [
        (True, 2),
        (False, 1),
    ],
)
def test_pausa_y_resuelve_segun_decision(decision, version_esperada):
    grafo = construir_grafo()

    # Aprobación y rechazo utilizan identificadores distintos.
    config = {
        "configurable": {
            "thread_id": f"prueba-{decision}"
        }
    }
    estado = {
        "version_actual": 1,
        "version_propuesta": 2,
        "huella_propuesta": "huella-simulada-para-prueba",
        "aprobado": False,
        "version_seleccionada": 1,
    }

    pausado = grafo.invoke(estado, config=config)

    # Antes de decidir, la propuesta no puede quedar seleccionada.
    assert "__interrupt__" in pausado
    assert pausado["version_seleccionada"] == 1

    final = grafo.invoke(
        Command(resume=decision),
        config=config,
    )

    assert final["aprobado"] is decision
    assert final["version_seleccionada"] == version_esperada

    # El flujo debe haber terminado, sin nodos pendientes.
    assert grafo.get_state(config).next == ()