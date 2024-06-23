from abc import ABC, abstractmethod

import pydantic

from src.core import models


class AbstractRepo(ABC):
    schema: pydantic.BaseModel
    _model: models.Base

    @abstractmethod
    def get_by(self, **kwargs):
        """Основная функция репозитория - отдать объект по одному или нескольким полям"""

    @abstractmethod
    class NothingFoundException:
        """Поднимается, когда репозиторий не смог отдать объект"""

    @abstractmethod
    class MultipleObjectsException:
        """Поднимается, когда репозиторий нашел несколько объектов, а должен был один"""


class AbstractMemeDbRepo(AbstractRepo):
    """Интерфейс абстрактного репозитория, отвечающего за отдачу мемов из БД"""

    @abstractmethod
    def get_meme_by_id(self, id: int):
        """Возвращает мем по его id"""
    @abstractmethod
    def get_memes(self, as_qs: bool = False):
        """Возвращает мем по его id"""

    @abstractmethod
    class DBConstrainException:
        """Поднимается, когда запись в БД невозможна по причинам, зависящим от БД"""
