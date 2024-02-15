from pydantic import BaseModel


class SparqlValue(BaseModel):
    string: str = ""
