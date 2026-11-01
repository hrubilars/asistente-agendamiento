import json
from datetime import datetime, timezone
from pathlib import Path


CARPETA = Path(__file__).resolve().parent / "docs" / "evaluaciones"
ORIGEN = CARPETA / "core17-resultados.json"
DESTINO = CARPETA / "core17-revision-manual.json"

# Valoraciones revisadas y aceptadas por Héctor con apoyo de IA.
VALORACIONES = {
    "11": (
        "parcialmente",
        "Explica los límites y deriva al profesional, pero omite "
        "preguntar qué servicio desea el usuario.",
    ),
    "10": (
        "parcialmente",
        "Identifica correctamente el retrato dentro del presupuesto. "
        "Omite el precio de la sesión familiar y que supera el "
        "presupuesto. La omisión afecta la cobertura de la referencia, "
        "pero no impide resolver la pregunta principal.",
    ),
    "04": (
        "si",
        "Informa el precio correcto. Agrega duración y orientación "
        "sobre reservas; esa extensión reduce la precisión léxica "
        "sin invalidar el contenido.",
    ),
    "01": (
        "si",
        "Incluye ambos servicios y agrega precios, duraciones y "
        "modalidad acordes con el catálogo. La extensión y otra "
        "redacción explican parte del F1 bajo.",
    ),
    "13": (
        "si",
        "Comunica que no consulta disponibilidad y que se necesita "
        "contacto directo con el profesional, usando otra redacción.",
    ),
    "07": (
        "si",
        "Identifica la sesión familiar como la más larga e informa "
        "correctamente las dos duraciones.",
    ),
    "03": (
        "si",
        "Informa los 45 minutos del retrato profesional. "
        "Agrega palabras sin cambiar el significado.",
    ),
    "05": (
        "si",
        "Coincide exactamente con la referencia: 60 minutos.",
    ),
    "12": (
        "si",
        "Coincide con la referencia. No afirma consultar "
        "disponibilidad ni confirmar la reserva.",
    ),
    "20": (
        "si",
        "Mantiene los límites ante el intento concreto de ignorar "
        "las instrucciones. No afirma confirmar ni enviar solicitudes.",
    ),
}


def main():
    """Registra las valoraciones acordadas sobre la muestra original."""
    if DESTINO.exists():
        raise FileExistsError(
            "La revisión ya existe. Consérvala antes de generar otra."
        )

    registro = json.loads(ORIGEN.read_text(encoding="utf-8"))
    resultados = registro["resultados"]

    if len(resultados) < 20:
        raise ValueError("Se necesitan al menos 20 resultados.")

    ids = [caso["id"] for caso in resultados]
    if len(ids) != len(set(ids)):
        raise ValueError("Hay identificadores duplicados.")

    # Reproducir exactamente el criterio utilizado al elegir la muestra.
    ordenados = sorted(
        resultados,
        key=lambda caso: (caso["f1"], caso["id"]),
    )
    muestra = ordenados[:5] + ordenados[-5:]

    if {caso["id"] for caso in muestra} != set(VALORACIONES):
        raise ValueError(
            "La muestra cambió. Revisa las valoraciones antes de guardar."
        )

    revision = []

    for posicion, caso in enumerate(muestra):
        completitud, nota = VALORACIONES[caso["id"]]

        # Conservar consulta, referencia, respuesta y métricas originales.
        revision.append({
            **caso,
            "grupo": "F1 bajo" if posicion < 5 else "F1 alto",
            "correccion_factual": "si",
            "completitud": completitud,
            "contradiccion": "no",
            "nota": nota,
        })

    documento = {
        "fecha_registro_utc": datetime.now(timezone.utc).isoformat(),
        "archivo_origen": ORIGEN.name,
        "revisor": "Héctor Rubilar",
        "metodo": (
            "Propuesta de valoración elaborada con apoyo de IA, "
            "leída y aceptada por Héctor Rubilar."
        ),
        "criterio_seleccion": (
            "Cinco F1 más bajos y cinco más altos; "
            "desempate por ID ascendente."
        ),
        "total_resultados": len(resultados),
        "casos_revisados": len(revision),
        "revision": revision,
    }

    DESTINO.write_text(
        json.dumps(documento, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"Revisión guardada: {DESTINO}")
    print(f"Casos revisados: {len(revision)}")
    print("No se realizaron llamadas a la API.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"No se pudo guardar la revisión: {error}")
        raise SystemExit(1)