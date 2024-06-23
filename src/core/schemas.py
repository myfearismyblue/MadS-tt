from pydantic import BaseModel


class MemeCreate(BaseModel):
    """Используется при создании мема пользователем"""
    title: str
    content: str


class MemeEnriched(MemeCreate):
    """Используется после загрузки файла мема в хранилище"""
    url: str
    etag: str


class Meme(MemeEnriched):
    """Используется после загрузки мема в БД"""
    id: int

    class Config:
        from_attributes = True
