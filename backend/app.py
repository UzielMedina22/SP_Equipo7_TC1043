from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
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
le vas a pasar los CONTACTOS CON LOS ASESORES (NOMBRE, EMAIL, ÁREA Y HORARIO DE ATENCIÓN). El área del asesor
DEBE ESTAR ESTRICTAMENTE RELACIONADA al problema del cliente (NUNCA ofrezcas asesores de áreas irrelevantes). 

INFORMACIÓN DE PRODUCTOS Y PROMOCIONES (debes usar esta información para responder al cliente):
- Productos disponibles: {products}
- Promociones vigentes: {promotions}

Cuando el cliente pregunte sobre promociones o productos, PROPORCIONA LA INFORMACIÓN DISPONIBLE.
NUNCA LE PIDAS AL CLIENTE QUE TE DÉ DATOS DE PROMOCIONES O PRODUCTOS DEL INVENTARIO.

Los FAQs son los siguientes: {faqs}
Los asesores disponibles son: {advisors}

El historial de la conversación es este: {chat_history}. IMPORTANTE: Solo es para que lo leas y te bases en eso
para tus respuestas. NO LO MENCIONES, SOLO ES COMO TU MEMORIA "CEREBRAL".

Aquí está la pregunta del cliente: {question}

También, presta ATENCIÓN: {greeting_instruction}

ATENCIÓN: Cuando el cliente te agradezca, SOLAMENTE DILE "De nada. ¡Que tenga un buen día!". NO LE DIGAS OTRAS COSA MÁS.

REGLAS IMPORTANTES:
Respuestas claras, breves y concisas, lo más actualizadas posible.
Si es un producto DAÑADO, DEFECTUOSO O CON PROBLEMAS DE ENVÍO:
   - Muestra los datos del asesor: nombre, email, área y horario.
   - El área del asesor debe estar ESTRICTAMENTE RELACIONADO al problema del cliente.
   - NUNCA ofrezcas contactos de asesores cuyas áreas NO ESTÉN RELACIONADAS al problema del cliente.
   - NO incluyas FAQs, productos, ni información extra.
   - Sé empático con el problema del cliente.
Si necesitas información del cliente: SOLO pide información relacionada con su problema.
TRATA de responder lo MÁS PRECISO QUE PUEDAS.
TRATA de ayudar al cliente HASTA EL LÍMITE DE TU ALCANCE.
Si después de intentar de ayudar al cliente no puedes resolver algo, ofrece los contactos de los asesores correspondientes.
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

# Buscar palabras relacionadas con daños o errores.
def damage(message):
    damage_words = [
        "dañado", "dañada", "roto", "rota", "problema", "rajado", "rajada", "defectuoso", 
        "defectuosa", "no funciona", "error", "accidente", "defecto"
    ]
    for word in damage_words:
        if word in message.lower(): 
            return True


# Buscar palabras de agradecimiento en el mensaje del usuario.
def thanks(message):
    thank_words = ["amable", "gracias", "agradezco"]
    for word in thank_words:
        if word in message.lower().strip(): 
            return True

# _______________________________________________________________________________________

"""
Para correr el servidor de la API en la terminal (ubicado en la carpeta "backend"
con el venv activado):

"daphne -b 0.0.0.0 -p 8000 app:API" -> El puerto no necesariamente debe ser 8000; puede
ser 3000, 5000, etc.
"""


API = FastAPI()     # Crear la API.

"""
Permitir que el frontend se conecte a la API. IMPORTANTE: Si el link de su servidor de React no está aquí,
ingréselo a la lista que está debajo de este comentario.
"""
api_clients_list = ["http://localhost:5173"]

# Añadir seguridad de CORS.
API.add_middleware(CORSMiddleware, allow_headers = ["*"], allow_methods = ["*"], allow_origins = api_clients_list)

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
    
    if not prompt.prompt_message or prompt.prompt_message.strip() == "":
        raise HTTPException(status_code=400, detail="El prompt ingresado es inválido o está vacío.")

    processed_prompt = prompt.prompt_message.strip()
    is_first_message = len(chat_history) == 0
    
    if is_first_message:
        greeting_instruction = "Saluda al usuario y responde su pregunta."
    else:
        greeting_instruction = "No saludes al usuario. Solo responde su pregunta."
    
    # Detectar si es un agradecimiento simple
    if thanks(processed_prompt):
        response = "De nada. ¡Que tenga un buen día!"
        chat_history.append({"Usuario": processed_prompt, "Bot": response})
        return {
            "user_prompt": processed_prompt,
            "chatbot_response": response
        }
    
    # Detectar si es un problema de daño/defecto
    if damage(processed_prompt):
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

    return { "date": date, "chatbot_response": response }