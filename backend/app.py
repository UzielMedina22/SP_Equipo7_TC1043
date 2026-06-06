from fastapi import FastAPI, HTTPException
from models.prompt_model import Prompt
from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from db.vector_db import products_retriever, promotions_retriever, faqs_retriever, advisors_retriever
import datetime


# ________________________________________________________________________________________

"""
Se está utilizando un LLM de Ollama llamado "llama3.2" para generación de texto.
Este se descarga aparte con el comando "ollama pull llama3.2".
"""
model = OllamaLLM(model="llama3.2")

date = datetime.datetime.now()

instructions = """
Eres un asistente virtual de atención al cliente de la empresa internacional de muebles IKEA.
Tus funciones son ayudar a los clientes a resolver sus dudas sobre los productos y ofertas vigentes.
En caso de que algunas necesidades del clientes estén fuera de tu alcance, debes notificar a un
agente humano para que atienda al cliente, enviándole una notificación con la información con base en
el contexto.

Hoy es {date}.

Aquí hay productos {products} y ofertas {promotions} relevantes.

Los FAQs son los siguientes: {faqs}

Los asesores disponibles son: {advisors}

Aquí está la pregunta del cliente: {question}

El historial de la conversación es este: {chat_history}. IMPORTANTE: Solo es para que lo leas y te bases en eso
para tus repuestas. No lo menciones. Solo es como tu memoria \"cerebral\".

También, presta ATENCIÓN: {greeting_instruction}

URGENTE: Que las respuestas sean claras, breves, concisas y lo más actualizadas posible.
"""

template_prompt = ChatPromptTemplate.from_template(instructions)
chain = template_prompt | model
chat_history = []

# Formatear el historial del chat.
def format_chat_history(history):
    if not history:
        return ""
    return "\n\n".join(
        f"Usuario: {item['Usuario']}\nAsistente: {item['content']}"
        for item in history
    )

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
    global chat_history
    global date

    date = datetime.datetime.now()
    
    if not prompt.description or prompt.description.strip() == "":
        raise HTTPException(status_code=400, detail="El prompt ingresado es inválido o está vacío.")

    processed_prompt = prompt.description.strip()
    
    is_first_message = len(chat_history) == 0
    
    if is_first_message:
        greeting_instruction = "Saluda al usuario en la primera interacción y responde su pregunta."
    else:
        greeting_instruction = "No saludes al usuario. Ve directo con la pregunta."
    
    productos = products_retriever.invoke(processed_prompt)   # Obtener productos relevantes para el prompt.
    promociones = promotions_retriever.invoke(processed_prompt)   # Obtener promociones relevantes para el prompt.
    faqs = faqs_retriever.invoke(processed_prompt)   # Obtener FAQs relevantes para el prompt.
    advisors = advisors_retriever.invoke(processed_prompt)   # Obtener asesores relevantes para el prompt.

    response = chain.invoke({
        "date": date,
        "products": productos,
        "promotions": promociones,
        "faqs": faqs,
        "advisors": advisors,
        "question": processed_prompt,
        "chat_history": format_chat_history(chat_history),
        "greeting_instruction": greeting_instruction
    })

    chat_history.append({"Usuario": processed_prompt, "content": response})

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