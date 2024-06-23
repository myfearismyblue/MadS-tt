from typing import Annotated

from fastapi import APIRouter, HTTPException, File, Depends, UploadFile
from fastapi_pagination import Page
from fastapi_pagination.ext.async_sqlalchemy import paginate
from sqlalchemy import Select
from starlette.responses import Response

from src.config import get_settings
from src.core import repositories, schemas

router = APIRouter()
settings = get_settings()
meme_repo = repositories.MemeRepository()
file_service = repositories.FileService()


# @router.put("/memes/{meme_id}")
# async def put_meme(meme_id: int) -> schemas.Meme:
#     try:
#         return await meme_repo.get_meme_by_id(id=meme_id)
#     except meme_repo.NothingFoundException as _e:
#         raise HTTPException(status_code=404, detail=_e.message)


@router.delete("/memes/{meme_id}")
async def delete_meme(meme_id: int):
    try:
        await meme_repo.delete_meme_by_id(id=meme_id)
        return Response(status_code=200)

    except meme_repo.NothingFoundException as _e:
        raise HTTPException(status_code=404, detail=_e.message)
    except meme_repo.DBConstrainException as _e:
        raise HTTPException(status_code=500, detail=_e.message)



