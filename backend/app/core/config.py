"""
应用配置管理
"""
import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "银龄精算师"
    DEBUG: bool = True
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./silver_age.db"
    
    # CORS配置 - use JSON format in env: ["http://localhost:5173","http://localhost:3000"]
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # 安全配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    model_config = SettingsConfigDict(
        env_file=".env" if not os.environ.get("TESTING") else None,
        env_file_encoding='utf-8',
        case_sensitive=True
    )

# 延迟实例化，允许测试环境覆盖
def get_settings():
    return Settings()

settings = get_settings()
