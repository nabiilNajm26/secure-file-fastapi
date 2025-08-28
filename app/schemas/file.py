from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class FileBase(BaseModel):
    description: Optional[str] = None
    is_public: bool = False


class FileUpload(FileBase):
    pass


class FileUpdate(BaseModel):
    description: Optional[str] = None
    is_public: Optional[bool] = None


class FileInDBBase(FileBase):
    id: int
    filename: str
    original_filename: str
    file_path: str
    file_size: float
    content_type: str
    file_extension: Optional[str]
    
    is_image: bool
    width: Optional[int]
    height: Optional[int]
    thumbnail_path: Optional[str]
    
    download_count: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class File(FileInDBBase):
    pass


class FileList(BaseModel):
    files: list[File]
    total: int
    page: int
    size: int


class FileUploadResponse(BaseModel):
    id: int
    filename: str
    original_filename: str
    file_size: float
    content_type: str
    download_url: str
    thumbnail_url: Optional[str] = None
    created_at: datetime