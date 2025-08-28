import io
import uuid
from typing import Optional, List, BinaryIO
from datetime import datetime
from fastapi import UploadFile
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.storage import storage_client
from app.models.file import File
from app.models.user import User
from app.schemas.file import FileUpload, FileUpdate
from app.utils.image import ImageProcessor


class FileService:
    @staticmethod
    def generate_unique_filename(original_filename: str) -> str:
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        extension = original_filename.rsplit('.', 1)[-1] if '.' in original_filename else ''
        return f"{timestamp}_{unique_id}.{extension}" if extension else f"{timestamp}_{unique_id}"
    
    @staticmethod
    def validate_file(file: UploadFile) -> tuple[bool, str]:
        # Check file size
        if file.size and file.size > settings.max_file_size:
            return False, f"File size exceeds maximum allowed size of {settings.max_file_size} bytes"
        
        # Check file extension
        if file.filename:
            extension = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
            if extension and extension not in settings.allowed_extensions_list:
                return False, f"File type .{extension} is not allowed"
        
        return True, "Valid"
    
    @staticmethod
    async def upload_file(
        db: Session,
        file: UploadFile,
        user: User,
        description: Optional[str] = None,
        is_public: bool = False
    ) -> Optional[File]:
        # Validate file
        is_valid, message = FileService.validate_file(file)
        if not is_valid:
            raise ValueError(message)
        
        # Read file data
        file_data = await file.read()
        file_size = len(file_data)
        
        # Generate unique filename
        unique_filename = FileService.generate_unique_filename(file.filename)
        
        # Process image if applicable
        thumbnail_path = None
        width = None
        height = None
        is_image = ImageProcessor.is_image(file.content_type)
        
        if is_image:
            # Get image dimensions
            image_info = ImageProcessor.get_image_info(file_data)
            if image_info:
                width, height, _ = image_info
            
            # Create and upload thumbnail
            thumbnail_data = ImageProcessor.create_thumbnail(file_data)
            if thumbnail_data:
                thumbnail_filename = f"thumb_{unique_filename}"
                thumbnail_io = io.BytesIO(thumbnail_data)
                storage_client.upload_file(
                    thumbnail_io,
                    f"thumbnails/{thumbnail_filename}",
                    "image/jpeg",
                    len(thumbnail_data)
                )
                thumbnail_path = f"thumbnails/{thumbnail_filename}"
            
            # Optimize original image
            optimized_data = ImageProcessor.optimize_image(file_data)
            if optimized_data:
                file_data = optimized_data
                file_size = len(file_data)
        
        # Upload to MinIO
        file_io = io.BytesIO(file_data)
        object_path = f"uploads/{user.id}/{unique_filename}"
        
        success = storage_client.upload_file(
            file_io,
            object_path,
            file.content_type,
            file_size
        )
        
        if not success:
            raise ValueError("Failed to upload file to storage")
        
        # Save metadata to database
        db_file = File(
            filename=unique_filename,
            original_filename=file.filename,
            file_path=object_path,
            file_size=file_size,
            content_type=file.content_type,
            file_extension=file.filename.rsplit('.', 1)[-1] if '.' in file.filename else None,
            is_image=is_image,
            width=width,
            height=height,
            thumbnail_path=thumbnail_path,
            description=description,
            is_public=is_public,
            user_id=user.id
        )
        
        db.add(db_file)
        db.commit()
        db.refresh(db_file)
        
        return db_file
    
    @staticmethod
    def get_file(db: Session, file_id: int) -> Optional[File]:
        return db.query(File).filter(File.id == file_id).first()
    
    @staticmethod
    def get_user_files(
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[File]:
        return db.query(File).filter(
            File.user_id == user_id
        ).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_public_files(
        db: Session,
        skip: int = 0,
        limit: int = 100
    ) -> List[File]:
        return db.query(File).filter(
            File.is_public == True
        ).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_file(
        db: Session,
        file: File,
        file_update: FileUpdate
    ) -> File:
        update_data = file_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(file, field, value)
        
        db.add(file)
        db.commit()
        db.refresh(file)
        return file
    
    @staticmethod
    def delete_file(db: Session, file: File) -> bool:
        # Delete from MinIO
        storage_client.delete_file(file.file_path)
        
        # Delete thumbnail if exists
        if file.thumbnail_path:
            storage_client.delete_file(file.thumbnail_path)
        
        # Delete from database
        db.delete(file)
        db.commit()
        return True
    
    @staticmethod
    def increment_download_count(db: Session, file: File) -> None:
        file.download_count += 1
        db.add(file)
        db.commit()
    
    @staticmethod
    def get_file_download_url(file: File, expires: int = 3600) -> Optional[str]:
        return storage_client.get_file_url(file.file_path, expires)
    
    @staticmethod
    def get_thumbnail_url(file: File, expires: int = 3600) -> Optional[str]:
        if file.thumbnail_path:
            return storage_client.get_file_url(file.thumbnail_path, expires)
        return None