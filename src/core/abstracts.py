from abc import ABC, abstractmethod
from typing import Any

import pydantic

from src.core import models


class AbstractRepo(ABC):

    @abstractmethod
    def get_by(self, **kwargs):
        """Основная функция репозитория - отдать объект по одному или нескольким полям"""

    @abstractmethod
    def create(self, *args, **kwargs):
        """Добавляет новый объект в хранилище"""

    @abstractmethod
    class NothingFoundException:
        """Поднимается, когда репозиторий не смог отдать объект"""

    @abstractmethod
    class MultipleObjectsException:
        """Поднимается, когда репозиторий нашел несколько объектов, а должен был один"""


class AbstractDBRepo(AbstractRepo):
    """Интерфейс абстрактного репозитория, отвечающего за отдачу данных из БД"""
    schema: pydantic.BaseModel
    _model: models.Base


class AbstractMemeDbRepo(AbstractDBRepo):
    """Интерфейс абстрактного репозитория, отвечающего за отдачу мемов из БД"""

    @abstractmethod
    def get_meme_by_id(self, id: int):
        """Возвращает мем по его id"""

    @abstractmethod
    def delete_meme_by_id(self, id: int):
        """Удаляет мем по его id"""

    @abstractmethod
    def get_memes(self, as_qs: bool = False):
        """Возвращает мем по его id"""

    @abstractmethod
    class DBConstrainException:
        """Поднимается, когда запись в БД невозможна по причинам, зависящим от БД"""


class AbstractFileRepo(AbstractRepo):
    """Интерфейс абстрактного репозитория, отвечающего за отдачу файлов из хранилища"""

    client: Any
    bucket: str

    @abstractmethod
    def get_file_by_id(self, id):
        """Возвращает файл по его id"""
