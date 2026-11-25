"""Funciones para instrumentar el flujo RAG del asistente."""

import argparse
import json
import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from indexar_corpus import INDICE, RAIZ
from recuperar_corpus import abrir_indice

from datetime import datetime, timezone

from langchain_core.output_parsers import StrOutputParser

from cadena_asistente import MODELO
from cliente import TARIFAS_MODELOS
from recuperar_corpus import formatear_contexto, recuperar_fragmentos
from responder_corpus import SIN_INFORMACION, construir_prompt, validar_citas

from contextlib import contextmanager
from time import perf_counter

import logging

from logging_rag import (
    configurar_logger,
    contexto_consulta,
    generar_huella,
    registrar_evento,
)

from seguridad_rag import (
    filtrar_documentos_sospechosos,
    validar_pregunta_segura,
)


@contextmanager
def medir(tiempos, etapa):
    """Guarda en segundos cuánto demora el bloque dentro de with."""
    # Antes de ejecutar el bloque, tomamos una lectura del reloj.
    inicio = perf_counter()

    try:
        # Cede el control al código que queremos medir.
        # No crea hilos ni ejecuta operaciones en paralelo.
        yield
    finally:
        # También registramos el tiempo si el bloque termina con error.
        # Ese error sigue propagándose: medir() no lo oculta.
        tiempos[etapa] = perf_counter() - inicio


def calcular_costo_consulta(uso, tarifas):
    """Estima el costo de generación con tokens reportados por LangChain.

    Las tarifas deben estar expresadas en USD por token,
    igual que en TARIFAS_MODELOS de cliente.py.
    """
    # Si falta el consumo o la tarifa, desconocemos el costo.
    # Devolver None evita confundir "sin información" con "gratis".
    if not uso or not tarifas:
        return None

    entrada = uso.get("input_tokens")
    salida = uso.get("output_tokens")

    # No sustituimos un consumo desconocido por cero.
    # type(...) is int también rechaza booleanos como True.
    if any(type(valor) is not int or valor < 0 for valor in (entrada, salida)):
        return None

    # Usamos los contadores normalizados de LangChain.
    # No sumamos nuevamente detalles de razonamiento a output_tokens.
    return (
        entrada * tarifas["entrada"]
        + salida * tarifas["salida"]
    )

