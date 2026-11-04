import json

from langchain_core.runnables import RunnableLambda

from cadena_tres_pasos import componer_cadena


def test_cadena_conserva_consulta_y_valida_resultado():
    consulta = "¿Cuánto cuesta la sesión familiar?"
    analisis = "La persona pregunta por el precio de la sesión familiar."
    borrador = "La sesión familiar cuesta $55.000 CLP."
    esperado = {
        "respuesta": borrador,
        "requiere_contacto_profesional": False,
        "reserva_confirmada": False,
    }

    def interpretar(datos):
        assert datos["consulta"] == consulta
        return analisis

    def orientar(datos):
        # La segunda etapa necesita tanto la consulta como su interpretación.
        assert datos["consulta"] == consulta
        assert datos["analisis"] == analisis
        return borrador

    def finalizar(datos):
        assert consulta in datos["consulta"]
        assert borrador in datos["consulta"]
        return json.dumps(esperado, ensure_ascii=False)

    cadena = componer_cadena(
        RunnableLambda(interpretar),
        RunnableLambda(orientar),
        RunnableLambda(finalizar),
    )

    assert cadena.invoke({"consulta": consulta}) == esperado