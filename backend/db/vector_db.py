from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
import os
import pandas as pd

# Embedding de Ollama en español e inglés.
embedding = OllamaEmbeddings(model="jina/jina-embeddings-v2-base-es")

# Importar productos, FAQs, asesores y promociones desde sus respectivos archivos CSV.
products_dataframe = pd.read_csv("./db/seed/productos.csv")
faqs_dataframe = pd.read_csv("./db/seed/faq.csv")
advisors_dataframe = pd.read_csv("./db/seed/asesores.csv")
promotions_dataframe = pd.read_csv("./db/seed/promociones.csv")

db_location = "./db_chroma"                                # Directorio de la base de datos.
must_add_db_documents = not os.path.exists(db_location)    # Verificar si la base de datos ya existe.


# IDs de los documentos según sus entidades.
product_ids = []
advisor_ids = []
faq_ids = []
promotion_ids = []

# Registros de cada entidad.
product_documents = []
advisor_documents = []
faq_documents = []
promotion_documents = []


# Productos.
for id, row in products_dataframe.iterrows():
    product_ids.append(id)
    product_id_key = row["product_id"]
    product_line = row["product_line"]
    product_name = row["product_name"]
    product_category = row["category"]
    product_color = row["color"]
    product_width = row["width_cm"]
    product_depth = row["depth_cm"]
    product_height = row["height_cm"]
    product_weight = row["weight_kg"]
    product_price = row["price_mxn"]
    product_stock_units = row["stock_units"]
    product_availability = row["availability_status"]
    product_source_url = row["source_url"]

    product_info = f"ID: {product_id_key}\n" \
                   f"Línea: {product_line}\n" \
                   f"Nombre: {product_name}\n" \
                   f"Categoría: {product_category}\n" \
                   f"Color: {product_color}\n" \
                   f"Ancho: {product_width} cm\n" \
                   f"Profundidad: {product_depth} cm\n" \
                   f"Alto: {product_height} cm\n" \
                   f"Peso: {product_weight} kg\n" \
                   f"Precio: ${product_price:.2f}\n" \
                   f"Unidades en stock: {product_stock_units}\n" \
                   f"Disponibilidad: {product_availability}\n" \
                   f"URL de origen: {product_source_url}"

    product_documents.append(Document(page_content=product_info))


# FAQs.
for id, row in faqs_dataframe.iterrows():
    faq_ids.append(id)
    faq_id_key = row["faq_id"]
    faq_topic = row["topic"]
    faq_question = row["question"]
    faq_answer = row["answer"]

    faq_info = f"ID: {faq_id_key}\n" \
                f"Tópico: {faq_topic}\n" \
                f"Pregunta: {faq_question}\n" \
                f"Respuesta: {faq_answer}"

    faq_documents.append(Document(page_content=faq_info))


# Asesores.
for id, row in advisors_dataframe.iterrows():
    advisor_ids.append(id)
    advisor_id_key = row["advisor_id"]
    advisor_name = row["advisor_name"]
    advisor_specialty = row["specialty"]
    advisor_email = row["email"]
    advisor_status = row["status"]
    advisor_shift_start = row["shift_start"]
    advisor_shift_end = row["shift_end"]

    advisor_info = f"ID: {advisor_id_key}\n" \
                   f"Nombre: {advisor_name}\n" \
                   f"Email: {advisor_email}\n" \
                   f"Especialidad: {advisor_specialty}\n" \
                   f"Estado: {advisor_status}\n" \
                   f"Inicio de turno: {advisor_shift_start}\n" \
                   f"Fin de turno: {advisor_shift_end}"

    advisor_documents.append(Document(page_content=advisor_info))


# Promociones
for id, row in promotions_dataframe.iterrows():
    promotion_ids.append(id)
    promotion_id_key = row["promotion_id"]
    promotion_name = row["promotion_name"]
    promotion_discount = row["discount_percent"]
    promotion_start_date = row["start_date"]
    promotion_end_date = row["end_date"]
    promotion_status = row["promotion_status"]

    promotion_info = f"ID: {promotion_id_key}\n" \
                     f"Nombre: {promotion_name}\n" \
                     f"Descuento: {promotion_discount}%\n" \
                     f"Fecha de inicio: {promotion_start_date}\n" \
                     f"Fecha de fin: {promotion_end_date}\n" \
                     f"Estado: {promotion_status}"

    promotion_documents.append(Document(page_content=promotion_info))


# Crear colecciones de productos, asesores, FAQs y promociones en la base de datos.
products_vector_store = Chroma(
    collection_name="productos",
    embedding_function=embedding,
    persist_directory=db_location
)

advisors_vector_store = Chroma(
    collection_name="asesores",
    embedding_function=embedding,
    persist_directory=db_location
)

faq_vector_store = Chroma(
    collection_name="faqs",
    embedding_function=embedding,
    persist_directory=db_location
)

promotions_vector_store = Chroma(
    collection_name="promociones",
    embedding_function=embedding,
    persist_directory=db_location
)


# Añadir productos, FAQs, asesores y promociones a sus respectivas colecciones.
if must_add_db_documents:
    products_vector_store.add_documents(product_documents, ids=[str(id) for id in product_ids])
    advisors_vector_store.add_documents(advisor_documents, ids=[str(id) for id in advisor_ids])
    faq_vector_store.add_documents(faq_documents, ids=[str(id) for id in faq_ids])
    promotions_vector_store.add_documents(promotion_documents, ids=[str(id) for id in promotion_ids])


# Buscar productos, FAQs, asesores y promociones por cantidad (k).
products_retriever = products_vector_store.as_retriever(search_kwargs={"k": 10})
advisors_retriever = advisors_vector_store.as_retriever(search_kwargs={"k": 10})
faqs_retriever = faq_vector_store.as_retriever(search_kwargs={"k": 10})
promotions_retriever = promotions_vector_store.as_retriever(search_kwargs={"k": 10})