def _registrar_consulta(almacen, modelo, pregunta, k=2, nombre_modelo=MODELO):
    """Ejecuta el RAG y devuelve su respuesta junto con tiempos y consumo."""
    # Revisamos la pregunta antes de recuperar documentos o generar.
    # registrar_consulta() capturará el error y registrará únicamente
    # su tipo, conservando el trace_id sin copiar la pregunta al log.
    pregunta = validar_pregunta_segura(pregunta)
    if type(k) is not int or k < 1:
        raise ValueError("k debe ser un entero mayor o igual a 1.")

    tiempos = {}
    inicio_total = perf_counter()
    timestamp = datetime.now(timezone.utc).isoformat()

    # Etapa 1: Gemini genera el embedding de la pregunta y Chroma
    # busca los fragmentos localmente. No recalculamos el corpus.
    # Registramos el inicio antes de llamar al recuperador.
    # Si falla, el log permitirá identificar la etapa pendiente.
    registrar_evento("recuperacion_iniciada", k=k)

    with medir(tiempos, "embed_y_busqueda"):
        fragmentos = recuperar_fragmentos(almacen, pregunta, k=k)

    # Guardamos cantidades y tiempo, sin copiar los documentos al log.
    registrar_evento(
        "recuperacion_finalizada",
        fragmentos_recuperados=len(fragmentos),
        tiempo_ms=round(tiempos["embed_y_busqueda"] * 1000, 2),
    )

    # Filtramos antes de numerar: así ninguna cita puede apuntar
    # a un documento que decidimos excluir del contexto.
    fragmentos_aceptados, fragmentos_descartados = (
        filtrar_documentos_sospechosos(fragmentos)
    )

    # Registramos cantidades, sin guardar textos ni instrucciones
    # sospechosas en los logs operativos.
    registrar_evento(
        "documentos_filtrados",
        aceptados=len(fragmentos_aceptados),
        descartados=len(fragmentos_descartados),
    )

    respuesta = SIN_INFORMACION
    fuentes = {}
    uso = None

    # Si no hay fragmentos, conservamos la abstención del asistente
    # y evitamos una llamada innecesaria al modelo generativo.
    tiempos["armado_prompt"] = 0.0
    tiempos["generacion"] = 0.0
    generacion_ejecutada = False
    costo_generacion = 0.0

    # Solo generamos si queda evidencia después del filtro.
    if fragmentos_aceptados:
        # Etapa 2: reutilizamos el contexto numerado y el mismo prompt.
        # Las reglas del sistema siguen separadas de la consulta.
        with medir(tiempos, "armado_prompt"):
            # Reconstruimos numeración y fuentes solo con los aceptados.
            contexto, mapa_citas = formatear_contexto(fragmentos_aceptados)
            prompt = construir_prompt().invoke({
                "pregunta": pregunta,
                "contexto": contexto,
            })

        # El contenido del prompt no se escribe en el log.
        # Registramos su contexto como longitud y cantidad de fuentes.
        registrar_evento(
            "prompt_preparado",
            contexto_len=len(contexto),
            fuentes_disponibles=len(mapa_citas),
            tiempo_ms=round(tiempos["armado_prompt"] * 1000, 2),
        )

        # Etapa 3: conservamos el mensaje completo, incluidos los tokens.
        # Si encadenáramos directamente StrOutputParser, solo quedaría texto.
        # Este evento indica que estamos a punto de llamar al modelo.
        registrar_evento(
            "generacion_iniciada",
            modelo=nombre_modelo,
        )

        with medir(tiempos, "generacion"):
            mensaje = modelo.invoke(prompt)

        # Recibir un mensaje no significa que su contenido ya sea válido.
        # La extracción del texto y la validación de citas siguen después.
        registrar_evento(
            "generacion_finalizada",
            tiempo_ms=round(tiempos["generacion"] * 1000, 2),
        )
        generacion_ejecutada = True
        metadata_uso = getattr(mensaje, "usage_metadata", None)
        uso = dict(metadata_uso) if metadata_uso else None

        # Extraemos texto sin asumir que content siempre es una cadena.
        respuesta = StrOutputParser().invoke(mensaje).strip()
        if not respuesta:
            raise ValueError("El modelo devolvió una respuesta vacía.")

        # Conservamos la validación existente:
        # las citas deben corresponder a los fragmentos recuperados.
        fuentes = validar_citas(respuesta, mapa_citas)

        costo_generacion = calcular_costo_consulta(
            uso,
            TARIFAS_MODELOS.get(nombre_modelo),
        )

    # Medimos el tiempo total por separado: también incluye extracción
    # del texto y validación. Puede superar la suma de las tres etapas.
    tiempo_total = perf_counter() - inicio_total

    return {
        "timestamp": timestamp,
        "pregunta": pregunta,
        "modelo_solicitado": nombre_modelo,
        "k": k,
        "fragmentos_recuperados": len(fragmentos),
        "fragmentos_aceptados": len(fragmentos_aceptados),
        "fragmentos_descartados": len(fragmentos_descartados),
        "ids_recuperados": [doc.id for doc in fragmentos],
        "respuesta": respuesta,
        "fuentes_citadas": fuentes,
        "abstencion": respuesta == SIN_INFORMACION,
        "generacion_ejecutada": generacion_ejecutada,
        "tiempos_ms": {
            etapa: round(segundos * 1000, 2)
            for etapa, segundos in tiempos.items()
        },
        "tiempo_total_ms": round(tiempo_total * 1000, 2),
        "tokens": uso,
        "costo_generacion_estimado_usd": costo_generacion,
        # Los tokens del mensaje corresponden a generación, no al
        # embedding de la pregunta. No inventamos ese consumo ni su costo.
        "costo_embedding_estimado_usd": None,
    }

