# -*- coding: utf-8 -*-
"""
金相识别Web应用 - FastAPI主入口
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn
import os
from pathlib import Path

from app.api import upload, segment, cluster, export, sem
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时创建必要的目录
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.RESULT_DIR, exist_ok=True)
    os.makedirs(settings.EXPORT_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(settings.SAM_MODEL_PATH), exist_ok=True)

    yield

    # 关闭时的清理工作


# 创建FastAPI应用
app = FastAPI(
    title="金相识别API",
    description="基于SAM分割和ResNet特征提取的金相晶粒识别与分类系统",
    version="1.0.0",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.API_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(upload.router, prefix="/api", tags=["上传"])
app.include_router(segment.router, prefix="/api", tags=["分割"])
app.include_router(cluster.router, prefix="/api", tags=["聚类"])
app.include_router(export.router, prefix="/api", tags=["导出"])
app.include_router(sem.router, prefix="/api", tags=["SEM定量分析"])

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory=settings.RESULT_DIR), name="static")
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "金相识别API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_RELOAD
    )
