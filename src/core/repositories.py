import io
import uuid
from urllib.parse import urlparse

import sqlalchemy as sa
from fastapi import UploadFile
from minio import error
from pydantic import BaseModel
from sqlalchemy import Select, delete
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker, AsyncEngine

from src.config import get_settings
from src.core import schemas, models
from src.core.abstracts import AbstractMemeDbRepo, AbstractDBRepo, AbstractFileRepo
from src.storages.minio import minio_client

settings = get_settings()


class DBRepoBaseMixin(AbstractDBRepo):
    def __init__(self, connection_config: dict = None, pool_size: int = None, max_overflow: int = None):
        """
        Прокидывает информацию для подключения к БД
        """
        self._cfg = connection_config

        self._engine: AsyncEngine = create_async_engine(settings.pg.uri,
                                                        pool_size=pool_size or 5,
                                                        max_overflow=max_overflow or 10,
                                                        echo=True)
        self.session: AsyncSession = async_sessionmaker(self._engine, class_=AsyncSession, expire_on_commit=False)()

    async def _get_object_by(self, **kwargs) -> models.Base:
        """Возвращает объект sqlalchemy по любым аттрибутам модели"""
        stmt = sa.select(self._model)
        kwargs = self.filter_kwargs(kwargs)
        for field_name in kwargs:
            model_field = getattr(self._model, field_name)
            stmt = stmt.where(model_field == kwargs[field_name])
        try:
            async with self.session:
                results = await self.session.scalars(stmt)
            obj: models.Base = results.one()
        except sa.exc.NoResultFound as _exc:
            raise self.NothingFoundException from _exc
        except sa.exc.MultipleResultsFound as _exc:
            raise self.MultipleObjectsException from _exc
        return obj

    async def _get_objects(self, as_stmt: bool = False) -> list[models.Base]:
        """Возвращает список объектов с заданной позиции и количеством"""
        stmt = sa.select(self._model)
        if as_stmt:
            return stmt
        try:
            async with self.session:
                results = await self.session.scalars(stmt)  # noqa
        except sa.exc.NoResultFound as _exc:
            return list()
        return list(results)

    async def get_by(self, as_pd: bool = False, **kwargs) -> dict | BaseModel:
        """Возвращает объект как словарь или как объект Pydantic"""
        obj = await self._get_object_by(**kwargs)
        return self.schema.from_orm(obj) if as_pd else obj.__dict__

    def filter_kwargs(self, kwargs: dict) -> dict:
        """Выбрасывает kw, не являющиеся столбцами модели"""
        ret: dict = {}
        for key in kwargs:
            if key in self._model.__table__.columns.keys():
                ret.update({key: kwargs[key]})
        return ret

    async def _create_obj(self, pd_obj: BaseModel) -> models.Base:
        """Создает объект в БД"""
        obj = self._model(**{**pd_obj.dict(), 'id': None})
        async with self.session:
            self.session.add(obj)
            await self.session.commit()
            await self.session.refresh(obj)
        return obj

    async def create(self, pd_obj: BaseModel, as_pd: bool = False) -> dict | BaseModel:
        """Создает объект в БД и возвращает его как словарь"""
        obj: models.Base = await self._create_obj(pd_obj)
        return self.schema.from_orm(obj) if as_pd else obj.__dict__

    async def update_or_create(self, *,
                               filter: dict,
                               data: dict,
                               partial=False,
                               as_pd: bool = False) -> dict | BaseModel:
        """
        Созадет или обновляет объект, отфильтрованный по ключам и значениям словаря filter данными из data.
        Если partial==False, то поля объекта будут обновлены значением None, если такие поля отсутствуют в data.
        """
        data: dict = self.filter_kwargs(data)
        try:
            obj: models.Base = await self._get_object_by(**filter)
            _obj: models.Base = await self.session.merge(obj)  # локальная копия объекта, чтобы избежать конфликта сессий
            # перебираем все ключи модели, если partial==false, иначе перебираем ключи из данных
            for key in data if partial else self._model.__table__.columns.keys():
                # если поле - primary, то его не обновляем
                if getattr(getattr(self._model, key), 'primary_key'):
                    continue
                field, value = key, data[key]
                setattr(_obj, field, value) if (value is not None or not partial) else None
        except self.NothingFoundException:
            _obj: models.Base = self._model(**data)
            self.session.add(_obj)
        await self.session.commit()
        return self.schema.from_orm(_obj) if as_pd else _obj.__dict__

    async def partial_update_or_create(self, *, filter: dict, data: dict, as_pd: bool = False) -> dict:
        return await self.update_or_create(filter=filter, data=data, partial=True, as_pd=as_pd)

    class NothingFoundException(Exception):
        message = "Nothing found"
        ...

    class MultipleObjectsException(Exception):
        message = "Found more than one object"
        ...


