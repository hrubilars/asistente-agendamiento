import json
import unittest

from src.consumir_gemini import parsear_respuesta_json


def respuesta_base():
    return {
        "respuesta": "Debes contactar directamente al profesional.",
        "requiere_contacto_profesional": True,
        "reserva_confirmada": False,
    }


class TestValidacionJSON(unittest.TestCase):
    def test_acepta_respuesta_valida(self):
        esperado = respuesta_base()

        resultado = parsear_respuesta_json(
            json.dumps(esperado)
        )

        self.assertEqual(resultado, esperado)

    def test_rechaza_json_malformado(self):
        with self.assertRaises(ValueError):
            parsear_respuesta_json('{"respuesta":')

    def test_rechaza_lista_en_lugar_de_objeto(self):
        with self.assertRaises(ValueError):
            parsear_respuesta_json("[]")

    def test_rechaza_clave_faltante(self):
        datos = respuesta_base()
        del datos["requiere_contacto_profesional"]

        with self.assertRaises(ValueError):
            parsear_respuesta_json(json.dumps(datos))

    def test_rechaza_booleano_como_texto(self):
        datos = respuesta_base()
        datos["reserva_confirmada"] = "false"

        with self.assertRaises(ValueError):
            parsear_respuesta_json(json.dumps(datos))

    def test_rechaza_respuesta_vacia(self):
        datos = respuesta_base()
        datos["respuesta"] = "   "

        with self.assertRaises(ValueError):
            parsear_respuesta_json(json.dumps(datos))

    def test_rechaza_confirmacion_de_reserva(self):
        datos = respuesta_base()
        datos["reserva_confirmada"] = True

        with self.assertRaises(ValueError):
            parsear_respuesta_json(json.dumps(datos))


if __name__ == "__main__":
    unittest.main()