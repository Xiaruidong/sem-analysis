# -*- coding: utf-8 -*-
"""
SEM 定量分析独立服务（不依赖 SAM/segment_anything）

启动: venv/Scripts/python.exe run_sem.py   （默认 http://127.0.0.1:8001）
"""

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api import sem
from app.core.config import settings

BASE = Path(__file__).resolve().parent

app = FastAPI(title="SEM 定量分析", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sem.router, prefix="/api", tags=["SEM定量分析"])

# 结果目录（标注图 / json）挂为静态，供前端直接访问
result_dir = Path(settings.RESULT_DIR)
result_dir.mkdir(parents=True, exist_ok=True)
app.mount("/results", StaticFiles(directory=str(result_dir)), name="results")

# 前端页面
app.mount("/", StaticFiles(directory=str(BASE / "sem_frontend"), html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
