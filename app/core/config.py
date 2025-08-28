from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # Database
    database_url: str = Field(..., env="DATABASE_URL")
    
    # Redis
    redis_url: str = Field(..., env="REDIS_URL")
    
    # JWT
    jwt_secret_key: str = Field(..., env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_access_token_expire_minutes: int = Field(default=30, env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
    jwt_refresh_token_expire_days: int = Field(default=7, env="JWT_REFRESH_TOKEN_EXPIRE_DAYS")
    
    # MinIO S3
    minio_endpoint: str = Field(..., env="MINIO_ENDPOINT")
    minio_access_key: str = Field(..., env="MINIO_ACCESS_KEY")
    minio_secret_key: str = Field(..., env="MINIO_SECRET_KEY")
    minio_secure: bool = Field(default=False, env="MINIO_SECURE")
    minio_bucket_name: str = Field(default="uploads", env="MINIO_BUCKET_NAME")
    
    # Email
    mail_username: Optional[str] = Field(None, env="MAIL_USERNAME")
    mail_password: Optional[str] = Field(None, env="MAIL_PASSWORD")
    mail_from: str = Field(default="noreply@example.com", env="MAIL_FROM")
    mail_port: int = Field(default=587, env="MAIL_PORT")
    mail_server: str = Field(default="smtp.gmail.com", env="MAIL_SERVER")
    mail_from_name: str = Field(default="Auth File API", env="MAIL_FROM_NAME")
    
    # File Upload
    max_file_size: int = Field(default=10485760, env="MAX_FILE_SIZE")  # 10MB
    allowed_extensions: str = Field(default="jpg,jpeg,png,gif,pdf,txt,doc,docx", env="ALLOWED_EXTENSIONS")
    upload_dir: str = Field(default="uploads", env="UPLOAD_DIR")
    
    # App
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    
    @property
    def allowed_extensions_list(self) -> list[str]:
        return [ext.strip().lower() for ext in self.allowed_extensions.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()