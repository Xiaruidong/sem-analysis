# -*- coding: utf-8 -*-
"""
聚类分析API
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging
import uuid
import json
import os
import numpy as np

from app.core.sam_manager import sam_manager
from app.core.feature_extractor import feature_extractor
from app.core.clustering import clustering_manager
from app.core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


class ClusterRequest(BaseModel):
    """聚类请求模型"""

    image_path: str
    sam_params: Optional[Dict[str, Any]] = {
        "points_per_side": 32,
        "pred_iou_thresh": 0.88,
        "stability_score_thresh": 0.95,
        "crop_n_layers": 1,
        "min_mask_region_area": 0.001,
    }
    cluster_params: Optional[Dict[str, Any]] = {
        "k": None,  # None表示自动选择
        "max_k": 6,
        "use_elbow": True,
    }


@router.post("/analyze")
async def analyze_grains(request: ClusterRequest):
    """
    完整的金相分析流程：分割 -> 特征提取 -> 聚类

    Args:
        request: 分析请求

    Returns:
        分析结果
    """

    # 验证图像路径
    if not os.path.exists(request.image_path):
        raise HTTPException(status_code=404, detail="图像文件不存在")

    task_id = str(uuid.uuid4())
    result_dir = os.path.join(settings.RESULT_DIR, task_id)
    os.makedirs(result_dir, exist_ok=True)

    try:
        # 步骤1: SAM分割
        logger.info(f"[{task_id}] 开始分割图像...")
        image_rgb, masks, scores, anns = sam_manager.segment_image(
            image_path=request.image_path,
            **request.sam_params
        )

        if len(masks) == 0:
            raise ValueError("未检测到任何晶粒区域")

        logger.info(f"[{task_id}] 分割完成，检测到 {len(masks)} 个区域")

        # 步骤2: 特征提取
        logger.info(f"[{task_id}] 开始提取特征...")
        feature_matrix, patches = feature_extractor.extract_features(
            image_rgb=image_rgb,
            masks=masks
        )

        if feature_matrix.shape[0] < 2:
            raise ValueError("有效特征不足，无法进行聚类分析")

        logger.info(f"[{task_id}] 特征提取完成，特征矩阵形状: {feature_matrix.shape}")

        # 步骤3: 确定K值
        k = request.cluster_params.get("k")
        max_k = request.cluster_params.get("max_k", 6)
        use_elbow = request.cluster_params.get("use_elbow", True)

        elbow_plot_base64 = None
        sse_list = None

        if k is None and use_elbow:
            logger.info(f"[{task_id}] 计算手肘法确定最优K值...")
            optimal_k, sse_list, elbow_plot_base64 = clustering_manager.find_optimal_k(
                features=feature_matrix,
                max_k=max_k
            )
            # 使用自动选择的K值，或者让用户选择
            k = optimal_k if optimal_k else 3  # 默认值
            logger.info(f"[{task_id}] 自动选择K值: {k}")

        elif k is None:
            k = 3  # 默认值

        # 步骤4: 执行聚类
        logger.info(f"[{task_id}] 执行K-Means聚类，K={k}...")
        clusters, kmeans_model, cluster_stats = clustering_manager.perform_clustering(
            features=feature_matrix,
            k=k
        )

        # 步骤5: t-SNE可视化
        logger.info(f"[{task_id}] 计算t-SNE可视化...")
        tsne_coords, tsne_plot_base64 = clustering_manager.compute_tsne(
            features=feature_matrix,
            clusters=clusters
        )

        # 步骤6: 在原图上可视化聚类结果
        logger.info(f"[{task_id}] 生成聚类可视化图像...")
        clustered_image_base64 = clustering_manager.visualize_clusters_on_image(
            image_rgb=image_rgb,
            masks=masks,
            clusters=clusters,
            k=k
        )

        # 保存结果图像
        import base64
        from PIL import Image
        import io

        clustered_img_data = base64.b64decode(clustered_image_base64)
        clustered_img_path = os.path.join(result_dir, "clustered_result.png")
        with open(clustered_img_path, "wb") as f:
            f.write(clustered_img_data)

        # 构建响应数据
        result = {
            "task_id": task_id,
            "status": "completed",
            "segmentation": {
                "segment_count": len(masks),
                "mean_score": float(np.mean(scores)),
            },
            "clustering": {
                "k": k,
                "stats": cluster_stats,
                "cluster_distribution": cluster_stats["cluster_distribution"],
            },
            "visualizations": {
                "clustered_image": f"/static/{task_id}/clustered_result.png",
                "clustered_image_base64": clustered_image_base64,
                "tsne_plot_base64": tsne_plot_base64,
            },
            "data": {
                "feature_matrix_shape": feature_matrix.shape,
                "clusters": clusters.tolist(),
                "tsne_coords": tsne_coords.tolist(),
            }
        }

        if elbow_plot_base64:
            result["visualizations"]["elbow_plot_base64"] = elbow_plot_base64
            result["data"]["sse_list"] = sse_list

        # 保存完整结果
        result_file = os.path.join(result_dir, "analysis_result.json")
        with open(result_file, "w", encoding="utf-8") as f:
            # 移除base64数据以减小文件大小
            save_result = result.copy()
            save_result["visualizations"] = {
                k: v for k, v in result["visualizations"].items()
                if not k.endswith("_base64")
            }
            json.dump(save_result, f, ensure_ascii=False, indent=2)

        logger.info(f"[{task_id}] 分析完成！")

        return {
            "success": True,
            "result": result
        }

    except Exception as e:
        logger.error(f"[{task_id}] 分析失败: {str(e)}")
        # 保存错误信息
        error_file = os.path.join(result_dir, "error.json")
        with open(error_file, "w", encoding="utf-8") as f:
            json.dump({"error": str(e)}, f, ensure_ascii=False, indent=2)

        raise HTTPException(
            status_code=500,
            detail=f"分析失败: {str(e)}"
        )


@router.get("/analyze/{task_id}")
async def get_analysis_result(task_id: str):
    """
    获取分析结果

    Args:
        task_id: 任务ID

    Returns:
        分析结果数据
    """

    result_file = os.path.join(settings.RESULT_DIR, task_id, "analysis_result.json")

    if not os.path.exists(result_file):
        raise HTTPException(status_code=404, detail="任务不存在或结果已过期")

    try:
        with open(result_file, "r", encoding="utf-8") as f:
            result_data = json.load(f)

        return {
            "success": True,
            "data": result_data
        }

    except Exception as e:
        logger.error(f"读取分析结果失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"读取分析结果失败: {str(e)}")


@router.get("/analyze")
async def list_analysis_results(limit: int = 20, offset: int = 0):
    """
    列出分析结果

    Args:
        limit: 返回数量限制
        offset: 偏移量

    Returns:
        分析结果列表
    """

    try:
        result_dir = settings.RESULT_DIR
        task_dirs = []

        for item in os.listdir(result_dir):
            item_path = os.path.join(result_dir, item)
            if os.path.isdir(item_path):
                result_file = os.path.join(item_path, "analysis_result.json")
                if os.path.exists(result_file):
                    # 读取基本信息
                    with open(result_file, "r", encoding="utf-8") as f:
                        data = json.load(f)

                    task_dirs.append({
                        "task_id": item,
                        "created_at": os.path.getctime(item_path),
                        "status": data.get("status", "unknown"),
                        "segment_count": data["segmentation"]["segment_count"],
                        "k": data["clustering"]["k"],
                    })

        # 按时间倒序排序
        task_dirs.sort(key=lambda x: x["created_at"], reverse=True)

        # 分页
        total = len(task_dirs)
        results = task_dirs[offset:offset + limit]

        return {
            "success": True,
            "total": total,
            "limit": limit,
            "offset": offset,
            "results": results
        }

    except Exception as e:
        logger.error(f"列出分析结果失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"列出分析结果失败: {str(e)}")


@router.delete("/analyze/{task_id}")
async def delete_analysis_result(task_id: str):
    """
    删除分析结果

    Args:
        task_id: 任务ID

    Returns:
        删除结果
    """

    import shutil

    task_dir = os.path.join(settings.RESULT_DIR, task_id)

    if not os.path.exists(task_dir):
        raise HTTPException(status_code=404, detail="任务不存在")

    try:
        shutil.rmtree(task_dir)
        logger.info(f"分析结果已删除: {task_id}")

        return {
            "success": True,
            "message": "分析结果删除成功"
        }

    except Exception as e:
        logger.error(f"删除分析结果失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"删除分析结果失败: {str(e)}")
