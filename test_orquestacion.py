from unittest.mock import Mock

from langchain_core.runnables import RunnableLambda

from enrutamiento import (
    construir_cadena_agendamiento_segura,
    construir_enrutador,
    procesar_mensaje_seguro,
)


def test_fallo_en_agendamiento_activa_respaldo(caplog):
    consulta = "¿Puedes confirmar una sesión familiar para mañana?"
    principal = Mock(side_effect=RuntimeError("Fallo simulado"))
    otra_ruta = Mock()

    # El clasificador simulado envía el mensaje a la ruta que va a fallar.
    enrutador = construir_enrutador(
        RunnableLambda(lambda _datos: " AGENDAMIENTO\n"),
        RunnableLambda(lambda datos: otra_ruta(datos)),
        construir_cadena_agendamiento_segura(
            RunnableLambda(lambda datos: principal(datos))
        ),
        RunnableLambda(lambda datos: otra_ruta(datos)),
    )

    resultado = enrutador.invoke({"consulta": consulta})

    principal.assert_called_once_with(
        {"consulta": consulta, "categoria": "agendamiento"}
    )
    otra_ruta.assert_not_called()
    assert resultado["requiere_contacto_profesional"] is True
    assert resultado["reserva_confirmada"] is False
    assert "contacta directamente al profesional" in resultado["respuesta"]
    assert "se activó el respaldo" in caplog.text

def test_fallo_en_clasificacion_devuelve_respuesta_segura(caplog):
    consulta = "¿Cuánto cuesta la sesión familiar?"
    clasificador = Mock(side_effect=RuntimeError("Fallo simulado"))
    ruta = Mock()
    ruta_simulada = RunnableLambda(lambda datos: ruta(datos))

    # El fallo ocurre antes de que el enrutador pueda elegir una ruta.
    asistente = construir_enrutador(
        RunnableLambda(lambda datos: clasificador(datos)),
        ruta_simulada,
        ruta_simulada,
        ruta_simulada,
    )

    resultado = procesar_mensaje_seguro(asistente, consulta)

    clasificador.assert_called_once_with({"consulta": consulta})
    ruta.assert_not_called()
    assert resultado["requiere_contacto_profesional"] is False
    assert resultado["reserva_confirmada"] is False
    assert "Intenta nuevamente más tarde" in resultado["respuesta"]
    assert "Falló la orquestación: RuntimeError" in caplog.text