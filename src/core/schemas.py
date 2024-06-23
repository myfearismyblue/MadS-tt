from pydantic import BaseModel


class MemeCreate(BaseModel):
    title: str


class MemeEnriched(MemeCreate):
    url: str
    etag: str


class Meme(MemeEnriched):
    id: int

    class Config:
        from_attributes = True
