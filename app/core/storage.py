import logging
import uuid
import boto3
from botocore.exceptions import ClientError
from fastapi import UploadFile, HTTPException, status
from anyio import to_thread

from app.core.config import settings

logger = logging.getLogger(__name__)

class CloudStorage:
    def __init__(self):
        self.s3_client = None
        if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
            self.s3_client = boto3.client(
                "s3",
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION,
                endpoint_url=settings.S3_ENDPOINT_URL,
            )

    async def upload_file(self, file: UploadFile, folder: str = "submissions") -> str:
        """
        Uploads a file to the S3 bucket and returns the public URL.
        """
        if not self.s3_client:
            logger.warning("Cloud Storage not configured. Falling back to mock URL.")
            return f"https://mock-storage.com/{folder}/{file.filename}"

        # Generate a unique filename to prevent collisions
        file_ext = file.filename.split(".")[-1] if "." in file.filename else ""
        unique_filename = f"{folder}/{uuid.uuid4()}.{file_ext}"

        try:
            # Read file content safely
            content = await file.read()
            
            # Execute blocking upload in a thread pool
            await to_thread.run_sync(
                self.s3_client.put_object,
                {
                    "Bucket": settings.S3_BUCKET_NAME,
                    "Key": unique_filename,
                    "Body": content,
                    "ContentType": file.content_type,
                }
            )
            
            # Reset file pointer if needed (though we already read it)
            await file.seek(0)
            
            # Construct the public URL
            # Note: For Supabase, the URL structure is usually:
            # {ENDPOINT_URL}/storage/v1/s3/object/public/{BUCKET}/{KEY}
            # However, if using the standard S3 endpoint, it depends on the provider.
            # We'll assume a standard path or let the user configure the full base URL.
            
            base_url = settings.S3_ENDPOINT_URL.rstrip("/")
            if "supabase.co" in base_url:
                # Custom Supabase Public URL construction
                project_ref = base_url.split("//")[1].split(".")[0]
                return f"https://{project_ref}.supabase.co/storage/v1/object/public/{settings.S3_BUCKET_NAME}/{unique_filename}"
            
            return f"{base_url}/{settings.S3_BUCKET_NAME}/{unique_filename}"

        except ClientError as e:
            logger.error(f"Failed to upload file to S3: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not upload file to cloud storage"
            )
        except Exception as e:
            logger.error(f"Unexpected error during file upload: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred during file upload"
            )

storage_service = CloudStorage()
