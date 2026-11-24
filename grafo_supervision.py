"""Supervisión humana para seleccionar una versión del prompt."""

import json
import uuid

from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from registro_prompts import ARCHIVO_REGISTRO


class EstadoSupervision(TypedDict):
    """Información compartida entre los nodos del grafo."""

    version_actual: int
    version_propuesta: int
    huella_propuesta: str
    aprobado: bool
    version_seleccionada: int


def solicitar_aprobacion(estado):
    """Pausa el flujo hasta recibir una decisión externa."""
    # interrupt() detiene el grafo y expone esta información
    # para que una persona pueda revisar la propuesta.
    decision = interrupt({
        "motivo": "Revisar una nueva versión del prompt del asistente.",
        "version_actual": estado["version_actual"],
        "version_propuesta": estado["version_propuesta"],
        "huella_propuesta": estado["huella_propuesta"],
    })

    # Este punto se alcanza cuando reanudamos con Command(resume=...).
    # No aceptamos textos como "false", porque no son booleanos.
    if type(decision) is not bool:
        raise ValueError("La decisión debe ser True o False.")

    return {"aprobado": decision}


def seleccionar_version(estado):
    """Selecciona la propuesta aprobada o conserva la versión anterior."""
    # Esta función solo puede ejecutarse después de resolver la pausa.
    if estado["aprobado"]:
        seleccionada = estado["version_propuesta"]
    else:
        seleccionada = estado["version_actual"]

    # Por ahora actualizamos únicamente el estado del grafo.
    # La conexión con el prompt del RAG será el siguiente paso.
    return {"version_seleccionada": seleccionada}


def construir_grafo():
    """Construye un flujo que puede pausarse y reanudarse."""
    grafo = StateGraph(EstadoSupervision)

    # Cada nodo representa una función del proceso.
    grafo.add_node("supervisar", solicitar_aprobacion)
    grafo.add_node("seleccionar", seleccionar_version)

    # Definimos el orden: inicio, aprobación, selección y final.
    grafo.add_edge(START, "supervisar")
    grafo.add_edge("supervisar", "seleccionar")
    grafo.add_edge("seleccionar", END)

    # El checkpointer conserva el estado mientras el proceso siga abierto.
    # Su memoria se pierde al terminar el programa.
    return grafo.compile(checkpointer=InMemorySaver())


def main():
    """Permite aprobar o rechazar una propuesta desde la terminal."""
    versiones = json.loads(
        ARCHIVO_REGISTRO.read_text(encoding="utf-8")
    )
    por_numero = {
        version["version"]: version
        for version in versiones
    }

    propuesta = por_numero[2]
    grafo = construir_grafo()

    # El mismo identificador debe acompañar la pausa y la reanudación.
    # Cada ejecución de este programa utiliza un identificador nuevo.
    config = {
        "configurable": {
            "thread_id": f"revision-{uuid.uuid4().hex}"
        }
    }

    estado_inicial = {
        "version_actual": 1,
        "version_propuesta": propuesta["version"],
        "huella_propuesta": propuesta["huella"],
        "aprobado": False,
        "version_seleccionada": 1,
    }

    pausado = grafo.invoke(estado_inicial, config=config)

    if "__interrupt__" not in pausado:
        raise RuntimeError("El grafo no se detuvo para pedir aprobación.")

    print("\nGrafo pausado. Propuesta pendiente:")
    print(json.dumps(
        pausado["__interrupt__"][0].value,
        ensure_ascii=False,
        indent=2,
    ))

    print("\nTexto propuesto:")
    print(propuesta["texto"])

    # Una entrada distinta de s/n no toma ninguna decisión.
    while True:
        respuesta = input("\n¿Apruebas esta versión? [s/n]: ").strip().lower()
        if respuesta in {"s", "n"}:
            break
        print("Escribe s para aprobar o n para rechazar.")

    # Reanudamos el mismo flujo con una decisión booleana.
    resultado = grafo.invoke(
        Command(resume=respuesta == "s"),
        config=config,
    )

    print("\nDecisión:", "aprobada" if resultado["aprobado"] else "rechazada")
    print("Versión seleccionada:", resultado["version_seleccionada"])
    print("El prompt del RAG todavía no se ha modificado.")


if __name__ == "__main__":
    main()