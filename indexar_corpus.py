import argparse
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

RAIZ = Path(__file__).resolve().parent
CORPUS = RAIZ / "docs" / "corpus"
INDICE = RAIZ / "vectorstore"
COLECCION = "fotografia"
MODELO_EMBEDDINGS = "models/gemini-embedding-001"


def preparar_fragmentos():
    """Lee los Markdown, los divide por archivo y conserva su fuente."""
    archivos = sorted(CORPUS.glob("*.md"))
    if len(archivos) < 5:
        raise ValueError("Se necesitan al menos cinco documentos Markdown.")

    # Los documentos actuales son cortos. Un límite de 300 caracteres
    # permite mantener juntas las reglas y sus condiciones.
    divisor = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=30)
    fragmentos = []

    for archivo in archivos:
        fuente = archivo.relative_to(RAIZ).as_posix()
        texto = archivo.read_text(encoding="utf-8").strip()

        if not texto:
            raise ValueError(f"El documento está vacío: {fuente}")

        fragmentos.extend(
            divisor.create_documents([texto], metadatas=[{"fuente": fuente}])
        )

    textos = [fragmento.page_content for fragmento in fragmentos]
    if len(textos) != len(set(textos)):
        raise ValueError("El corpus produjo fragmentos duplicados.")

    print(f"Documentos: {len(archivos)} | Fragmentos: {len(fragmentos)}")
    return fragmentos


def indexar():
    """Genera embeddings reales y guarda el índice en disco."""
    if INDICE.exists():
        raise ValueError("vectorstore/ ya existe. Usa el modo verificar.")

    fragmentos = preparar_fragmentos()
    load_dotenv(RAIZ / ".env")
    clave = os.getenv("GEMINI_API_KEY")
    if not clave:
        raise ValueError("Falta GEMINI_API_KEY en el archivo .env.")

    embeddings = GoogleGenerativeAIEmbeddings(
        model=MODELO_EMBEDDINGS,
        api_key=clave,
    )

    try:
        Chroma.from_documents(
            documents=fragmentos,
            embedding=embeddings,
            collection_name=COLECCION,
            persist_directory=str(INDICE),
        )
    except Exception as error:
        raise RuntimeError(
            f"No se completó la indexación ({type(error).__name__}). "
            "Revisa la clave, la cuota o la conexión."
        ) from None

    print(f"Índice guardado: {len(fragmentos)} fragmentos en vectorstore/.")


def verificar():
    """Reabre Chroma y comprueba el contenido sin llamar a Gemini."""
    if not (INDICE / "chroma.sqlite3").is_file():
        raise ValueError("No se encontró el índice. Ejecuta primero indexar.")

    fragmentos = preparar_fragmentos()
    almacen = Chroma(collection_name=COLECCION, persist_directory=str(INDICE))
    datos = almacen.get(include=["documents", "metadatas"])

    # Compara fuente y texto, sin depender del orden en que Chroma los devuelva.
    esperados = sorted(
        (fragmento.metadata["fuente"], fragmento.page_content)
        for fragmento in fragmentos
    )
    guardados = sorted(
        ((metadatos or {}).get("fuente", ""), texto)
        for metadatos, texto in zip(datos["metadatas"], datos["documents"])
    )

    if guardados != esperados:
        raise ValueError("El contenido guardado no coincide con el corpus actual.")

    print(f"Índice reabierto: {len(guardados)} fragmentos verificados.")
    print("No se recalcularon embeddings.")
    for fuente in sorted({fuente for fuente, _ in guardados}):
        print(f"- {fuente}")


def main():
    parser = argparse.ArgumentParser(description="Indexa o verifica el corpus.")
    parser.add_argument("modo", choices=("indexar", "verificar"))
    argumentos = parser.parse_args()

    try:
        if argumentos.modo == "indexar":
            indexar()
        else:
            verificar()
    except (ValueError, RuntimeError) as error:
        raise SystemExit(str(error)) from None


if __name__ == "__main__":
    main()