from unittest.mock import Mock, call, patch

import pytest

import cliente
from src.consumir_gemini import enviar_peticion


MODELO = "gemini-3.5-flash-lite"
URL_PRUEBA = "https://ejemplo.invalid"
CUERPO_PRUEBA = {"pregunta": "Consulta simulada"}


@pytest.fixture(autouse=True)
def reiniciar_costo_total(monkeypatch):
    """Evita que una prueba herede el acumulado de otra."""
    monkeypatch.setattr(cliente, "costo_total_sesion", 0.0)


@pytest.fixture
def respuesta_con_uso():
    """Entrega tokens conocidos para verificar el cálculo de costo."""
    return {
        "usageMetadata": {
            "promptTokenCount": 1000,
            "candidatesTokenCount": 100,
            "thoughtsTokenCount": 20,
        }
    }


# ENVÍO DE PETICIONES


@pytest.mark.parametrize("codigo", [401, 403])
def test_enviar_peticion_credencial_invalida(codigo):
    """Una credencial inválida o sin permisos produce ValueError."""
    respuesta = Mock()
    respuesta.status_code = codigo
    respuesta.headers = {}
    respuesta.json.return_value = {
        "error": {"message": "Acceso rechazado"}
    }

    # Sustituir la llamada HTTP en el módulo donde se utiliza.
    with patch(
        "src.consumir_gemini.requests.post",
        return_value=respuesta,
    ) as enviar:
        with pytest.raises(ValueError):
            enviar_peticion(URL_PRUEBA, CUERPO_PRUEBA)

    enviar.assert_called_once()


@pytest.mark.parametrize("codigo", [429, 503])
def test_enviar_peticion_error_temporal(codigo):
    """Los errores temporales se traducen a TimeoutError."""
    respuesta = Mock()
    respuesta.status_code = codigo
    respuesta.headers = {}
    respuesta.json.return_value = {
        "error": {"message": "Error temporal simulado"}
    }

    with patch(
        "src.consumir_gemini.requests.post",
        return_value=respuesta,
    ):
        with pytest.raises(TimeoutError, match=str(codigo)):
            enviar_peticion(URL_PRUEBA, CUERPO_PRUEBA)


def test_enviar_peticion_exito():
    """Una respuesta exitosa devuelve el diccionario recibido."""
    datos_esperados = {"texto": "Respuesta simulada"}
    respuesta = Mock()
    respuesta.status_code = 200
    respuesta.json.return_value = datos_esperados

    with patch(
        "src.consumir_gemini.requests.post",
        return_value=respuesta,
    ):
        resultado = enviar_peticion(URL_PRUEBA, CUERPO_PRUEBA)

    assert resultado == datos_esperados


# REINTENTOS


def test_con_reintento_recupera_operacion():
    """La operación puede recuperarse después de fallos temporales."""
    operacion = Mock(
        side_effect=[
            TimeoutError("Primer fallo"),
            TimeoutError("Segundo fallo"),
            "Respuesta recuperada",
        ]
    )

    # Fijar el jitter permite comprobar las esperas sin aleatoriedad.
    with patch("cliente.random.uniform", return_value=0):
        with patch("cliente.time.sleep") as dormir:
            resultado = cliente.con_reintento(operacion)

    assert resultado == "Respuesta recuperada"
    assert operacion.call_count == 3
    assert dormir.call_args_list == [call(2), call(4)]


def test_con_reintento_no_reintenta_value_error():
    """Los errores no temporales se propagan sin repetir ni esperar."""
    error_original = ValueError("Credencial inválida")
    operacion = Mock(side_effect=error_original)

    with patch("cliente.time.sleep") as dormir:
        with pytest.raises(ValueError) as error:
            cliente.con_reintento(operacion)

    assert error.value is error_original
    operacion.assert_called_once()
    dormir.assert_not_called()


def test_con_reintento_agota_intentos():
    """Al agotar los intentos se propaga el error original."""
    error_original = TimeoutError("Servicio no disponible")
    operacion = Mock(side_effect=error_original)

    with patch("cliente.time.sleep") as dormir:
        with pytest.raises(TimeoutError) as error:
            cliente.con_reintento(operacion, intentos=3)

    assert error.value is error_original
    assert operacion.call_count == 3
    assert dormir.call_count == 2


# REGISTRO DE COSTOS


def test_registrar_costo_calcula_valor_correcto(respuesta_con_uso):
    """Incluye entrada, salida y razonamiento en el cálculo."""
    costo = cliente.registrar_costo(respuesta_con_uso, MODELO)

    # Tarifas actualmente configuradas: entrada 0.30 y salida 2.50
    # USD por millón. Resultado: 0.000300 + 0.000300.
    assert costo == pytest.approx(0.000600)


def test_registrar_costo_acumula(respuesta_con_uso):
    """Dos operaciones incrementan el acumulado de la sesión."""
    cliente.registrar_costo(respuesta_con_uso, MODELO)
    cliente.registrar_costo(respuesta_con_uso, MODELO)

    assert cliente.costo_total_sesion == pytest.approx(0.001200)


# CONSULTA DEL MODELO


def test_consultar_modelo_convierte_error():
    """El agotamiento de reintentos se comunica como RuntimeError."""
    # Simular la construcción evita depender de una API key.
    with patch(
        "cliente.armar_peticion",
        return_value=(URL_PRUEBA, CUERPO_PRUEBA),
    ):
        with patch(
            "cliente.con_reintento",
            side_effect=TimeoutError("Intentos agotados"),
        ):
            with pytest.raises(
                RuntimeError,
                match="El servicio no respondió tras varios intentos",
            ):
                cliente.consultar_modelo("Consulta de prueba")


def test_consultar_modelo_propaga_value_error():
    """Una credencial inválida conserva su excepción original."""
    error_original = ValueError("Credencial inválida")

    with patch(
        "cliente.armar_peticion",
        return_value=(URL_PRUEBA, CUERPO_PRUEBA),
    ):
        with patch(
            "cliente.con_reintento",
            side_effect=error_original,
        ):
            with pytest.raises(ValueError) as error:
                cliente.consultar_modelo("Consulta de prueba")

    assert error.value is error_original