def registrar_consulta(almacen, modelo, pregunta, k=2, nombre_modelo=MODELO):
    """Ejecuta una consulta y correlaciona sus eventos de logging."""
    # Validamos antes de registrar datos de la consulta.
    if not isinstance(pregunta, str) or not pregunta.strip():
        raise ValueError("La pregunta debe ser un texto no vacío.")

    if type(k) is not int or k < 1:
        raise ValueError("k debe ser un entero mayor o igual a 1.")

    pregunta = pregunta.strip()

    # Todos los eventos emitidos dentro de este bloque comparten trace_id.
    # Al salir, el contexto se restaura incluso si ocurre un error.
    with contexto_consulta() as identificador:
        registrar_evento(
            "consulta_iniciada",
            pregunta_len=len(pregunta),
            pregunta_huella=generar_huella(pregunta),
            k=k,
        )

        try:
            # Reutilizamos la implementación que ya funciona:
            # recuperación, prompt, generación, citas y medición de consumo.
            registro = _registrar_consulta(
                almacen,
                modelo,
                pregunta,
                k=k,
                nombre_modelo=nombre_modelo,
            )
        except Exception as error:
            # Guardamos el tipo de error, no su mensaje completo:
            # el mensaje podría contener datos de la petición.
            registrar_evento(
                "consulta_fallida",
                nivel=logging.ERROR,
                tipo_error=type(error).__name__,
            )
            raise

        # El identificador también queda en el resultado para relacionarlo
        # con los eventos operativos de esta consulta.
        registro["trace_id"] = identificador

        if registro["generacion_ejecutada"]:
            uso = registro["tokens"] or {}

            registrar_evento(
                "consumo_llm",
                modelo=nombre_modelo,
                input_tokens=uso.get("input_tokens"),
                output_tokens=uso.get("output_tokens"),
                total_tokens=uso.get("total_tokens"),
                costo_generacion_estimado_usd=registro[
                    "costo_generacion_estimado_usd"
                ],
            )
        else:
            # La abstención sin generación no debe aparentar una llamada
            # al modelo ni un consumo de tokens observado.
            registrar_evento(
                "generacion_omitida",
                motivo="sin_fragmentos_utilizables",
            )

        registrar_evento(
            "consulta_finalizada",
            fragmentos_recuperados=registro["fragmentos_recuperados"],
            fuentes_citadas=len(registro["fuentes_citadas"]),
            abstencion=registro["abstencion"],
            tiempo_total_ms=registro["tiempo_total_ms"],
        )

        return registro


def guardar_registro(registro):
    """Agrega una consulta al archivo JSONL sin borrar las anteriores."""
    carpeta = RAIZ / "docs" / "evaluaciones"
    carpeta.mkdir(parents=True, exist_ok=True)
    archivo = carpeta / "registros_latencia_costo.jsonl"

    # Cada línea contiene un objeto JSON completo e independiente.
    # "a" significa agregar al final, sin sobrescribir otras corridas.
    with archivo.open("a", encoding="utf-8") as salida:
        salida.write(json.dumps(registro, ensure_ascii=False) + "\n")

    return archivo


def main():
    """Ejecuta una consulta real y guarda su respuesta, tiempos y consumo."""
    parser = argparse.ArgumentParser(
        description="Registra la latencia y el consumo del asistente RAG."
    )
    parser.add_argument("pregunta")
    parser.add_argument("--k", type=int, default=2)
    args = parser.parse_args()

    pregunta = args.pregunta.strip()
    if not pregunta or args.k < 1:
        parser.error("Escribe una pregunta y usa un --k mayor o igual a 1.")

    # Revisamos los requisitos locales antes de llamar al proveedor.
    if not (INDICE / "chroma.sqlite3").is_file():
        raise SystemExit("No encontré el índice local en vectorstore/.")

    load_dotenv(RAIZ / ".env")
    clave = os.getenv("GEMINI_API_KEY")
    if not clave:
        raise SystemExit("Falta GEMINI_API_KEY en el archivo .env.")

    # Los logs operativos se guardan en la carpeta excluida de Git.
    configurar_logger(archivo=RAIZ / "logs" / "rag.jsonl")

    try:
        almacen = abrir_indice(clave)
        modelo = ChatGoogleGenerativeAI(
            model=MODELO,
            api_key=clave,
            vertexai=False,
            timeout=90,
            max_retries=0,
        )

        # Este paso sí hace las llamadas reales:
        # embedding de la pregunta y generación con el contexto recuperado.
        registro = registrar_consulta(
            almacen,
            modelo,
            pregunta,
            k=args.k,
            nombre_modelo=MODELO,
        )
    except Exception as error:
        # No imprimimos la petición ni detalles que puedan contener la clave.
        # Una operación fallida no se guarda como una consulta exitosa.
        raise SystemExit(
            f"No se completó la consulta ({type(error).__name__}). "
            "Revisa la conexión, la cuota o la configuración."
        ) from None

    # La consulta ya terminó. Distinguimos un fallo de escritura
    # de un fallo del proveedor, porque no conviene repetirla innecesariamente.
    try:
        archivo = guardar_registro(registro)
    except OSError:
        print(json.dumps(registro, ensure_ascii=False, indent=2))
        raise SystemExit(
            "La consulta terminó, pero no se pudo guardar el registro. "
            "Conserva la salida y revisa los permisos de docs/evaluaciones/."
        ) from None

    print(json.dumps(registro, ensure_ascii=False, indent=2))
    print(f"\nRegistro guardado en: {archivo}")


# Importar este módulo para una prueba no ejecuta consultas.
if __name__ == "__main__":
    main()