class MemeRepository(DBRepoBaseMixin, AbstractMemeDbRepo):
    """Репозиторий для работы с мемами. Синглтон, инстанцируется только в один экземпляр."""
    schema = schemas.Meme
    _model = models.Meme

    _self = None

    def __new__(cls, *args, **kwargs):
        if cls._self:
            return cls._self
        cls._self = super().__new__(cls, *args, **kwargs)
        return cls._self

    async def get_meme_by_id(self, id: int) -> schemas.Meme:
        return await self.get_by(id=id, as_pd=True)

    async def get_memes(self, as_stmt: bool = False, **kwargs) -> list[dict] | Select:
        return await self._get_objects(as_stmt=as_stmt)

    async def create_meme(self, meme: schemas.MemeCreate) -> dict:
        return await self.create(meme)

    async def delete_meme_by_id(self, id: int):
        async with self.session:
            stmt = sa.delete(self._model).where(self._model.id == id)
            await self.session.execute(stmt)
            await self.session.commit()

    @staticmethod
    def _parse_name(url: str) -> str:
        path = urlparse(url).path
        return path.split('/')[-1]

    async def get_meme_file_name(self, id: int) -> str:
        obj = await self.get_by(id=id, as_pd=True)
        name: str = self._parse_name(obj.url)
        return name

    async def get_etag(self, id: int) -> str:
        obj: schemas.Meme = await self.get_by(id=id, as_pd=True)
        return obj.etag

    async def is_etag_unique(self, etag: str) -> bool:
        try:
            await self._get_object_by(etag=etag)
            return True
        except self.MultipleObjectsException:
            return False



    class DBConstrainException(Exception):
        message = "Internal DB constraint"

    class NothingFoundException(Exception):
        message = "No meme found"

    class MultipleObjectsException(Exception):
        message = "Found more than one meme"


class FileService(AbstractFileRepo):
    """Репозиторий для работы с файлами. Синглтон, инстанцируется только в один экземпляр."""
    client = minio_client
    bucket = settings.minio.STORAGE_BUCKET

    _self = None

    def __new__(cls, *args, **kwargs):
        if cls._self:
            return cls._self
        cls._self = super().__new__(cls, *args, **kwargs)
        return cls._self

    async def get_by(self, **kwargs):
        id_ = kwargs.get('id')
        if not id_:
            raise NotImplementedError('File id should be provided')
        pass

    async def get_file_by_id(self, id):
        return await self.get_by(id=id)

    async def create(self, data: bytes, filename: str, content_type: str) -> (str, str):
        file_buffer = io.BytesIO(data)
        file_buffer.seek(0)
        length_ = file_buffer.getbuffer().nbytes

        result = self.client.put_object(self.bucket, filename, file_buffer, length=length_, content_type=content_type)
        url = self.client.get_presigned_url("GET", self.bucket, filename)
        return url, result.etag

    def _prevent_file_rewriting(self, filename: str) -> str:
        """
        Возвращает новое название файла, если файл с таким названием уже существует.
        Если перезаписывать файл другим содержанием и таким же названием,
        то все ссылки старые ссылки будут вести на файл с новым содержанием.
        """
        try:
            while self.client.stat_object(self.bucket, filename):
                filename = f'{filename}{str(uuid.uuid4())}'
        except error.S3Error:
            pass
        return filename

    async def upload_file(self, file: UploadFile, prevent_rewriting: bool = True) -> (str, str):
        data = await file.read()
        filename = getattr(file, 'filename') or f'file{str(uuid.uuid4())}'
        if prevent_rewriting:
            filename = self._prevent_file_rewriting(filename)
        content_type = getattr(file, 'content_type') or 'image/jpeg'
        return await self.create(data, filename, content_type)

    async def delete_file_by_name(self, name: str) -> None:
        try:
            return self.client.remove_object(self.bucket, name)
        except error.S3Error:
            raise self.NothingFoundException

    async def get_etag_by_name(self, name: str) -> str:
        try:
            return self.client.stat_object(self.bucket, name).etag
        except error.S3Error:
            raise self.NothingFoundException

    # async def _delete_file_by_etag(self, etag: str) -> None:
    #     self.client

    class DBConstrainException(Exception):
        message = "Internal storage error"

    class NothingFoundException(Exception):
        message = "File not found"

    class MultipleObjectsException(Exception):
        message = "Found more than one file"
