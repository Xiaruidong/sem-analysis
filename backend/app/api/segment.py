# -*- coding: utf-8 -*-
"""
SAM分割API
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging
import uuid
import json
import os

from app.core.sam_manager import sam_manager
from app.core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


class SegmentRequest(BaseModel):
    """分割请求模型"""

    image_path: str
    sam_params: Optional[Dict[str, Any]] = {
        "points_per_side": 32,
        "pred_iou_thresh": 0.88,
        "stability_score_thresh": 0.95,
        "crop_n_layers": 1,
        "min_mask_region_area": 0.001,
    }


class SegmentResponse(BaseModel):
    """分割响应模型"""

    success: bool
    task_id: str
    segment_count: int
    message: str


@router.post("/segment", response_model=SegmentResponse)
async def segment_image(request: SegmentRequest):
    """
    执行SAM图像分割

    Args:
        request: 分割请求

    Returns:
        分割结果
    """

    # 验证图像路径
    if not os.path.exists(request.image_path):
        raise HTTPException(status_code=404, detail="图像文件不存在")

    try:
        # 执行分割
        logger.info(f"开始分割图像: {request.image_path}")

        image_rgb, masks, scores, anns = sam_manager.segment_image(
            image_path=request.image_path,
            **request.sam_params
        )

        # 保存结果
        task_id = str(uuid.uuid4())
        result_dir = os.path.join(settings.RESULT_DIR, task_id)
        os.makedirs(result_dir, exist_ok=True)

        # 保存分割数据
        segment_data = {
            "task_id": task_id,
            "image_path": request.image_path,
            "segment_count": len(masks),
            "sam_params": request.sam_params,
            "masks": [mask.tolist() for mask in masks],
            "scores": scores,
        }

        result_file = os.path.join(result_dir, "segment_data.json")
        with open(result_file, "w", encoding="utf-8") as f:
            json.dump(segment_data, f, ensure_ascii=False, indent=2)

        logger.info(f"分割完成，检测到 {len(masks)} 个区域，任务ID: {task_id}")

        return SegmentResponse(
            success=True,
            task_id=task_id,
            segment_count=len(masks),
            message="分割完成"
        )

    except Exception as e:
        logger.error(f"分割失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"分割失败: {str(e)}")


@router.get("/segment/{task_id}")
async def get_segment_result(task_id: str):
    """
    获取分割结果

    Args:
        task_id: 任务ID

    Returns:
        分割结果数据
    """

    result_file = os.path.join(settings.RESULT_DIR, task_id, "segment_data.json")

    if not os.path.exists(result_file):
        raise HTTPException(status_code=404, detail="任务不存在或结果已过期")

    try:
        with open(result_file, "r", encoding="utf-8") as f:
            segment_data = json.load(f)

        return {
            "success": True,
            "data": segment_data
        }

    except Exception as e:
        logger.error(f"读取分割结果失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"读取分割结果失败: {str(e)}")


@router.post("/segment/visualize")
async def visualize_segmentation(task_id: str):
    """
    生成分割结果可视化图像

    Args:
        task_id: 任务ID

    Returns:
        可视化结果信息
    """

    result_file = os.path.join(settings.RESULT_DIR, task_id, "segment_data.json")

    if not os.path.exists(result_file):
        raise HTTPException(status_code=404, detail="任务不存在")

    try:
        # 读取分割数据
        with open(result_file, "r", encoding="utf-8") as f:
            segment_data = json.load(f)

        # 读取原图
        import cv2
        image_bgr = cv2.imread(segment_data["image_path"])
        if image_bgr is None:
            raise ValueError("无法读取原图")

        # 创建可视化
        import numpy as np
        import matplotlib.pyplot as plt
        from PIL import Image
        import io
        import base64

        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)

        # 生成随机颜色的掩码叠加
        h, w = image_rgb.shape[:2]
        overlay = np.ones((h, w, 4))
        overlay[:, :, 3] = 0

        masks = [np.array(mask, dtype=bool) for mask in segment_data["masks"]]

        for mask in masks:
            color_mask = np.concatenate([np.random.random(3), [0.45]])
            overlay[mask] = color_mask

        # 绘制
        plt.figure(figsize=(15, 15))
        plt.imshow(image_rgb)
        plt.imshow(overlay)
        plt.axis('off')
        plt.title(f"SAM分割结果 - {segment_data['segment_count']}个区域")

        # 保存图像
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)

        # 保存到文件
        viz_filename = f"segment_viz_{task_id}.png"
        viz_path = os.path.join(settings.RESULT_DIR, task_id, viz_filename)

        pil_img = Image.open(buf)
        pil_img.save(viz_path)

        # 转换为base64
        img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        plt.close()

        return {
            "success": True,
            "image_base64": img_base64,
            "image_url": f"/static/{task_id}/{viz_filename}"
        }

    except Exception as e:
        logger.error(f"生成可视化失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"生成可视化失败: {str(e)}")
