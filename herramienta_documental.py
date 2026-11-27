"""Herramienta que permite al agente consultar el RAG existente."""

import json

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from cadena_asistente import MODELO
from registro_rag import registrar_consulta
from seguridad_rag import validar_pregunta_segura


class ArgumentosConsultaDocumental(BaseModel):
    """Define el dato que el agente debe enviar a la herramienta."""

    pregunta: str = Field(
        min_length=1,
        description=(
            "Pregunta completa sobre los servicios o políticas del "
            "profesional. Incluye el servicio mencionado en la conversación "
            "para que pueda entenderse sin leer el historial."
        ),
    )


def crear_herramienta_documental(
    almacen,
    modelo,
    k=2,
    nombre_modelo=MODELO,
):
    """Construye la herramienta utilizando un índice y un modelo existentes."""
    if type(k) is not int or k < 1:
        raise ValueError("k debe ser un entero mayor o igual a 1.")

    def consultar_documentos(pregunta: str) -> str:
        """Responde sobre servicios y políticas usando fuentes documentales."""
        # Rechazamos señales conocidas de inyección antes de ejecutar el RAG.
        pregunta = validar_pregunta_segura(pregunta)

        # Reutilizamos el flujo instrumentado. No reconstruimos el índice
        # ni implementamos otro sistema de recuperación en este archivo.
        registro = registrar_consulta(
            almacen,
            modelo,
            pregunta,
            k=k,
            nombre_modelo=nombre_modelo,
        )

        # Entregamos la respuesta y sus fuentes, sin copiar al resultado
        # todos los detalles internos ni el texto completo de los documentos.
        resultado = {
            "respuesta": registro["respuesta"],
            "fuentes": registro["fuentes_citadas"],
            "sin_informacion": registro["abstencion"],
            "trace_id": registro["trace_id"],
        }

        return json.dumps(resultado, ensure_ascii=False)

    return StructuredTool.from_function(
        func=consultar_documentos,
        args_schema=ArgumentosConsultaDocumental,
        # El agente devolverá el resultado documental directamente.
        # Así evitamos una reformulación posterior que altere las citas.
        return_direct=True,
    )