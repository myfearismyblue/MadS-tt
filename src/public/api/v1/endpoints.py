from typing import Annotated

from fastapi import APIRouter, HTTPException, File, Depends, UploadFile
from fastapi_pagination import Page
from fastapi_pagination.ext.async_sqlalchemy import paginate
from sqlalchemy import Select

from src.config import get_settings
from src.core import repositories, schemas

router = APIRouter()
settings = get_settings()
meme_repo = repositories.MemeRepository()
file_service = repositories.FileService()


@router.get("/memes", response_model=Page[schemas.Meme])
async def get_memes():
    memes_stmt: Select = await meme_repo.get_memes(as_stmt=True)
    return await paginate(meme_repo.session, memes_stmt)


@router.get("/memes/{meme_id}")
async def get_meme(meme_id: int) -> schemas.Meme:
    try:
        return await meme_repo.get_meme_by_id(id=meme_id)
    except meme_repo.NothingFoundException as _e:
        raise HTTPException(status_code=404, detail=_e.message)


@router.post("/memes/")
async def post_meme(file: UploadFile, meme: schemas.MemeCreate = Depends()) -> schemas.Meme:
    try:
        file_url, etag = await file_service.upload_file(file=file)
        meme = schemas.MemeEnriched(**meme.dict(), url=file_url, etag=etag)
        return await meme_repo.create(meme, as_pd=True)
    except meme_repo.DBConstrainException as _e:
        raise HTTPException(status_code=500, detail=_e.message)



