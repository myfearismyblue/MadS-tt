from pydantic import BaseModel


class MemeCreate(BaseModel):
    title: str


class MemeEnriched(MemeCreate):
    url: str


class Meme(MemeEnriched):
    id: int

    class Config:
        orm_mode = True
        from_attributes = True
