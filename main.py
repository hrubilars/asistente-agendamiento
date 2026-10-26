import json
from time import perf_counter

from cliente import consultar_modelo
from src.consumir_gemini import (
    cargar_datos_profesional,
    crear_instrucciones_sistema,
    parsear_respuesta_json,
)


def main():
    """Ejecuta el asistente utilizando el cliente modular."""

    try:
        # Construir las instrucciones a partir del catálogo del profesional.
        profesional = cargar_datos_profesional()
        instrucciones = crear_instrucciones_sistema(profesional)

        print("Asistente de atención y solicitudes de hora")
        print("Esta versión no confirma ni registra reservas.\n")

        consulta = input("Escribe tu consulta: ")

        # El cliente se encarga del envío y de los reintentos.
        inicio = perf_counter()
        texto = consultar_modelo(
            pregunta=consulta,
            system_instruction=instrucciones,
        )
        duracion = perf_counter() - inicio

        # Verificar la estructura antes de mostrar la respuesta.
        respuesta = parsear_respuesta_json(texto)

        print(
            f"\nTiempo total de consulta: {duracion:.2f} segundos"
        )
        print("\nJSON validado:")
        print(json.dumps(
            respuesta,
            indent=2,
            ensure_ascii=False,
        ))

    except (ValueError, RuntimeError) as error:
        # Mostrar los errores controlados con un mensaje comprensible.
        print("No se pudo completar la operación:", error)


if __name__ == "__main__":
    main()