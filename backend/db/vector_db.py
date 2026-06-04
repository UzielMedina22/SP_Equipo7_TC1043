from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
import os
import pandas as pd

# Embedding de Ollama en español e inglés.
embedding = OllamaEmbeddings(model="jina/jina-embeddings-v2-base-es")

products_dataframe = pd.read_csv("./db/seed/productos.csv")        # Importar productos desde el CSV.
db_location = "./db_chroma"                                     # Directorio de la base de datos.
must_add_product_documents = not os.path.exists(db_location)    # Verificar si hay base de datos.


# Poblar la base de datos con los productos en el CSV.
if must_add_product_documents:
    product_documents = []
    product_ids = []

    for id, row in products_dataframe.iterrows():
        product_ids.append(id)
        product_name = row["nombre"]
        product_price = row["precio"]
        product_category = row["categoria"]
        product_desc = row["descripcion"]

        product_info = f"Nombre: {product_name}\nPrecio: {product_price}\nCategoría: {product_category}\nDescripción: {product_desc}"
        product_documents.append(Document(page_content=product_info))


# Crear una colección de productos la base de datos.
products_vector_store = Chroma(
    collection_name="productos",
    embedding_function=embedding,
    persist_directory=db_location
)


# Añadir productos.
if must_add_product_documents:
    products_vector_store.add_documents(product_documents, ids=product_ids)


# Buscar productos por cantidad (k).
products_retriever = products_vector_store.as_retriever(search_kwargs={"k": 10})   # Buscar documentos.