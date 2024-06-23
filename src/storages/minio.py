from minio import Minio

from src.config import get_settings

settings = get_settings()

minio_client = Minio(endpoint=settings.minio.uri,
                     access_key=settings.minio.ROOT_USER,
                     secret_key=settings.minio.ROOT_PASSWORD,
                     secure=settings.minio.SECURE)

found = minio_client.bucket_exists(settings.minio.STORAGE_BUCKET)
if not found:
    minio_client.make_bucket(settings.minio.STORAGE_BUCKET)