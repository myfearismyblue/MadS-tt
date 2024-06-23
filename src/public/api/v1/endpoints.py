from fastapi import APIRouter, HTTPException
from fastapi_pagination import Page
from fastapi_pagination.ext.async_sqlalchemy import paginate
from sqlalchemy import Select

from src.config import get_settings
from src.core import repositories, schemas

router =  APIRouter()
settings = get_settings()
meme_repo = repositories.MemeRepository()


@router.get("/memes", response_model=Page[schemas.Meme])
async def get_memes():
    memes_qs: Select = await meme_repo.get_memes(as_qs=True)
    return await paginate(meme_repo.session, memes_qs)


@router.get("/memes/{meme_id}")
async def get_meme(meme_id: int) -> schemas.Meme:
    try:
        return await meme_repo.get_meme_by_id(id=meme_id)
    except meme_repo.NothingFoundException as _e:
        raise HTTPException(status_code=404, detail=_e.message)


@router.post("/memes/")
async def post_meme(meme: schemas.MemeCreate) -> schemas.Meme:
    try:
        return await meme_repo.create(meme, as_pd=True)
    except meme_repo.DBConstrainException as _e:
        raise HTTPException(status_code=500, detail=_e.message)



