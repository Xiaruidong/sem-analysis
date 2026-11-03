# -*- coding: utf-8 -*-
"""
SAM模型管理器 - 基于segment-anything的图像分割
"""

import cv2
import numpy as np
import torch
from segment_anything import SamAutomaticMaskGenerator, sam_model_registry
from typing import List, Dict, Tuple, Optional
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class SAMManager:
    """SAM模型管理器 - 单例模式"""

    _instance = None
    _model = None
    _mask_generator = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """初始化SAM模型"""
        if self._model is None:
            self._load_model()

    def _load_model(self):
        """加载SAM模型"""
        try:
            logger.info(f"加载SAM模型: {settings.SAM_MODEL_PATH}")

            # 检查模型文件是否存在
            if not os.path.exists(settings.SAM_MODEL_PATH):
                raise FileNotFoundError(f"SAM模型文件不存在: {settings.SAM_MODEL_PATH}")

            # 注册并加载模型
            sam = sam_model_registry[settings.SAM_MODEL_TYPE](
                checkpoint=settings.SAM_MODEL_PATH
            )

            # 设置设备
            device = torch.device(settings.DEVICE if torch.cuda.is_available() else "cpu")
            sam.to(device)

            self._model = sam
            self._device = device

            logger.info(f"SAM模型加载成功，使用设备: {device}")

        except Exception as e:
            logger.error(f"加载SAM模型失败: {str(e)}")
            raise

    def get_mask_generator(
        self,
        points_per_side: int = 32,
        pred_iou_thresh: float = 0.88,
        stability_score_thresh: float = 0.95,
        crop_n_layers: int = 1,
        min_mask_region_area: float = 0.001,
    ) -> SamAutomaticMaskGenerator:
        """获取或创建掩码生成器"""

        # 创建新的掩码生成器
        mask_generator = SamAutomaticMaskGenerator(
            model=self._model,
            points_per_side=points_per_side,
            pred_iou_thresh=pred_iou_thresh,
            stability_score_thresh=stability_score_thresh,
            crop_n_layers=crop_n_layers,
            min_mask_region_area=min_mask_region_area,
        )

        return mask_generator

    def segment_image(
        self,
        image_path: str,
        points_per_side: int = 32,
        pred_iou_thresh: float = 0.88,
        stability_score_thresh: float = 0.95,
        crop_n_layers: int = 1,
        min_mask_region_area: float = 0.001,
    ) -> Tuple[np.ndarray, List[np.ndarray], List[float], List[Dict]]:
        """
        对图像进行分割

        Args:
            image_path: 图像路径
            points_per_side: 每边的采样点数
            pred_iou_thresh: 预测IoU阈值
            stability_score_thresh: 稳定性分数阈值
            crop_n_layers: 裁剪层数
            min_mask_region_area: 最小掩码区域面积

        Returns:
            (image_rgb, masks, scores, annotations)
            - image_rgb: RGB格式的原图
            - masks: 掩码列表 (每个是布尔数组)
            - scores: 稳定性分数列表
            - annotations: 完整的注释列表
        """

        # 读取图像
        image_bgr = cv2.imread(image_path)
        if image_bgr is None:
            raise ValueError(f"无法读取图像: {image_path}")

        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)

        # 获取掩码生成器
        mask_generator = self.get_mask_generator(
            points_per_side=points_per_side,
            pred_iou_thresh=pred_iou_thresh,
            stability_score_thresh=stability_score_thresh,
            crop_n_layers=crop_n_layers,
            min_mask_region_area=min_mask_region_area,
        )

        # 执行分割
        logger.info("正在执行SAM自动分割...")
        anns = mask_generator.generate(image_rgb)
        logger.info(f"分割完成，检测到 {len(anns)} 个区域")

        # 提取掩码和分数
        masks = [ann['segmentation'].astype(bool) for ann in anns]
        scores = [ann['stability_score'] for ann in anns]

        return image_rgb, masks, scores, anns

    def segment_image_array(
        self,
        image_array: np.ndarray,
        **kwargs
    ) -> Tuple[np.ndarray, List[np.ndarray], List[float], List[Dict]]:
        """
        对图像数组进行分割

        Args:
            image_array: 图像数组 (RGB格式)
            **kwargs: 其他参数同segment_image

        Returns:
            同segment_image
        """

        # 确保是RGB格式
        if len(image_array.shape) == 3 and image_array.shape[2] == 3:
            # 如果是BGR，转换为RGB
            image_rgb = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
        else:
            image_rgb = image_array

        # 获取掩码生成器
        mask_generator = self.get_mask_generator(**kwargs)

        # 执行分割
        logger.info("正在执行SAM自动分割...")
        anns = mask_generator.generate(image_rgb)
        logger.info(f"分割完成，检测到 {len(anns)} 个区域")

        # 提取掩码和分数
        masks = [ann['segmentation'].astype(bool) for ann in anns]
        scores = [ann['stability_score'] for ann in anns]

        return image_rgb, masks, scores, anns


# 导入os模块
import os


# 全局SAM管理器实例
sam_manager = SAMManager()
