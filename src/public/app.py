from fastapi import FastAPI
from fastapi_pagination import add_pagination, Page, paginate
from starlette.responses import Response

from src.config import get_settings
from src.core import repositories, schemas

app = FastAPI()
add_pagination(app)
settings = get_settings()
meme_repo = repositories.MemeRepository()

@app.get(settings.web_app.HEALTHCHECK_PATH)
async def get_health() -> Response:
    return Response(status_code=200)


@app.get("/memes", response_model=Page[schemas.Meme])
async def get_memes():
    memes = await meme_repo.get_memes()
    return paginate(memes)

@app.get("/memes/{meme_id}")
async def get_meme(meme_id: int) -> schemas.Meme:
    data: dict = await meme_repo.get_meme_by_id(id=meme_id)
    return schemas.Meme(**data)
