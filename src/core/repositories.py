import sqlalchemy as sa
from pydantic import BaseModel
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker, AsyncEngine

from src.config import get_settings
from src.core import schemas, models
from src.core.abstracts import AbstractMemeDbRepo, AbstractRepo

settings = get_settings()


class DBRepoBaseMixin(AbstractRepo):
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
        qs = sa.select(self._model)
        kwargs = self.filter_kwargs(kwargs)
        for field_name in kwargs:
            model_field = getattr(self._model, field_name)
            qs = qs.where(model_field == kwargs[field_name])
        try:
            async with self.session:
                results = await self.session.scalars(qs)
            obj: models.Base = results.one()
        except sa.exc.NoResultFound as _exc:
            raise self.NothingFoundException from _exc
        except sa.exc.MultipleResultsFound as _exc:
            raise self.MultipleObjectsException from _exc
        return obj

    async def _get_objects(self, as_qs: bool = False) -> list[models.Base]:
        """Возвращает список объектов с заданной позиции и количеством"""
        qs = sa.select(self._model)
        if as_qs:
            return qs
        try:
            async with self.session:
                results = await self.session.scalars(qs)  # noqa
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

    class NothingFoundException(Exception):
        message = "Nothing found"
        ...

    class MultipleObjectsException(Exception):
        message = "Found more than one object"
        ...


class MemeRepository(DBRepoBaseMixin, AbstractMemeDbRepo):
    schema = schemas.Meme
    _model = models.Meme

    async def get_meme_by_id(self, id: int) -> schemas.Meme:
        return await self.get_by(id=id, as_pd=True)

    async def get_memes(self, as_qs: bool = False, **kwargs) -> list[dict] | Select:
        return await self._get_objects(as_qs=as_qs)

    async def create_meme(self, meme: schemas.MemeCreate) -> dict:
        return await self.create(meme)

    class DBConstrainException(Exception):
        message = "Internal DB constraint"
        ...

    class NothingFoundException(Exception):
        message = "No meme found"
        ...

    class MultipleObjectsException(Exception):
        message = "Found more than one meme"
        ...
