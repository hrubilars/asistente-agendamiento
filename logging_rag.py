"""Logging estructurado para las consultas del asistente RAG."""

import hashlib
import json
import logging
import sys
import uuid

from contextlib import contextmanager
from contextvars import ContextVar
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from pathlib import Path


# Cada contexto de ejecución mantiene su propio identificador.
# Esto evita usar una variable global compartida entre consultas.
trace_id_var = ContextVar("trace_id", default=None)

logger = logging.getLogger("asistente.rag")
logger.setLevel(logging.INFO)
logger.propagate = False


class JsonFormatter(logging.Formatter):
    """Convierte cada evento de logging en una línea JSON."""

    def format(self, record):
        # Registramos fecha UTC para poder comparar eventos
        # aunque el programa se ejecute en distintas zonas horarias.
        payload = {
            "timestamp": datetime.fromtimestamp(
                record.created,
                tz=timezone.utc,
            ).isoformat(),
            "nivel": record.levelname,
            "evento": record.getMessage(),
            "trace_id": trace_id_var.get(),
            "datos": getattr(record, "datos", {}),
        }

        return json.dumps(payload, ensure_ascii=False)


def configurar_logger(archivo=None, flujo=None):
    """Configura la salida a consola y, opcionalmente, a un archivo."""
    # Reconfigurar no debe acumular handlers: eso duplicaría los eventos.
    for handler in list(logger.handlers):
        logger.removeHandler(handler)
        handler.close()

    formato = JsonFormatter()

    consola = logging.StreamHandler(
        flujo if flujo is not None else sys.stdout
    )
    consola.setFormatter(formato)
    logger.addHandler(consola)

    if archivo is not None:
        ruta = Path(archivo)
        ruta.parent.mkdir(parents=True, exist_ok=True)

        # Al alcanzar aproximadamente 1 MB, rota el archivo.
        # Conserva hasta tres respaldos, además del archivo activo.
        archivo_handler = RotatingFileHandler(
            ruta,
            maxBytes=1_000_000,
            backupCount=3,
            encoding="utf-8",
        )
        archivo_handler.setFormatter(formato)
        logger.addHandler(archivo_handler)


def generar_huella(texto):
    """Genera una huella para comparar textos sin guardarlos completos."""
    # No es cifrado ni garantiza anonimización.
    # Permite reconocer cambios o repeticiones de un mismo texto.
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


@contextmanager
def contexto_consulta():
    """Asigna un trace_id y restaura el contexto al finalizar."""
    identificador = f"trace-{uuid.uuid4().hex}"
    token = trace_id_var.set(identificador)

    try:
        # Entregamos el identificador al código que ejecuta la consulta.
        yield identificador
    finally:
        # También se restaura si ocurre un error durante la consulta.
        trace_id_var.reset(token)


def registrar_evento(evento, nivel=logging.INFO, **datos):
    """Registra un evento con sus métricas y el trace_id activo."""
    # Los llamadores deben enviar solo datos necesarios:
    # conteos, tiempos, tokens y huellas.
    # No enviar preguntas, documentos, respuestas ni claves completas.
    logger.log(
        nivel,
        evento,
        extra={"datos": datos},
    )