from pydantic import BaseModel

class Prompt(BaseModel):
    description: str