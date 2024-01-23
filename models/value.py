from pydantic import BaseModel


class Value(BaseModel):
    value: str = ""
