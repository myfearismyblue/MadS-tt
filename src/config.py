from functools import lru_cache
from pathlib import Path
from typing import Dict

from pydantic_settings import BaseSettings


class BaseConfig(BaseSettings):
    class Config:
        env_file = Path(Path(__file__).parent, '.env')
        env_file_encoding = 'utf-8'
        frozen = True


class PostgresSettings(BaseConfig):
    HOST: str
    PORT: int
    DB: str
    USER: str
    PASSWORD: str
    DRIVER: str

    @property
    def uri(self):
        return f'{self.DRIVER}://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.DB}'

    class Config(BaseConfig.Config):
        env_prefix = 'POSTGRES_'


class WebAppSettings(BaseConfig):
    HEALTHCHECK_PATH: str
    PORT: int

    class Config(BaseConfig.Config):
        env_prefix = 'WEB_APP_'


class WebPrivateAppSettings(BaseConfig):
    API_KEY: str

    class Config(BaseConfig.Config):
        env_prefix = 'WEB_PRIVATE_APP_'


class MinioSettings(BaseConfig):
    HOST: str
    PORT: int
    CONSOLE_PORT: int
    ROOT_USER: str
    ROOT_PASSWORD: str
    STORAGE_BUCKET: str
    SECURE: bool

    @property
    def uri(self):
        return f'{self.HOST}:{self.PORT}'

    class Config(BaseConfig.Config):
        env_prefix = 'MINIO_'


class ProjectSettings(BaseSettings):
    pg: PostgresSettings = PostgresSettings()
    web_app: WebAppSettings = WebAppSettings()
    web_private: WebPrivateAppSettings = WebPrivateAppSettings()
    minio: MinioSettings = MinioSettings()
    connection_config: Dict = {
        'driver': pg.DRIVER,
        'database': pg.DB,
        'host': pg.HOST,
        'user': pg.USER,
        'password': pg.PASSWORD,
        'port': pg.PORT,
    }


@lru_cache()
def get_settings() -> ProjectSettings:
    return ProjectSettings()
