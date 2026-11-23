"""Prepara y valida ejemplos de clasificación para el asistente.

Este módulo no llama a una API ni entrena un modelo.
Los ejemplos son simulados y no contienen datos personales.
"""

import json
from collections import Counter


# Definimos un vocabulario fijo para que las etiquetas sean consistentes.
INTENCIONES = {
    "consultar_servicio",
    "consultar_politica",
    "solicitar_reserva",
    "gestionar_reserva",
}

CLAVES_ESPERADAS = {
    "intencion",
    "requiere_contacto_profesional",
}


# Cada ejemplo tiene dos partes:
# 1. Lo que podría escribir un cliente.
# 2. La clasificación exacta que queremos obtener.
#
# Hay tres ejemplos por categoría, para mantener el balance.
EJEMPLOS_RAW = [
    (
        "¿Qué servicios ofrecen?",
        {
            "intencion": "consultar_servicio",
            "requiere_contacto_profesional": False,
        },
    ),
    (
        "¿Cuánto cuesta la sesión familiar?",
        {
            "intencion": "consultar_servicio",
            "requiere_contacto_profesional": False,
        },
    ),
    (
        "¿Cuánto dura un retrato profesional?",
        {
            "intencion": "consultar_servicio",
            "requiere_contacto_profesional": False,
        },
    ),
    (
        "¿Con cuánta anticipación se debe cancelar?",
        {
            "intencion": "consultar_politica",
            "requiere_contacto_profesional": False,
        },
    ),
    (
        "¿Cómo se coordina el pago?",
        {
            "intencion": "consultar_politica",
            "requiere_contacto_profesional": False,
        },
    ),
    (
        "¿Las solicitudes necesitan confirmación del profesional?",
        {
            "intencion": "consultar_politica",
            "requiere_contacto_profesional": False,
        },
    ),
    (
        "Quiero reservar una sesión familiar para mañana.",
        {
            "intencion": "solicitar_reserva",
            "requiere_contacto_profesional": True,
        },
    ),
    (
        "¿Puedes agendarme un retrato el viernes?",
        {
            "intencion": "solicitar_reserva",
            "requiere_contacto_profesional": True,
        },
    ),
    (
        "Necesito una hora para la próxima semana.",
        {
            "intencion": "solicitar_reserva",
            "requiere_contacto_profesional": True,
        },
    ),
    (
        "Quiero cancelar una reserva existente.",
        {
            "intencion": "gestionar_reserva",
            "requiere_contacto_profesional": True,
        },
    ),
    (
        "Necesito cambiar la fecha de mi sesión.",
        {
            "intencion": "gestionar_reserva",
            "requiere_contacto_profesional": True,
        },
    ),
    (
        "¿Puedes modificar el horario de mi reserva?",
        {
            "intencion": "gestionar_reserva",
            "requiere_contacto_profesional": True,
        },
    ),
]


def construir_ejemplos(ejemplos_raw: list[tuple[str, dict]]) -> list[dict]:
    """Convierte los pares en entradas y salidas JSON."""
    # Conservamos el formato conceptual de la clase: text_input y output.
    # output es un texto JSON, no la representación de un diccionario.
    return [
        {
            "text_input": texto,
            "output": json.dumps(salida, ensure_ascii=False),
        }
        for texto, salida in ejemplos_raw
    ]


def chequear_balance(ejemplos_raw: list[tuple[str, dict]]) -> Counter:
    """Cuenta los ejemplos de cada intención."""
    # Counter devuelve algo como:
    # {"consultar_servicio": 3, "solicitar_reserva": 3, ...}
    return Counter(
        salida["intencion"]
        for _, salida in ejemplos_raw
    )


