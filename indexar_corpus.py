import argparse
import os
from pathlib import Path

from hashlib import sha256

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

def actualizar():
    """Sincroniza Chroma con los Markdown y recalcula solo lo necesario."""
    # Este modo trabaja sobre un índice existente. Si todavía no hay
    # una base local, primero hay que crearla con el modo "indexar".
    if not (INDICE / "chroma.sqlite3").is_file():
        raise ValueError("No se encontró el índice. Ejecuta primero indexar.")

    # Leemos y dividimos el corpus con la misma función del Bloque 24.
    # Este paso es local: todavía no se llama a Gemini.
    fragmentos = preparar_fragmentos()

    # Cada clave combina el archivo de origen y el texto del fragmento.
    # Al principio, todos están pendientes de comparar con Chroma.
    pendientes = {
        (doc.metadata["fuente"], doc.page_content): doc
        for doc in fragmentos
    }

    # Apuntamos a la misma carpeta y colección que usamos al indexar.
    # Si la colección no existe, preferimos que falle en lugar de
    # crear una colección vacía por error.
    opciones = {
        "collection_name": COLECCION,
        "persist_directory": str(INDICE),
        "create_collection_if_not_exists": False,
    }

    # Para leer lo guardado no necesitamos un modelo de embeddings.
    # get() devuelve los textos, sus metadatos y los IDs de Chroma.
    almacen = Chroma(**opciones)
    datos = almacen.get(include=["documents", "metadatas"])

    conservar = 0
    obsoletos = []

    # zip reúne el ID, el texto y los metadatos de cada registro.
    # strict=True hace visible un problema si las listas no tienen
    # la misma cantidad de elementos.
    for id_guardado, texto, metadata in zip(
        datos["ids"], datos["documents"], datos["metadatas"], strict=True
    ):
        clave = ((metadata or {}).get("fuente"), texto)

        if clave in pendientes:
            # El mismo texto sigue vigente en el mismo archivo.
            # Lo quitamos de "pendientes" porque ya está en Chroma.
            # No escribimos nada: conserva su ID y su embedding.
            pendientes.pop(clave)
            conservar += 1
        else:
            # Este registro ya no tiene una coincidencia en el corpus.
            # Guardamos su ID para retirarlo más adelante.
            obsoletos.append(id_guardado)

    # Lo que quedó pendiente no tenía una copia vigente en Chroma:
    # son fragmentos nuevos o versiones modificadas de otros anteriores.
    nuevos = list(pendientes.values())

    if nuevos:
        # Solo buscamos la clave y configuramos Gemini si hay texto
        # que requiere un embedding nuevo.
        load_dotenv(RAIZ / ".env")
        clave_api = os.getenv("GEMINI_API_KEY")
        if not clave_api:
            raise ValueError("Falta GEMINI_API_KEY en el archivo .env.")

        # Usamos el mismo modelo del índice original para que los
        # vectores nuevos sean comparables con los que conservamos.
        embeddings = GoogleGenerativeAIEmbeddings(
            model=MODELO_EMBEDDINGS,
            api_key=clave_api,
        )
        almacen = Chroma(embedding_function=embeddings, **opciones)

        # SHA-256 genera una huella a partir de la fuente y el texto.
        # La misma fuente con el mismo texto da el mismo ID.
        # Si cambia el texto, cambia el ID. El "\0" separa ambas partes.
        ids = [
            sha256(
                f"{doc.metadata['fuente']}\0{doc.page_content}".encode("utf-8")
            ).hexdigest()
            for doc in nuevos
        ]

        try:
            # Esta es la operación que llama a Gemini para calcular
            # los embeddings y luego guarda los fragmentos en Chroma.
            almacen.add_documents(nuevos, ids=ids)
        except Exception as error:
            # Si no pudimos guardar los reemplazos, nos detenemos
            # antes de borrar los registros anteriores.
            raise RuntimeError(
                f"No se pudieron guardar los fragmentos nuevos "
                f"({type(error).__name__}). No se inició la eliminación."
            ) from None

    # Borramos por ID para retirar exactamente los registros obsoletos.
    # Hacemos esto después de guardar los nuevos, si los hubo.
    if obsoletos:
        almacen.delete(ids=obsoletos)

    print(f"Fragmentos conservados: {conservar}")
    print(f"Fragmentos con embeddings nuevos: {len(nuevos)}")
    print(f"Fragmentos retirados: {len(obsoletos)}")

def main():
    """Lee el comando de la terminal y ejecuta el modo correspondiente."""
    parser = argparse.ArgumentParser(
        description="Indexa, verifica o actualiza el corpus."
    )
    parser.add_argument("modo", choices=("indexar", "verificar", "actualizar"))
    argumentos = parser.parse_args()

    try:
        if argumentos.modo == "indexar":
            indexar()       # Crea el índice por primera vez.
        elif argumentos.modo == "actualizar":
            actualizar()    # Aplica cambios a un índice existente.
        else:
            verificar()     # Comprueba si Chroma coincide con los Markdown.
    except (ValueError, RuntimeError) as error:
        # Muestra el mensaje del problema y termina con un código de error.
        raise SystemExit(str(error)) from None


if __name__ == "__main__":
    main()