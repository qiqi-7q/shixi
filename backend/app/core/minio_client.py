from io import BytesIO

from minio import Minio
from minio.error import S3Error

from app.core.config import settings

import socket


class MinioService:

    def __init__(self):
        self.client = Minio(
            f"{settings.MINIO_HOST}:{settings.MINIO_API_PORT}",
            access_key=settings.MINIO_ROOT_USER,
            secret_key=settings.MINIO_ROOT_PASSWORD,
            secure=False,
        )


    def ensure_bucket(self, bucket_name: str = None):
        bucket = bucket_name or settings.MINIO_BUCKET
        if not self.client.bucket_exists(bucket):
            self.client.make_bucket(bucket)
        return bucket

    def upload_file(
        self,
        file_data: bytes,
        object_name: str,
        bucket_name: str = None,
        content_type: str = "application/octet-stream",
    ) -> str:
        bucket = self.ensure_bucket(bucket_name)
        try:
            self.client.put_object(
                bucket_name=bucket,
                object_name=object_name,
                data=BytesIO(file_data),
                length=len(file_data),
                content_type=content_type,
            )
            return f"http://{settings.MINIO_HOST}:{settings.MINIO_API_PORT}/{bucket}/{object_name}"
        except S3Error as e:
            raise Exception(f"MinIO上传失败: {str(e)}")

    def download_file(self, object_name: str, bucket_name: str = None) -> bytes:
        bucket = bucket_name or settings.MINIO_BUCKET
        try:
            response = self.client.get_object(bucket, object_name)
            data = response.read()
            response.close()
            response.release_conn()
            return data
        except S3Error as e:
            raise Exception(f"MinIO下载失败: {str(e)}")

    def delete_file(self, object_name: str, bucket_name: str = None):
        bucket = bucket_name or settings.MINIO_BUCKET
        try:
            self.client.remove_object(bucket, object_name)
        except S3Error as e:
            raise Exception(f"MinIO删除失败: {str(e)}")

    def list_objects(self, prefix: str = "", bucket_name: str = None):
        bucket = bucket_name or settings.MINIO_BUCKET
        try:
            return list(self.client.list_objects(bucket, prefix=prefix, recursive=True))
        except S3Error as e:
            raise Exception(f"MinIO列出对象失败: {str(e)}")

    def get_object_url(self, object_name: str, bucket_name: str = None) -> str:
        bucket = bucket_name or settings.MINIO_BUCKET
        return f"http://{settings.MINIO_HOST}:{settings.MINIO_WEB_PORT}/browser/{bucket}/{object_name}"

    def conn_ping(self) -> str:
        try:
            self.ensure_bucket()
            return "MinIO连接成功"
        except Exception as e:
            return f"MinIO连接异常: {str(e)}"


minioserve = MinioService()