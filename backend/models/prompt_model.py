from pydantic import BaseModel

# Modelo de un prompt del usuario.
class Prompt(BaseModel):
    prompt_message: str