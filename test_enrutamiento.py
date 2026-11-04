import pytest
from langchain_core.runnables import RunnableLambda

from enrutamiento import construir_enrutador


@pytest.mark.parametrize(
    ("etiqueta", "ruta_esperada"),
    [
        ("  CATALOGO\n", "catalogo"),
        (" Agendamiento ", "agendamiento"),
        ("general", "general"),
        ("etiqueta_desconocida", "general"),
    ],
)
def test_enrutador_ejecuta_solo_la_ruta_elegida(etiqueta, ruta_esperada):
    consulta = "Consulta de prueba"
    rutas_ejecutadas = []

    def clasificar(datos):
        assert datos["consulta"] == consulta
        return etiqueta

    def crear_ruta(nombre):
        def ejecutar(datos):
            # Cada ruta debe recibir el mensaje original.
            assert datos["consulta"] == consulta
            rutas_ejecutadas.append(nombre)
            return nombre

        return RunnableLambda(ejecutar)

    enrutador = construir_enrutador(
        RunnableLambda(clasificar),
        crear_ruta("catalogo"),
        crear_ruta("agendamiento"),
        crear_ruta("general"),
    )

    assert enrutador.invoke({"consulta": consulta}) == ruta_esperada
    assert rutas_ejecutadas == [ruta_esperada]