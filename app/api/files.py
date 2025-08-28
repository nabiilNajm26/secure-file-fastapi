from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File as FastAPIFile, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import io
from app.core.deps import get_db, get_current_active_user, get_current_verified_user
from app.core.storage import storage_client
from app.models.user import User as UserModel
from app.models.file import File as FileModel
from app.schemas.file import File, FileList, FileUpdate, FileUploadResponse
from app.services.file_service import FileService

router = APIRouter(prefix="/files", tags=["Files"])


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = FastAPIFile(...),
    description: Optional[str] = Form(None),
    is_public: bool = Form(False),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_verified_user)
):
    try:
        uploaded_file = await FileService.upload_file(
            db=db,
            file=file,
            user=current_user,
            description=description,
            is_public=is_public
        )
        
        if not uploaded_file:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to upload file"
            )
        
        # Get download URL
        download_url = FileService.get_file_download_url(uploaded_file)
        thumbnail_url = FileService.get_thumbnail_url(uploaded_file) if uploaded_file.is_image else None
        
        return FileUploadResponse(
            id=uploaded_file.id,
            filename=uploaded_file.filename,
            original_filename=uploaded_file.original_filename,
            file_size=uploaded_file.file_size,
            content_type=uploaded_file.content_type,
            download_url=download_url or "",
            thumbnail_url=thumbnail_url,
            created_at=uploaded_file.created_at
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/upload-multiple", response_model=List[FileUploadResponse])
async def upload_multiple_files(
    files: List[UploadFile] = FastAPIFile(...),
    is_public: bool = Form(False),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_verified_user)
):
    if len(files) > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 10 files can be uploaded at once"
        )
    
    uploaded_files = []
    for file in files:
        try:
            uploaded_file = await FileService.upload_file(
                db=db,
                file=file,
                user=current_user,
                is_public=is_public
            )
            
            if uploaded_file:
                download_url = FileService.get_file_download_url(uploaded_file)
                thumbnail_url = FileService.get_thumbnail_url(uploaded_file) if uploaded_file.is_image else None
                
                uploaded_files.append(FileUploadResponse(
                    id=uploaded_file.id,
                    filename=uploaded_file.filename,
                    original_filename=uploaded_file.original_filename,
                    file_size=uploaded_file.file_size,
                    content_type=uploaded_file.content_type,
                    download_url=download_url or "",
                    thumbnail_url=thumbnail_url,
                    created_at=uploaded_file.created_at
                ))
        except ValueError as e:
            # Skip files that fail validation
            continue
    
    return uploaded_files


@router.get("/", response_model=FileList)
def get_user_files(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    files = FileService.get_user_files(db, current_user.id, skip, limit)
    total = db.query(FileModel).filter(FileModel.user_id == current_user.id).count()
    
    return FileList(
        files=files,
        total=total,
        page=skip // limit + 1,
        size=limit
    )


@router.get("/public", response_model=FileList)
def get_public_files(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    files = FileService.get_public_files(db, skip, limit)
    total = db.query(FileModel).filter(FileModel.is_public == True).count()
    
    return FileList(
        files=files,
        total=total,
        page=skip // limit + 1,
        size=limit
    )


@router.get("/{file_id}", response_model=File)
def get_file_info(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    file = FileService.get_file(db, file_id)
    
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Check permissions
    if file.user_id != current_user.id and not file.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this file"
        )
    
    return file


@router.get("/{file_id}/download")
def download_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[UserModel] = None
):
    file = FileService.get_file(db, file_id)
    
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Check if file is public or user owns it
    if not file.is_public:
        if not current_user:
            current_user = Depends(get_current_active_user)
        if file.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this file"
            )
    
    # Get file from storage
    file_data = storage_client.download_file(file.file_path)
    
    if not file_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found in storage"
        )
    
    # Increment download count
    FileService.increment_download_count(db, file)
    
    # Return file
    return StreamingResponse(
        io.BytesIO(file_data),
        media_type=file.content_type,
        headers={
            "Content-Disposition": f"attachment; filename={file.original_filename}"
        }
    )


@router.put("/{file_id}", response_model=File)
def update_file(
    file_id: int,
    file_update: FileUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    file = FileService.get_file(db, file_id)
    
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Check ownership
    if file.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to modify this file"
        )
    
    updated_file = FileService.update_file(db, file, file_update)
    return updated_file


@router.delete("/{file_id}")
def delete_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    file = FileService.get_file(db, file_id)
    
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Check ownership
    if file.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this file"
        )
    
    FileService.delete_file(db, file)
    return {"message": "File deleted successfully"}