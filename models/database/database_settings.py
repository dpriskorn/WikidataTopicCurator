from pydantic import BaseModel


class DatabaseSettings(BaseModel):
    username: str
    password: str
    host: str
    port: int
    database: str
