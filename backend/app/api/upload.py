# -*- coding: utf-8 -*-
"""
图像上传API
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import os
import uuid
from pathlib import Path
from typing import List
import logging

from app.core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    """
    上传单个图像文件

    Args:
        file: 上传的图像文件

    Returns:
        上传结果信息
    """

    # 验证文件类型
    allowed_extensions = {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".tif"}
    file_ext = Path(file.filename).suffix.lower()

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型: {file_ext}。支持的类型: {allowed_extensions}"
        )

    # 生成唯一文件名
    file_id = str(uuid.uuid4())
    filename = f"{file_id}{file_ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, filename)

    # 保存文件
    try:
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        logger.info(f"文件上传成功: {filename}")

        return {
            "success": True,
            "file_id": file_id,
            "filename": filename,
            "original_filename": file.filename,
            "file_path": file_path,
            "url": f"/uploads/{filename}"
        }

    except Exception as e:
        logger.error(f"文件上传失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")


@router.post("/upload/multiple")
async def upload_multiple_images(files: List[UploadFile] = File(...)):
    """
    上传多个图像文件

    Args:
        files: 上传的图像文件列表

    Returns:
        上传结果信息列表
    """

    results = []

    for file in files:
        try:
            result = await upload_image(file)
            results.append(result)

        except HTTPException as e:
            results.append({
                "success": False,
                "filename": file.filename,
                "error": e.detail
            })

    successful_count = sum(1 for r in results if r.get("success"))

    logger.info(f"批量上传完成: {successful_count}/{len(files)} 成功")

    return {
        "success": True,
        "total": len(files),
        "successful": successful_count,
        "failed": len(files) - successful_count,
        "results": results
    }


@router.get("/uploads/{filename}")
async def get_uploaded_file(filename: str):
    """
    获取已上传的图像文件

    Args:
        filename: 文件名

    Returns:
        图像文件
    """

    file_path = os.path.join(settings.UPLOAD_DIR, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")

    return FileResponse(
        file_path,
        media_type="image/jpeg",
        headers={"Content-Disposition": f"inline; filename={filename}"}
    )


@router.delete("/uploads/{file_id}")
async def delete_uploaded_file(file_id: str):
    """
    删除已上传的图像文件

    Args:
        file_id: 文件ID

    Returns:
        删除结果
    """

    # 查找文件
    upload_dir = Path(settings.UPLOAD_DIR)
    matching_files = list(upload_dir.glob(f"{file_id}.*"))

    if not matching_files:
        raise HTTPException(status_code=404, detail="文件不存在")

    # 删除文件
    try:
        for file_path in matching_files:
            os.remove(file_path)
            logger.info(f"文件已删除: {file_path}")

        return {
            "success": True,
            "message": "文件删除成功"
        }

    except Exception as e:
        logger.error(f"文件删除失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"文件删除失败: {str(e)}")
