"""Evalúa qué fragmentos recupera el asistente para el banco del Bloque 27."""

import argparse
import os
from datetime import datetime, timezone
from statistics import mean

from dotenv import load_dotenv

from casos_recuperacion import CASOS
from indexar_corpus import COLECCION, INDICE, MODELO_EMBEDDINGS, RAIZ
from recuperar_corpus import abrir_indice, recuperar_fragmentos


def obtener_ids_por_fuente(almacen):
    """Relaciona las rutas del banco con los IDs del índice que estamos usando."""
    datos = almacen.get(include=["metadatas"])
    ids_por_fuente = {}

    for id_fragmento, metadata in zip(
        datos["ids"], datos["metadatas"], strict=True
    ):
        fuente = (metadata or {}).get("fuente")
        if not fuente:
            raise ValueError(f"El fragmento {id_fragmento} no tiene fuente.")

        # Hoy hay un fragmento por archivo. Si eso cambia, hay que etiquetar
        # los fragmentos específicos; no asumir que todo el archivo es relevante.
        if fuente in ids_por_fuente:
            raise ValueError(f"{fuente} tiene varios fragmentos. Revisa las etiquetas.")

        ids_por_fuente[fuente] = id_fragmento

    return ids_por_fuente


def calcular_metricas(ids_recuperados, ids_esperados):
    """Compara los fragmentos encontrados con los etiquetados como relevantes."""
    recuperados = set(ids_recuperados)
    aciertos = len(recuperados & ids_esperados)

    # Precisión: de lo que llegó, ¿cuánto sirve?
    precision = aciertos / len(recuperados) if recuperados else 0.0

    # Si el corpus no contiene la respuesta, no hay fragmentos relevantes
    # que podamos usar como denominador. Tampoco hay F1 para ese caso.
    if not ids_esperados:
        return precision, None, None

    # Exhaustividad: de todo lo que servía, ¿cuánto llegó?
    recall = aciertos / len(ids_esperados)
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return precision, recall, f1


def evaluar(almacen, k):
    """Ejecuta el banco contra la búsqueda real y devuelve un reporte de texto."""
    ids_por_fuente = obtener_ids_por_fuente(almacen)

    # Resolvemos todas las referencias antes de iniciar llamadas a Gemini.
    fuentes_faltantes = {
        fuente
        for caso in CASOS
        for fuente in caso["fuentes_esperadas"]
        if fuente not in ids_por_fuente
    }
    if fuentes_faltantes:
        raise ValueError("Fuentes ausentes en el índice: " + ", ".join(sorted(fuentes_faltantes)))

    momento = datetime.now(timezone.utc)
    lineas = [
        f"Fecha (UTC): {momento.isoformat()}",
        f"Configuración: k={k}, chunk_size=300, chunk_overlap=30",
        f"Colección: {COLECCION} | Embeddings: {MODELO_EMBEDDINGS}",
        "",
    ]
    precisiones, recalls, valores_f1 = [], [], []

    for caso in CASOS:
        pregunta = caso["pregunta"]
        esperados = {ids_por_fuente[fuente] for fuente in caso["fuentes_esperadas"]}

        # Reutilizamos la función del asistente: un embedding de la consulta
        # y una búsqueda en Chroma. Aquí no se genera una respuesta de chat.
        fragmentos = recuperar_fragmentos(almacen, pregunta, k=k)
        recuperados = [fragmento.id for fragmento in fragmentos]
        if any(not id_fragmento for id_fragmento in recuperados):
            raise ValueError(f"Caso {caso['id']}: Chroma devolvió un fragmento sin ID.")

        precision, recall, f1 = calcular_metricas(recuperados, esperados)
        precisiones.append(precision)
        if recall is not None:
            recalls.append(recall)
        if f1 is not None:
            valores_f1.append(f1)

        recall_txt = "n/a" if recall is None else f"{recall:.3f}"
        f1_txt = "n/a" if f1 is None else f"{f1:.3f}"
        encabezado = f"Caso {caso['id']}: {pregunta}"
        resumen = f"Precisión={precision:.3f} | Recall={recall_txt} | F1={f1_txt}"
        print(encabezado, resumen, sep="\n", flush=True)

        lineas.extend([
            encabezado,
            f"  IDs esperados: {', '.join(sorted(esperados)) or 'ninguno'}",
            f"  IDs recuperados: {', '.join(recuperados) or 'ninguno'}",
            "  Fuentes recuperadas: " + (
                ", ".join(doc.metadata.get("fuente", "(sin fuente)") for doc in fragmentos)
                or "ninguna"
            ),
            f"  {resumen}",
            "",
        ])

    # La precisión incluye los 10 casos. Recall y F1 solo promedian
    # los 9 que tienen al menos un fragmento relevante.
    promedio = (
        f"Promedios: precisión={mean(precisiones):.3f} ({len(precisiones)} casos) | "
        f"recall={mean(recalls):.3f} | F1={mean(valores_f1):.3f} "
        f"({len(recalls)} casos con fuente)"
    )
    lineas.append(promedio)
    return momento, lineas


def main():
    """Configura la corrida y guarda su evidencia sin sobrescribir la anterior."""
    parser = argparse.ArgumentParser(description="Evalúa la recuperación del RAG.")
    parser.add_argument("--k", type=int, default=2, help="Cantidad de fragmentos a buscar.")
    args = parser.parse_args()
    if args.k < 1:
        parser.error("--k debe ser mayor o igual a 1.")

    if not (INDICE / "chroma.sqlite3").is_file():
        raise SystemExit("No se encontró el índice local en vectorstore/.")

    load_dotenv(RAIZ / ".env")
    clave = os.getenv("GEMINI_API_KEY")
    if not clave:
        raise SystemExit("Falta GEMINI_API_KEY en el archivo .env.")

    try:
        almacen = abrir_indice(clave)
        momento, lineas = evaluar(almacen, args.k)
    except ValueError as error:
        # Ocultamos la clave si un error de configuración llegara a incluirla.
        raise SystemExit(str(error).replace(clave, "[CLAVE OCULTA]")) from None
    except Exception as error:
        raise SystemExit(
            f"La evaluación se interrumpió ({type(error).__name__}). "
            "Revisa la conexión, el índice o la cuota. No se guardó esta corrida."
        ) from None

    carpeta = RAIZ / "docs" / "evaluaciones"
    carpeta.mkdir(parents=True, exist_ok=True)
    marca = momento.strftime("%Y%m%dT%H%M%S%fZ")
    archivo = carpeta / f"resultados_evaluacion-{marca}-k{args.k}.txt"
    archivo.write_text("\n".join(lineas) + "\n", encoding="utf-8")

    print(f"\n{lineas[-1]}")
    print(f"Reporte guardado en: {archivo}")


if __name__ == "__main__":
    main()
