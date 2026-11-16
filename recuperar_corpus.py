import argparse
import os

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from indexar_corpus import COLECCION, INDICE, MODELO_EMBEDDINGS, RAIZ


def abrir_indice(clave):
    """Abre la colección de fotografía que ya guardamos en Chroma."""
    # Usamos el mismo modelo que al indexar para que los vectores
    # de la pregunta y de los documentos sean comparables.
    embeddings = GoogleGenerativeAIEmbeddings(
        model=MODELO_EMBEDDINGS,
        api_key=clave,
    )
    return Chroma(
        collection_name=COLECCION,
        persist_directory=str(INDICE),
        embedding_function=embeddings,
        create_collection_if_not_exists=False,
    )


def recuperar_fragmentos(almacen, pregunta, k=2):
    """Busca hasta k fragmentos cercanos al significado de la pregunta."""
    # Gemini convierte la pregunta en un vector. Chroma lo compara
    # con los vectores guardados sin volver a indexar los Markdown.
    return almacen.similarity_search(pregunta, k=k)


def formatear_contexto(fragmentos):
    """Devuelve el contexto numerado y un mapa de citas a archivos."""
    lineas = []
    citas = {}

    for numero, fragmento in enumerate(fragmentos, start=1):
        # La fuente viene del metadato que guardamos al indexar.
        fuente = fragmento.metadata.get("fuente")
        if not fuente:
            raise ValueError(f"El fragmento [{numero}] no tiene fuente registrada.")

        lineas.append(f"[{numero}] {fragmento.page_content}")
        citas[numero] = fuente

    return "\n\n".join(lineas), citas


def main():
    parser = argparse.ArgumentParser(description="Busca y numera fragmentos del corpus.")
    parser.add_argument("pregunta")
    parser.add_argument("--k", type=int, default=2)
    args = parser.parse_args()

    pregunta = args.pregunta.strip()
    if not pregunta or args.k < 1:
        parser.error("Escribe una pregunta y usa un --k de al menos 1.")

    if not (INDICE / "chroma.sqlite3").is_file():
        raise SystemExit("No se encontró vectorstore/. Revisa el índice del Bloque 24.")

    load_dotenv(RAIZ / ".env")
    clave = os.getenv("GEMINI_API_KEY")
    if not clave:
        raise SystemExit("Falta GEMINI_API_KEY en el archivo .env.")

    try:
        almacen = abrir_indice(clave)
        fragmentos = recuperar_fragmentos(almacen, pregunta, k=args.k)
    except Exception as error:
        # Informamos el tipo de fallo sin mostrar la petición ni la clave.
        raise SystemExit(
            f"No se pudo consultar Chroma ({type(error).__name__})."
        ) from None

    if not fragmentos:
        print("No se recuperaron fragmentos.")
        return

    try:
        contexto, citas = formatear_contexto(fragmentos)
    except ValueError as error:
        raise SystemExit(str(error)) from None

    print(f"\nContexto recuperado:\n\n{contexto}")
    print("\nMapa de citas:")
    for numero, fuente in citas.items():
        print(f"[{numero}] {fuente}")


if __name__ == "__main__":
    main()