def validar_dataset(ejemplos: list[dict]) -> list[str]:
    """Detecta entradas vacías, duplicados y salidas incorrectas."""
    problemas = []
    vistos = set()

    for numero, ejemplo in enumerate(ejemplos, start=1):
        entrada = ejemplo.get("text_input")
        salida_json = ejemplo.get("output")

        # Normalizamos espacios y mayúsculas para detectar duplicados
        # aunque una misma consulta esté escrita con pequeñas diferencias.
        if not isinstance(entrada, str) or not entrada.strip():
            problemas.append(f"Ejemplo {numero}: entrada vacía o inválida.")
        else:
            entrada_normalizada = " ".join(entrada.casefold().split())

            if entrada_normalizada in vistos:
                problemas.append(f"Ejemplo {numero}: entrada duplicada.")

            vistos.add(entrada_normalizada)

        if not isinstance(salida_json, str) or not salida_json.strip():
            problemas.append(f"Ejemplo {numero}: salida vacía o inválida.")
            continue

        # Una salida puede parecer correcta y aun así tener JSON mal formado.
        try:
            salida = json.loads(salida_json)
        except json.JSONDecodeError:
            problemas.append(f"Ejemplo {numero}: salida no es JSON válido.")
            continue

        # Exigimos un objeto con exactamente los campos acordados.
        if not isinstance(salida, dict):
            problemas.append(f"Ejemplo {numero}: la salida debe ser un objeto.")
            continue

        if set(salida) != CLAVES_ESPERADAS:
            problemas.append(f"Ejemplo {numero}: claves incorrectas.")
            continue

        if salida["intencion"] not in INTENCIONES:
            problemas.append(f"Ejemplo {numero}: intención desconocida.")

        # "true" como texto no equivale al booleano True de Python.
        if type(salida["requiere_contacto_profesional"]) is not bool:
            problemas.append(f"Ejemplo {numero}: contacto debe ser booleano.")

    return problemas


def comprobar_validador(ejemplos: list[dict]) -> None:
    """Comprueba que el validador rechace tres errores deliberados."""
    # Creamos copias para mantener intacto el dataset válido.
    duplicados = [dict(ejemplo) for ejemplo in ejemplos]
    duplicados.append(dict(ejemplos[0]))

    claves_incompletas = [dict(ejemplo) for ejemplo in ejemplos]
    claves_incompletas[0]["output"] = json.dumps({
        "intencion": "consultar_servicio",
    })

    json_invalido = [dict(ejemplo) for ejemplo in ejemplos]
    json_invalido[0]["output"] = "{esto no es JSON}"

    pruebas = [
        ("Entrada duplicada", duplicados, "entrada duplicada"),
        ("Clave faltante", claves_incompletas, "claves incorrectas"),
        ("JSON malformado", json_invalido, "JSON válido"),
    ]

    for nombre, datos, mensaje_esperado in pruebas:
        problemas = validar_dataset(datos)

        # Verificamos el motivo del rechazo, no solo que exista algún error.
        if not any(mensaje_esperado in problema for problema in problemas):
            raise AssertionError(f"El validador no detectó: {nombre}")

        print(f"{nombre}: detectado correctamente")


def main() -> None:
    """Construye el dataset y ejecuta sus comprobaciones locales."""
    ejemplos = construir_ejemplos(EJEMPLOS_RAW)

    if len(ejemplos) < 10:
        raise ValueError("La actividad requiere al menos 10 ejemplos.")

    print(f"Ejemplos construidos: {len(ejemplos)}")

    print("\nBalance por intención:")
    for intencion, cantidad in chequear_balance(EJEMPLOS_RAW).items():
        print(f"- {intencion}: {cantidad}")

    problemas = validar_dataset(ejemplos)
    print(f"\nProblemas encontrados: {len(problemas)}")

    if problemas:
        for problema in problemas:
            print(f"- {problema}")
        raise SystemExit(1)

    print("\nComprobaciones con errores deliberados:")
    comprobar_validador(ejemplos)

    print("\nDataset preparado y validado, sin llamadas a la API.")


if __name__ == "__main__":
    main()