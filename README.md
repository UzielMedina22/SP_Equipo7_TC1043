# IKEA-Bot 
Este es un chatbot de atención al cliente desarrollado para la Etapa 3 de la Situación Problema de Fundamentos de Inteligencia Artificial.

## ¿Cómo utilizarlo?
- Descarga Ollama en tu computadora.
- Cuando se haya instalado, abre la terminal e ingresa `ollama pull llama3.2` para descargar el LLM que utiliza el sistema.
- Ingresa `ollama pull jina/jina-embeddings-v2-base-es` para descargar el embedding necesario para el LLM.

### Backend
- Ubícate en la carpeta `backend` y activa el entorno virtual de la carpeta `my_venv`.
- Instala las dependencias con `pip install requirements.txt`
- Para levantar el servidor, ingresa `daphne -b 0.0.0.0 -p [PUERTO] app:API`.
- Para interactuar con el chatbot ve a `http://127.0.0.1:[PUERTO]/chatbot-conversation`. El protocolo utilizado es `POST` y el JSON que debes mandar es.
- IMPORTANTE: Asegúrate de que Ollama esté corriendo en el equipo mientras el servidor de backend esté corriendo.
```
{
  "prompt_message": "Aquí va el mensaje o pregunta que le quieras mandar al chatbot."
}
```

### Frontend
- Asegúrate de tener Node.js instalado en tu equipo.
- Ubícate en la carpeta `frontend/chatbot-demo`.
- Abre la terminal e ingresa `npm install` (o `npm.cmd install`) para instalar las dependencias necesarias.
- Ingresa `npm run dev` (o `npm.cmd run dev`) para levantar el servidor de React.

## IMPORTANTE
El servidor de backend utiliza protección CORS. Si no recibes respuesta del chatbot, haz clic derecho y da clic en "Inspeccionar". Revisa la consola y verifica si hay algún error relacionado con el endpoint. En caso de tenerlo, modifiqué la línea 113 de `app.py`, agregando el link local del servidor de React (ej.: `http://localhost:5173/`).
