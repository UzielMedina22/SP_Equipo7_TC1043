from fastapi import FastAPI, HTTPException
from models.prompt_model import Prompt
from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from db.vector_db import products_retriever


# ________________________________________________________________________________________

"""
Se está utilizando un LLM de Ollama llamado "llama3.2" para generación de texto.
Este se descarga aparte con el comando "ollama pull llama3.2".
"""
model = OllamaLLM(model="llama3.2")


instructions = """
Eres un asistente virtual de atención al cliente de la empresa internacional de muebles IKEA.
Tus funciones son ayudar a los clientes a resolver sus dudas sobre los productos y ofertas vigentes.
En caso de que algunas necesidades del clientes estén fuera de tu alcance, debes notificar a un
agente humano para que atienda al cliente, enviándole una notificación con la información con base en
el contexto.

Aquí hay productos {products} y ofertas {offers} relevantes.

Aquí está la pregunta del cliente: {question}

Trata que las respuestas sean claras, breves y concisas.
"""

template_prompt = ChatPromptTemplate.from_template(instructions)
chain = template_prompt | model

# _______________________________________________________________________________________

"""
Para correr el servidor de la API en la terminal (ubicado en la carpeta "backend"
con el venv activado):

"daphne -b 0.0.0.0 -p 8000 app:API"
"""

# Crear la API.
API = FastAPI()

# Endpoint raíz.
@API.get("/")
def main():
    return {"data": "Este es el servidor de IKEA-Bot."}


# Monitorear la salud del servidor.
@API.get("/health")
def health():
    return {"status": "OK", "http_code": 200}


# Endpoint para obtener la respuesta del chatbot.
@API.post("/chatbot-conversation")
async def chatbot_conversation(prompt: Prompt):
    if not prompt.description or prompt.description.strip() == "":
        raise HTTPException(status_code=400, detail="El prompt ingresado es inválido o está vacío.")

    processed_prompt = prompt.description.strip()
    productos = products_retriever.invoke(processed_prompt)   # Obtener productos relevantes para el prompt.

    response = chain.invoke({
        "products": productos,
        "offers": [],
        "question": processed_prompt
    })

    return {
        "user_prompt": processed_prompt,
        "chatbot_response": response
    }


# Endpoint para obtener notificaciones de las dudas de los usuarios.
@API.get("/get-help-notifications")
def get_help_notifications():
    notifications = [
        {"id": 1, "message": "El usuario necesita ayuda con su pedido."},
        {"id": 2, "message": "El usuario quiere realizar un reembolso."},
        {"id": 3, "message": "El usuario necesita ayuda para facturar."},
    ]

    return {"data": notifications}