from pydantic import BaseModel

class MemeCreate(BaseModel):
    title: str
    url: str

class Meme(MemeCreate):
    id: int

    class Config:
        orm_mode = True