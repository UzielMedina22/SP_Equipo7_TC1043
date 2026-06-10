from pydantic import BaseModel

class Prompt(BaseModel):
    prompt_message: str
