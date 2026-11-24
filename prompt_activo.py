"""Guarda y recupera la versión aprobada del prompt."""

import hashlib
import json

from pathlib import Path


RAIZ = Path(__file__).resolve().parent
REGISTRO = RAIZ / "docs" / "prompts" / "versiones.json"
ACTIVO = RAIZ / ".local" / "prompt_activo.json"


def leer_version(numero, archivo_registro=REGISTRO):
    """Busca una versión y comprueba que su texto conserva la huella."""
    versiones = json.loads(
        archivo_registro.read_text(encoding="utf-8")
    )

    coincidencias = [
        version
        for version in versiones
        if version["version"] == numero
    ]

    if len(coincidencias) != 1:
        raise ValueError("La versión no existe o está duplicada.")

    version = coincidencias[0]

    # No basta con confiar en el número de versión:
    # comprobamos que el texto corresponde a la huella registrada.
    huella_calculada = hashlib.sha256(
        version["texto"].encode("utf-8")
    ).hexdigest()

    if huella_calculada != version["huella"]:
        raise ValueError("El texto del prompt no coincide con su huella.")

    return version


def cargar_version_activa(
    archivo_registro=REGISTRO,
    archivo_activo=ACTIVO,
):
    """Devuelve la versión activa o None si todavía no se ha activado ninguna."""
    if not archivo_activo.exists():
        return None

    seleccion = json.loads(
        archivo_activo.read_text(encoding="utf-8")
    )
    version = leer_version(
        seleccion["version"],
        archivo_registro,
    )

    # Detectamos si el registro cambió después de la aprobación.
    if seleccion["huella"] != version["huella"]:
        raise ValueError("La versión activa cambió desde su aprobación.")

    return version


def aplicar_decision(
    resultado,
    archivo_registro=REGISTRO,
    archivo_activo=ACTIVO,
):
    """Activa la propuesta aprobada; un rechazo no modifica el archivo."""
    if type(resultado["aprobado"]) is not bool:
        raise ValueError("La aprobación debe ser un booleano.")

    if not resultado["aprobado"]:
        # Rechazar significa conservar la selección anterior.
        return

    version = leer_version(
        resultado["version_propuesta"],
        archivo_registro,
    )

    # Aprobamos exactamente el texto que se presentó a la persona.
    # Si alguien lo cambió durante la revisión, no lo activamos.
    if version["huella"] != resultado["huella_propuesta"]:
        raise ValueError("La propuesta cambió durante la revisión.")

    seleccion = {
        "version": version["version"],
        "huella": version["huella"],
    }

    archivo_activo.parent.mkdir(parents=True, exist_ok=True)

    # Escribimos primero un archivo temporal y después lo reemplazamos.
    # Así evitamos dejar una selección escrita parcialmente.
    temporal = archivo_activo.with_suffix(".tmp")
    temporal.write_text(
        json.dumps(seleccion, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporal.replace(archivo_activo)