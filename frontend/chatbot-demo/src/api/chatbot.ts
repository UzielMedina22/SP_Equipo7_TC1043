import axios from "axios";

const API_URL = import.meta.env.VITE_LLM_URL || "http://127.0.0.1:8000"

// Función que permite obtener la respuesta del chatbot.
export const talkWithLLM = async (prompt: string) => {
    const res = await axios.post(`${API_URL}/chatbot-conversation/`, { prompt_message: prompt });
    return res.data;
}