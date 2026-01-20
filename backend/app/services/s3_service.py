"""
S3 service for media file management.
"""
import logging
import uuid
from typing import Optional
from fastapi import UploadFile
import boto3
from botocore.exceptions import ClientError

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class S3Service:
    """Service for managing files in AWS S3."""

    def __init__(self):
        """Initialize S3 client with credentials from settings."""
        self.bucket_name = settings.S3_BUCKET
        self.region = settings.AWS_REGION

        # Initialize boto3 client
        self.client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
        )

    def _generate_key(self, user_id: int, filename: str) -> str:
        """Generate a unique S3 key for the file.

        Args:
            user_id: User ID for namespacing
            filename: Original filename

        Returns:
            S3 key with user prefix and UUID
        """
        file_uuid = str(uuid.uuid4())
        # Extract extension from filename
        ext = filename.rsplit(".", 1)[-1] if "." in filename else ""
        if ext:
            return f"posts/{user_id}/{file_uuid}.{ext}"
        return f"posts/{user_id}/{file_uuid}"

    async def upload_file(
        self,
        file: UploadFile,
        user_id: int,
    ) -> dict:
        """Upload a file to S3.

        Args:
            file: FastAPI UploadFile object
            user_id: User ID for namespacing

        Returns:
            Dict with s3_url, s3_key, filename, and content_type

        Raises:
            Exception: If upload fails
        """
        try:
            # Generate unique key
            s3_key = self._generate_key(user_id, file.filename or "upload")

            # Read file content
            content = await file.read()

            # Upload to S3
            self.client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=content,
                ContentType=file.content_type or "application/octet-stream",
            )

            # Construct URL
            s3_url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{s3_key}"

            logger.info(f"Uploaded file to S3: {s3_key}")

            return {
                "s3_url": s3_url,
                "s3_key": s3_key,
                "filename": file.filename or "upload",
                "content_type": file.content_type or "application/octet-stream",
            }

        except ClientError as e:
            logger.error(f"Failed to upload file to S3: {str(e)}")
            raise Exception(f"Failed to upload file to S3: {str(e)}")

    def delete_file(self, s3_key: str) -> bool:
        """Delete a file from S3.

        Args:
            s3_key: S3 key of the file to delete

        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            self.client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key,
            )
            logger.info(f"Deleted file from S3: {s3_key}")
            return True

        except ClientError as e:
            logger.error(f"Failed to delete file from S3: {str(e)}")
            return False

    def generate_presigned_url(
        self,
        s3_key: str,
        expiration: int = 3600,
    ) -> Optional[str]:
        """Generate a presigned URL for private bucket access.

        Args:
            s3_key: S3 key of the file
            expiration: URL expiration time in seconds (default 1 hour)

        Returns:
            Presigned URL or None if generation fails
        """
        try:
            url = self.client.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": self.bucket_name,
                    "Key": s3_key,
                },
                ExpiresIn=expiration,
            )
            return url

        except ClientError as e:
            logger.error(f"Failed to generate presigned URL: {str(e)}")
            return None

    def extract_key_from_url(self, s3_url: str) -> Optional[str]:
        """Extract S3 key from a full S3 URL.

        Args:
            s3_url: Full S3 URL

        Returns:
            S3 key or None if extraction fails
        """
        try:
            # Handle format: https://bucket.s3.region.amazonaws.com/key
            if f"{self.bucket_name}.s3." in s3_url:
                return s3_url.split(f"{self.bucket_name}.s3.{self.region}.amazonaws.com/")[-1]
            return None

        except Exception:
            return None


# Singleton instance
_s3_service: Optional[S3Service] = None


def get_s3_service() -> S3Service:
    """Get S3 service singleton instance."""
    global _s3_service
    if _s3_service is None:
        _s3_service = S3Service()
    return _s3_service
