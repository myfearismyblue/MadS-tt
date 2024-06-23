from fastapi import APIRouter, HTTPException, Depends, UploadFile
from starlette.responses import Response

from src.config import get_settings
from src.core import repositories, schemas

router = APIRouter()
settings = get_settings()
meme_repo = repositories.MemeRepository()
file_service = repositories.FileService()


@router.put("/memes/{meme_id}")
async def put_meme(meme_id: int, file: UploadFile, meme: schemas.MemeCreate = Depends()) -> schemas.Meme:
    """
    Заменяет объект целиком, включая файл.
    Если файл объекта используется, только в текущем меме, то удаляет старый файл.
    """
    try:

        etag: str = await meme_repo.get_etag(id=meme_id)
        file_not_shared: bool = await meme_repo.is_etag_unique(etag=etag)
        if file_not_shared:
            name: str = await meme_repo.get_meme_file_name(id=meme_id)
            await file_service.delete_file_by_name(name=name)
        new_file_url, new_etag = await file_service.upload_file(file=file)
        new_meme = schemas.MemeEnriched(**meme.dict(), url=new_file_url, etag=new_etag)
        return await meme_repo.update_or_create(filter={"id": meme_id},     # noqa
                                                data=new_meme.model_dump(),
                                                as_pd=True)
    except meme_repo.NothingFoundException as _e:
        raise HTTPException(status_code=404, detail=_e.message)


@router.delete("/memes/{meme_id}")
async def delete_meme(meme_id: int):
    """
    Удаляет объект целиком, включая файл, если файл объекта используется, только в текущем меме.
    """
    try:
        etag: str = await meme_repo.get_etag(id=meme_id)
        file_not_shared: bool = await meme_repo.is_etag_unique(etag=etag)
        if file_not_shared:
            name: str = await meme_repo.get_meme_file_name(id=meme_id)
            await file_service.delete_file_by_name(name=name)
        await meme_repo.delete_meme_by_id(id=meme_id)
        return Response(status_code=200)

    except meme_repo.NothingFoundException as _e:
        raise HTTPException(status_code=404, detail=_e.message)
    except meme_repo.DBConstrainException as _e:
        raise HTTPException(status_code=500, detail=_e.message)



