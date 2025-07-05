from pydantic import BaseModel


class Ask(BaseModel):
    message: str
