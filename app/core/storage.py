import io
from typing import BinaryIO, Optional
from minio import Minio
from minio.error import S3Error
from app.core.config import settings
from app.core.storage_fallback import local_storage_client


class MinIOClient:
    def __init__(self):
        self.client = None
        self.bucket_name = settings.minio_bucket_name
        self._client_initialized = False
    
    def _init_client(self):
        """Initialize MinIO client lazily"""
        if not self._client_initialized:
            try:
                self.client = Minio(
                    settings.minio_endpoint,
                    access_key=settings.minio_access_key,
                    secret_key=settings.minio_secret_key,
                    secure=settings.minio_secure
                )
                self._ensure_bucket_exists()
                self._client_initialized = True
            except Exception as e:
                print(f"Warning: MinIO client initialization failed: {e}")
                self.client = None
    
    def _ensure_bucket_exists(self):
        if not self.client:
            return
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
        except S3Error as e:
            print(f"Error creating bucket: {e}")
    
    def upload_file(
        self, 
        file_data: BinaryIO, 
        object_name: str, 
        content_type: str,
        file_size: int
    ) -> bool:
        self._init_client()
        if not self.client:
            print("MinIO not available, using local storage fallback")
            return local_storage_client.upload_file(file_data, object_name, content_type, file_size)
        try:
            self.client.put_object(
                self.bucket_name,
                object_name,
                file_data,
                file_size,
                content_type=content_type
            )
            return True
        except S3Error as e:
            print(f"Error uploading file to MinIO: {e}, falling back to local storage")
            # Reset file pointer if possible
            if hasattr(file_data, 'seek'):
                file_data.seek(0)
            return local_storage_client.upload_file(file_data, object_name, content_type, file_size)
    
    def download_file(self, object_name: str) -> Optional[bytes]:
        self._init_client()
        if not self.client:
            return local_storage_client.download_file(object_name)
        try:
            response = self.client.get_object(self.bucket_name, object_name)
            data = response.read()
            response.close()
            response.release_conn()
            return data
        except S3Error as e:
            print(f"Error downloading file from MinIO: {e}, trying local storage")
            return local_storage_client.download_file(object_name)
    
    def delete_file(self, object_name: str) -> bool:
        self._init_client()
        if not self.client:
            return local_storage_client.delete_file(object_name)
        try:
            self.client.remove_object(self.bucket_name, object_name)
            return True
        except S3Error as e:
            print(f"Error deleting file from MinIO: {e}, trying local storage")
            return local_storage_client.delete_file(object_name)
    
    def get_file_url(self, object_name: str, expires: int = 3600) -> Optional[str]:
        self._init_client()
        if not self.client:
            return local_storage_client.get_file_url(object_name, expires)
        try:
            from datetime import timedelta
            url = self.client.presigned_get_object(
                self.bucket_name,
                object_name,
                expires=timedelta(seconds=expires)
            )
            return url
        except S3Error as e:
            print(f"Error generating MinIO URL: {e}, using local storage URL")
            return local_storage_client.get_file_url(object_name, expires)
    
    def file_exists(self, object_name: str) -> bool:
        try:
            self.client.stat_object(self.bucket_name, object_name)
            return True
        except S3Error:
            return False


# Global MinIO client instance
storage_client = MinIOClient()