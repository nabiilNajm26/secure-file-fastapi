import os
import io
from typing import BinaryIO, Optional
from pathlib import Path
from app.core.config import settings


class LocalStorageClient:
    """Fallback local storage when MinIO is not available"""
    
    def __init__(self):
        self.storage_path = Path("/tmp/uploads")
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    def upload_file(
        self, 
        file_data: BinaryIO, 
        object_name: str, 
        content_type: str,
        file_size: int
    ) -> bool:
        try:
            file_path = self.storage_path / object_name
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, "wb") as f:
                if hasattr(file_data, 'read'):
                    f.write(file_data.read())
                else:
                    f.write(file_data)
            
            print(f"File saved locally: {file_path}")
            return True
        except Exception as e:
            print(f"Error saving file locally: {e}")
            return False
    
    def download_file(self, object_name: str) -> Optional[bytes]:
        try:
            file_path = self.storage_path / object_name
            if file_path.exists():
                with open(file_path, "rb") as f:
                    return f.read()
            return None
        except Exception as e:
            print(f"Error reading local file: {e}")
            return None
    
    def delete_file(self, object_name: str) -> bool:
        try:
            file_path = self.storage_path / object_name
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except Exception as e:
            print(f"Error deleting local file: {e}")
            return False
    
    def get_file_url(self, object_name: str, expires: int = 3600) -> Optional[str]:
        # For local storage, return a basic file path
        # In production, you'd want to serve these through your web server
        return f"/api/v1/files/download/{object_name.split('/')[-1]}"


# Global fallback storage client
local_storage_client = LocalStorageClient()