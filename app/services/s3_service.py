import uuid
import aioboto3
from fastapi import UploadFile, HTTPException
from app.core.config import settings


class S3Service:
    def __init__(self):
        self.session = aioboto3.Session()

    async def upload_file(self, file: UploadFile) -> str:
        """
        Загружает файл в S3 и возвращает URL.
        """
        # Генерируем уникальное имя файла, чтобы не затереть старые
        file_extension = file.filename.split(".")[-1]
        file_name = f"{uuid.uuid4()}.{file_extension}"

        try:
            async with self.session.client(
                    "s3",
                    endpoint_url=settings.S3_ENDPOINT_URL,
                    aws_access_key_id=settings.S3_ACCESS_KEY,
                    aws_secret_access_key=settings.S3_SECRET_KEY,
                    region_name=settings.S3_REGION
            ) as s3:
                # Проверяем наличие бакета, если нет - создаем
                try:
                    await s3.head_bucket(Bucket=settings.S3_BUCKET_NAME)
                except:
                    await s3.create_bucket(Bucket=settings.S3_BUCKET_NAME)

                # Загружаем файл
                # file.file - это spooled temporary file
                await s3.upload_fileobj(
                    file.file,
                    settings.S3_BUCKET_NAME,
                    file_name,
                    ExtraArgs={"ContentType": file.content_type}  # Важно для просмотра в браузере
                )

                # Формируем URL (для MinIO локально это может быть просто путь)
                # В реальном AWS S3 URL будет другим
                return f"{settings.S3_ENDPOINT_URL}/{settings.S3_BUCKET_NAME}/{file_name}"

        except Exception as e:
            print(f"S3 Upload Error: {e}")
            raise HTTPException(status_code=500, detail="Failed to upload image")