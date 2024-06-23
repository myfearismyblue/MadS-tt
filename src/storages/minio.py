import functools

from minio import Minio

from src.config import get_settings

settings = get_settings()

minio_client = Minio(endpoint=settings.minio.uri,
                     access_key=settings.minio.ROOT_USER,
                     secret_key=settings.minio.ROOT_PASSWORD,
                     secure=settings.minio.SECURE)


@functools.lru_cache
def _bucket_exist():
    return minio_client.bucket_exists(settings.minio.STORAGE_BUCKET)


if not _bucket_exist:
    minio_client.make_bucket(settings.minio.STORAGE_BUCKET)
