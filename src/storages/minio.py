from minio import Minio

from src.config import get_settings

settings = get_settings()

minio_client = Minio(endpoint=settings.minio.uri,
                     access_key=settings.minio.ROOT_USER,
                     secret_key=settings.minio.ROOT_PASSWORD,
                     secure=settings.minio.SECURE)

