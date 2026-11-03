# -*- coding: utf-8 -*-
"""
应用配置管理
"""

from pydantic_settings import BaseSettings
from typing import List
import os
from pathlib import Path


class Settings(BaseSettings):
    """应用配置"""

    # API配置
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_RELOAD: bool = True
    API_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    # 数据库配置
    DATABASE_URL: str = "sqlite:///./jinxiangshibie.db"

    # Redis配置
    REDIS_URL: str = "redis://localhost:6379/0"

    # 模型配置
    SAM_MODEL_PATH: str = "models/sam_vit_h_4b8939.pth"
    SAM_MODEL_TYPE: str = "default"
    DEVICE: str = "cuda"

    # 存储配置
    UPLOAD_DIR: str = "../storage/uploads"
    RESULT_DIR: str = "../storage/results"
    EXPORT_DIR: str = "../storage/exports"

    # 处理配置
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB
    BATCH_SIZE: int = 32
    IMG_SIZE: int = 224

    # JWT配置
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"
        case_sensitive = True


# 创建配置实例
settings = Settings()
