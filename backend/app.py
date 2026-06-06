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
Hoy es {date}.
Eres un asistente virtual de atención al cliente de la empresa internacional de muebles IKEA.
Tus funciones son ayudar a los clientes a resolver sus dudas sobre los productos y promociones vigentes.
Cuando el usuario te pida ayuda EN TODO LO QUE TENGA QUE VER CON REEMBOLSOS, PEDIDOS DEFECTUOSOS Y PROBLEMAS DE ENVÍO, 
le vas a pasar los CONTACTOS CON LOS ASESORES (SOLAMENTE NOMBRE, EMAIL Y HORARIO DE ATENCIÓN).
INFORMACIÓN DE PRODUCTOS Y PROMOCIONES (debes usar esta información para responder al cliente):
- Productos disponibles: {products}
- Promociones vigentes: {promotions}
Cuando el cliente pregunte sobre promociones o productos, PROPORCIONA LA INFORMACIÓN DISPONIBLE.
NUNCA LE PIDAS AL CLIENTE QUE TE DÉ DATOS DE PROMOCIONES O PRODUCTOS DEL INVENTARIO.
Los FAQs son los siguientes: {faqs}
Los asesores disponibles son: {advisors}
Aquí está la pregunta del cliente: {question}
El historial de la conversación es este: {chat_history}. IMPORTANTE: Solo es para que lo leas y te bases en eso
para tus respuestas. No lo menciones. Solo es como tu memoria "cerebral".
También, presta ATENCIÓN: {greeting_instruction}
ATENCIÓN: Cuando el usuario te agradezca, SOLAMENTE DILE "De nada. ¡Que tenga un buen día!". NO LE DIGAS OTRAS COSA MÁS.

REGLAS IMPORTANTES:
Respuestas claras, breves y concisas, lo más actualizadas posible.
Si es un producto DAÑADO, DEFECTUOSO O CON PROBLEMAS DE ENVÍO:
   - SÓLO muestra los datos del asesor: Nombre, Email y Horario
   - NO incluyas FAQs, productos, ni información extra
   - Sé empático con el problema del cliente
Si necesitas información del cliente: SOLO pide información DIRECTA relacionada con su problema.
Si no puedes resolver algo: ofrece los contactos de los asesores correspondientes.
NUNCA pidas ayuda ni solicites datos innecesarios.
NUNCA le pidas promociones, productos, o contactos como si fuera el cliente quien te ayuda.
NUNCA digas que no pudiste responder una pregunta. Si necesario, deriva al asesor.
NUNCA incluyas FAQs si el cliente reporta daño/defecto/envío.
"""

template_prompt = ChatPromptTemplate.from_template(instructions)
chain = template_prompt | model
chat_history = []

# Formatear el historial del chat.
def chat_history_to_string(history):
    if history: 
        return "\n\n".join(
            f"Usuario: {line['Usuario']}\nBot: {line['Bot']}" for line in history
        )
    return ""

# _______________________________________________________________________________________

"""
Para correr el servidor de la API en la terminal (ubicado en la carpeta "backend"
con el venv activado):

"daphne -b 0.0.0.0 -p 8000 app:API"
"""

# Detectar si la pregunta está relacionada con un producto dañado/defectuoso.
def is_damage_or_defect_issue(text):
    damage_keywords = [
        "dañado", "dañada", "roto", "rota", "defectuoso", "defectuosa",
        "problema de envío", "problema con envío", "llegó roto", "llegó dañado",
        "llegó defectuoso", "pata rota", "patas rotas", "brazo roto", "respaldo roto",
        "cristal roto", "espejo roto", "madera rota", "rajado", "rajada",
        "roto en el envío", "dañado en el envío", "producto defectuoso", 
        "no funciona", "defecto de fábrica", "defecto", "error de fabricación"
    ]
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in damage_keywords)

# Detectar si es un agradecimiento simple (no requiere búsqueda de información)
def is_gratitude(text):
    gratitude_keywords = [
        "gracias", "muchas gracias", "gracias por", "agradezco", "muy amable",
        "thank you", "thanks", "merci", "grazie", "danke"
    ]
    text_lower = text.lower().strip()
    return any(keyword in text_lower for keyword in gratitude_keywords)

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
        greeting_instruction = "Saluda al usuario y responde su pregunta."
    else:
        greeting_instruction = "No saludes al usuario. Solo responde su pregunta."
    
    # Detectar si es un agradecimiento simple
    if is_gratitude(processed_prompt):
        response = "De nada. ¡Que tenga un buen día!"
        chat_history.append({"Usuario": processed_prompt, "Bot": response})
        return {
            "user_prompt": processed_prompt,
            "chatbot_response": response
        }
    
    # Detectar si es un problema de daño/defecto
    is_damage_issue = is_damage_or_defect_issue(processed_prompt)
    
    if is_damage_issue:
        # Si es producto dañado/defectuoso, priorizar asesores y NO incluir FAQs
        productos = []
        promociones = []
        faqs = []
        advisors = advisors_retriever.invoke(processed_prompt)
    else:
        # Recuperación normal de productos
        productos = products_retriever.invoke(processed_prompt)
        promociones = promotions_retriever.invoke(processed_prompt)
        faqs = faqs_retriever.invoke(processed_prompt)
        advisors = advisors_retriever.invoke(processed_prompt)

    response = chain.invoke({
        "date": date,
        "products": productos,
        "promotions": promociones,
        "faqs": faqs,
        "advisors": advisors,
        "question": processed_prompt,
        "chat_history": chat_history_to_string(chat_history),
        "greeting_instruction": greeting_instruction
    })

    chat_history.append({"Usuario": processed_prompt, "Bot": response})

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