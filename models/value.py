from pydantic import BaseModel


class Value(BaseModel):
    value_: str = ""
