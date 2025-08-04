import os
import uuid
from datetime import timedelta
from minio import Minio
from minio.error import S3Error
from django.conf import settings
from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)


class MinioService:
    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_USE_SSL
        )
        self.bucket_name = settings.MINIO_BUCKET_NAME
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        """Create bucket if it doesn't exist."""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                logger.info(f"Created bucket: {self.bucket_name}")
        except S3Error as e:
            logger.error(f"Error creating bucket: {e}")
            raise ValidationError(f"Failed to create storage bucket: {str(e)}")

    def upload_file(self, file, folder="uploads"):
        """
        Upload a file to MinIO and return the filename.
        
        Args:
            file: Django UploadedFile instance
            folder: Folder path in MinIO bucket
            
        Returns:
            str: The filename of the uploaded file
        """
        try:
            # Generate unique filename
            file_extension = os.path.splitext(file.name)[1].lower()
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            object_name = f"{folder}/{unique_filename}"
            
            # Reset file pointer to beginning
            file.seek(0)
            
            # Upload file
            self.client.put_object(
                self.bucket_name,
                object_name,
                file,
                file.size,
                content_type=file.content_type
            )
            
            logger.info(f"File uploaded successfully: {object_name}")
            return unique_filename
            
        except S3Error as e:
            logger.error(f"Error uploading file: {e}")
            raise ValidationError(f"Failed to upload file: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error uploading file: {e}")
            raise ValidationError(f"Unexpected error: {str(e)}")

    def delete_file(self, filename, folder="uploads"):
        """
        Delete a file from MinIO.
        
        Args:
            filename: Name of the file to delete
            folder: Folder path in MinIO bucket
        """
        try:
            object_name = f"{folder}/{filename}"
            self.client.remove_object(self.bucket_name, object_name)
            logger.info(f"File deleted successfully: {object_name}")
        except S3Error as e:
            logger.error(f"Error deleting file: {e}")
            raise ValidationError(f"Failed to delete file: {str(e)}")

    def get_file_url(self, filename, folder="uploads", expires=3600):
        """
        Get a presigned URL for a file.
        
        Args:
            filename: Name of the file
            folder: Folder path in MinIO bucket
            expires: URL expiration time in seconds
            
        Returns:
            str: Presigned URL
        """
        try:
            object_name = f"{folder}/{filename}"
            # Convert seconds to timedelta if needed
            if isinstance(expires, int):
                expires = timedelta(seconds=expires)
            
            url = self.client.presigned_get_object(
                self.bucket_name, 
                object_name, 
                expires=expires
            )
            return url
        except S3Error as e:
            logger.error(f"Error generating file URL: {e}")
            raise ValidationError(f"Failed to generate file URL: {str(e)}")


# Global instance
minio_service = MinioService()