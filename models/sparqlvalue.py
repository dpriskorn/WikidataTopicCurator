from pydantic import BaseModel


class SparqlValue(BaseModel):
    value: str = ""
