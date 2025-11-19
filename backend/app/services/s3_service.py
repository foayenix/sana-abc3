"""AWS S3 service for file uploads."""

import boto3
from botocore.exceptions import ClientError
from typing import Optional
import uuid
from datetime import datetime
from app.core.config import settings


class S3Service:
    """Service for handling file uploads to AWS S3."""

    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
        )
        self.bucket_name = settings.S3_BUCKET_NAME

    def _generate_key(self, folder: str, filename: str) -> str:
        """Generate unique S3 key for file."""
        ext = filename.split('.')[-1] if '.' in filename else ''
        unique_id = uuid.uuid4().hex[:8]
        timestamp = datetime.utcnow().strftime('%Y%m%d')
        return f"{folder}/{timestamp}/{unique_id}.{ext}"

    async def upload_file(
        self,
        file_content: bytes,
        filename: str,
        folder: str = "uploads",
        content_type: Optional[str] = None,
        public: bool = False,
    ) -> dict:
        """Upload file to S3."""
        try:
            key = self._generate_key(folder, filename)

            extra_args = {}
            if content_type:
                extra_args['ContentType'] = content_type
            if public:
                extra_args['ACL'] = 'public-read'

            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=file_content,
                **extra_args,
            )

            url = f"https://{self.bucket_name}.s3.amazonaws.com/{key}"

            return {
                "success": True,
                "key": key,
                "url": url,
            }
        except ClientError as e:
            return {
                "success": False,
                "error": str(e),
            }

    async def get_presigned_url(
        self,
        key: str,
        expiration: int = 3600,
    ) -> Optional[str]:
        """Generate presigned URL for private file access."""
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': key,
                },
                ExpiresIn=expiration,
            )
            return url
        except ClientError:
            return None

    async def get_presigned_upload_url(
        self,
        key: str,
        content_type: str,
        expiration: int = 3600,
    ) -> Optional[dict]:
        """Generate presigned URL for direct upload."""
        try:
            url = self.s3_client.generate_presigned_url(
                'put_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': key,
                    'ContentType': content_type,
                },
                ExpiresIn=expiration,
            )
            return {
                "upload_url": url,
                "key": key,
            }
        except ClientError:
            return None

    async def delete_file(self, key: str) -> bool:
        """Delete file from S3."""
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=key,
            )
            return True
        except ClientError:
            return False

    async def list_files(
        self,
        prefix: str = "",
        max_keys: int = 100,
    ) -> list:
        """List files in S3 bucket with prefix."""
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix,
                MaxKeys=max_keys,
            )
            return [
                {
                    "key": obj['Key'],
                    "size": obj['Size'],
                    "last_modified": obj['LastModified'].isoformat(),
                }
                for obj in response.get('Contents', [])
            ]
        except ClientError:
            return []


# File type helpers
class FileTypes:
    """Allowed file types and content types."""

    IMAGES = {
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png',
        'gif': 'image/gif',
        'webp': 'image/webp',
    }

    DOCUMENTS = {
        'pdf': 'application/pdf',
        'doc': 'application/msword',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    }

    @classmethod
    def get_content_type(cls, filename: str) -> Optional[str]:
        """Get content type for filename."""
        ext = filename.lower().split('.')[-1] if '.' in filename else ''
        return cls.IMAGES.get(ext) or cls.DOCUMENTS.get(ext)

    @classmethod
    def is_allowed(cls, filename: str) -> bool:
        """Check if file type is allowed."""
        ext = filename.lower().split('.')[-1] if '.' in filename else ''
        return ext in cls.IMAGES or ext in cls.DOCUMENTS


s3_service = S3Service()
